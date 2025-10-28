import requests
import logging
from config import OPENWEATHER_API_KEY

# class WeatherService:
#     @staticmethod
def get_weather(city: str) -> dict:
    """Возвращает погоду для указанного города."""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.HTTPError:
        return {"error": f"You entered an invalid city: '{city}'."}
    except requests.exceptions.RequestException as e:
        logging.error(f"Error requesting OpenWeather: {e}")
        return {"error": "Failed to retrieve weather data. Please try again later."}