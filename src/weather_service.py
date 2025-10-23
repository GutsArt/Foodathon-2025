import requests
import os
# from dotenv import load_dotenv

# load_dotenv()
# API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
API_KEY = "12406b51536b2e8b97a7264508483b5d"
def get_weather(city: str):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()
    return {
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"]
    }
