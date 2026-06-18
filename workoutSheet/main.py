import datetime as dt
import json
import os

import requests

NT_APP_ID = os.environ["NT_APP_ID"]
NT_API_KEY = os.environ["NT_API_KEY"]
SHEETY_TOKEN = os.environ["SHEETY_TOKEN"]
MY_WEIGHT = int(os.environ["MY_WEIGHT"])
MY_HEIGHT = int(os.environ["MY_HEIGHT"])
MY_AGE = int(os.environ["MY_AGE"])
GENDER = os.environ["GENDER"]

exercise_input = os.environ.get("WORKOUT_INPUT") or input("write your exercise today: ")

nutrition_headers = {
    "x-app-id": NT_APP_ID,
    "x-app-key": NT_API_KEY,
    "Content-Type": "application/json",
}

parameters = {
    "query": exercise_input,
    "weight_kg": MY_WEIGHT,
    "height_cm": MY_HEIGHT,
    "age": MY_AGE,
    "gender": GENDER,
}

nut_url = "https://app.100daysofpython.dev/v1/nutrition/natural/exercise"
response = requests.post(url=nut_url, json=parameters, headers=nutrition_headers)
print(response.status_code)
print(response.text)
response.raise_for_status()

data = response.json()
print(json.dumps(data, indent="\t"))

if not data.get("exercises"):
    print("No exercises were returned by the API.")
    raise SystemExit(1)

exercise_name = data["exercises"][0]["name"]
exercise_duration = data["exercises"][0]["duration_min"]
exercise_calories = data["exercises"][0]["nf_calories"]

now = dt.datetime.now()
push_json = {
    "workout": {
        "date": now.strftime("%d/%m/%Y"),
        "time": now.strftime("%H:%M:%S"),
        "exercise": exercise_name,
        "duration": exercise_duration,
        "calories": exercise_calories,
    }
}

sheety_headers = {"Authorization": f"Bearer {SHEETY_TOKEN}"}
push_url = "https://api.sheety.co/d8bd143a76eb3082f849f878fb729513/workoutTracking/workouts"
push_response = requests.post(url=push_url, json=push_json, headers=sheety_headers)
print(push_response.status_code)
print(push_response.text)
push_response.raise_for_status()
