from flight_data import FlightData
from twilio.rest import Client
import os
from dotenv import load_dotenv


class NotificationManager:
    # Sends flight deal alerts via WhatsApp using Twilio

    def __init__(self):
        # Initialize Twilio client with credentials from environment variables
        load_dotenv()
        self.client = Client(
            os.getenv('TWILIO_SID'),
            os.getenv('TWILIO_AUTH_TOKEN')
        )

    def send_notification(self, flight: FlightData):
        # Send WhatsApp notification with flight deal details
        body = f"Low price alert! Only ${flight.price} to fly from {flight.origin_airport} to {flight.destination_airport}, from {flight.out_date} to {flight.return_date}."
        message = self.client.messages.create(
            from_=os.getenv('TWILIO_WHATSAPP_NUMBER'),
            body=body,
            to= os.getenv('MY_WHATSAPP_NUMBER')

        )
        print(message.status)
