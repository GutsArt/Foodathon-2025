from fastapi import APIRouter
from services.weather_service import get_weather

router = APIRouter()

@router.get("/")
def current_weather(city: str):
    """Получить текущую погоду для города"""
    return get_weather(city)
