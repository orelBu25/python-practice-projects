import requests
import requests_cache


class DataManager:
    # Manages communication with the Google Sheet API via Sheety

    def __init__(self, url, auth, root):
        self.cities_counter = 0
        self.url = url
        self.auth = auth
        self.headers = {"Authorization" : f"Bearer {self.auth}"}
        self.root = root

    def add_city(self, city, start_price):
        # Add a new destination city with initial price alert threshold
        self.cities_counter += 1
        parameters = { self.root:{
            "city" : city,
            "lowestPrice" : start_price,
            }
        }
        response = requests.put(url=f"{self.url}/{self.cities_counter + 1}", json=parameters, headers=self.headers)
        response.raise_for_status()
    def get_data(self):
        # Fetch all destinations and their current lowest prices from the sheet
        response = requests.get(url=self.url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def update_lowest_price(self, id, price):
        # Update the lowest price for a destination if a better deal is found
        parameters = { self.root:{
                "lowestPrice" : price,
                }
            }
        response = requests.put(url=f"{self.url}/{id}", json=parameters, headers=self.headers)
        response.raise_for_status()