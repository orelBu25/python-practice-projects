import datetime as dt
import requests
import os
from dotenv import load_dotenv

load_dotenv()
SERPAPI_KEY = os.getenv('SERP_API_KEY')
SERP_API_URL = "https://serpapi.com/search?engine=google_flights"


class FlightSearch:
    # Queries Google Flights API for available flights between origin and destination

    def __init__(self,origin_IATA, dest_IATA, from_time: dt.datetime, to_time: dt.datetime):
        self.origin = origin_IATA
        self.dest = dest_IATA
        self.from_time = from_time
        self.to_time = to_time

    def get_json_data(self):
        # Retrieve flight options for the specified dates and route
        req_parameters = {
            "engine" : "google_flights",
            "api_key" : SERPAPI_KEY,
            "arrival_id": self.dest,
            "departure_id": self.origin,
            "outbound_date": self.from_time.strftime("%Y-%m-%d"),
            "return_date": self.to_time.strftime("%Y-%m-%d"),
            "type": "1",
            "adults": "1",

        }
        response = requests.get(url=SERP_API_URL, params=req_parameters)
        response.raise_for_status()
        return response.json()
