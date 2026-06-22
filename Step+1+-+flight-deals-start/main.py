import datetime as dt
import os
import pandas as pd
from dotenv import load_dotenv
from data_manager import DataManager
from flight_search import FlightSearch
from flight_data import FlightData
from notification_manager import NotificationManager
import requests_cache

# Initialize response caching for API calls
requests_cache.install_cache()

# Configuration constants
ORIGIN_IATA = "TLV"
CSV_FILE = "cities_and_prices.csv"

load_dotenv()
PRICES_SHEET_AUTHENTICATION = os.getenv('PRICES_SHEET_AUTHENTICATION')
PRICES_SHEET_URL = "https://api.sheety.co/d8bd143a76eb3082f849f878fb729513/myFlightDeals/prices"

my_destinations_manager = DataManager(url=PRICES_SHEET_URL, auth=PRICES_SHEET_AUTHENTICATION, root="price")
notification_manager = NotificationManager()

# Load existing data or prompt user for destinations
try:
    cities_and_prices = pd.read_csv(CSV_FILE)
except (FileNotFoundError, pd.errors.EmptyDataError):
    user_input = input("enter the names of the cities and max price comma-separated (e.g., paris 40, new york 120): ")
    input_processing = [city.strip().title().rsplit(' ', 1) for city in user_input.split(",")]

    cities_and_prices = pd.DataFrame(input_processing, columns=["city", "lowestPrice"])
    cities_and_prices["lowestPrice"] = pd.to_numeric(cities_and_prices["lowestPrice"])
    cities_and_prices.to_csv(CSV_FILE, index=False, encoding="utf-8")

# Add cities to the sheet via API
for index, row in cities_and_prices.iterrows():
    my_destinations_manager.add_city(city=row["city"], start_price=row["lowestPrice"])

# Fetch updated destination data from Sheety
dest_data = my_destinations_manager.get_data()
prices_list = dest_data.get("prices", [])

tomorrow = dt.datetime.now() + dt.timedelta(days=1)
six_months_from_now = dt.datetime.now() + dt.timedelta(days=6 * 30)

# Search for flight deals for each destination
for airport in prices_list:
    airport_IATA = airport.get("iataCode")
    airport_city = airport.get("city", "Unknown")

    # Skip invalid IATA codes or error values
    if not airport_IATA or "#N/A" in airport_IATA:
        continue

    print(f"\nSearching flights to {airport_city} ({airport_IATA})...")
    
    flight_search = FlightSearch(origin_IATA=ORIGIN_IATA, dest_IATA=airport_IATA, from_time=tomorrow,
                                 to_time=six_months_from_now)
    search_json = flight_search.get_json_data()
    all_flights = search_json.get("best_flights", []) + search_json.get("other_flights", [])

    print(f"Found {len(all_flights)} flights")

    cheapest_flight = None
    for flight in all_flights:
        if not cheapest_flight or int(flight["price"]) < int(cheapest_flight["price"]):
            cheapest_flight = flight

    # Only proceed if at least one flight was found
    if cheapest_flight is not None:
        current_sheet_price = int(airport["lowestPrice"])
        flight_price = int(cheapest_flight["price"])
        
        print(f"Cheapest flight: ${flight_price} | Sheet price: ${current_sheet_price}")

        # If a cheaper flight is found, update the sheet and send alert
        if flight_price < current_sheet_price:
            print(f"✓ Deal found! Sending notification...")
            sheet_row_id = airport.get("id")
            my_destinations_manager.update_lowest_price(id=sheet_row_id, price=flight_price)

            flight_to_notify = FlightData(
                price=flight_price,
                origin_airport=cheapest_flight["flights"][0]["departure_airport"]["id"],
                destination_airport=cheapest_flight["flights"][-1]["arrival_airport"]["id"],
                out_date=cheapest_flight["flights"][0]["departure_airport"]["time"].split(" ")[0],
                return_date=six_months_from_now.strftime("%Y-%m-%d")
            )

            notification_manager.send_notification(flight_to_notify)
        else:
            print(f"✗ No deal (flight price >= sheet price)")
    else:
        print(f"✗ No flights found")