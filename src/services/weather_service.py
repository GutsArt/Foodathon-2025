import requests
from config import OPENWEATHER_API_KEY

# class WeatherService:
#     @staticmethod
def get_weather(city: str):
    """Возвращает погоду для указанного города."""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
