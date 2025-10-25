import requests
import os
from config import API_KEY


def get_weather(city: str):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()
    return {
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"]
    }
