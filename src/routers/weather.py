from fastapi import APIRouter, Query
from services.weather_service import get_weather

router = APIRouter()

@router.get("/")
def current_weather(city: str = Query(..., description="Название города, например: Paris")):
    """Получить текущую погоду для города"""
    return get_weather(city)
