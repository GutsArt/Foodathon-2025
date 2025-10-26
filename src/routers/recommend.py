import logging
from fastapi import APIRouter, Query
from services.ecocrop_service import ecocrop_service
from services.weather_service import get_weather

logging.basicConfig(
    level=logging.INFO,
    format="\033[92m%(asctime)s [%(levelname)s]\033[0m %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

router = APIRouter()

@router.get("/check")
def check_crop_suitability(
    city: str = Query(..., description="Название города, например: Paris"),
    crop: str = Query(..., description="Научное или обычное название культуры"),
):
    """
    Проверяет, подходят ли текущие погодные условия в городе для выращивания выбранной культуры.
    """
    weather = get_weather(city)
    if not weather:
        return {"error": f"Не удалось получить данные погоды для города '{city}'."}
    crop_data = ecocrop_service.get_crop(crop)
    if not crop_data:
        return {"error": f"Культура '{crop}' не найдена в базе EcoCrop."}

    # --- Извлечение нужных параметров погоды ---
    main_data = weather.get("main", {})
    rain_data = weather.get("rain", {})

    temp = main_data.get("temp")            # °C
    humidity = main_data.get("humidity")    # %
    # иногда ключ может быть "1h" или "3h" — берём любой доступный
    rain = rain_data.get("1h") or 0.0 

    logging.info("=== WEATHER DATA ===")
    logging.info(f"Город: {city}")
    logging.info(f"Погода: {weather}")
    logging.info(f"Температура: {temp}°C, Осадки: {rain} мм, Влажность: {humidity}%")


    # From EcoCrop
    tmin = crop_data.get("TMIN")
    tmax = crop_data.get("TMAX")
    # Rain за год
    rmin = crop_data.get("RMIN") 
    rmax = crop_data.get("RMAX")

    logging.info("=== CROP DATA ===")
    logging.info(f"Культура: {crop}")
    logging.info(f"TMIN: {tmin}°C, TMAX: {tmax}°C")
    logging.info(f"RMIN: {rmin} мм/год, RMAX: {rmax} мм/год")

    # Проверяем соответствие
    results = []
    if tmin and tmax:
        if temp < tmin:
            results.append(f"Слишком холодно (текущая {temp}°C, нужно ≥ {tmin}°C)")
        elif temp > tmax:
            results.append(f"Слишком жарко (текущая {temp}°C, нужно ≤ {tmax}°C)")
        else:
            results.append(f"Температура подходит ({temp}°C ∈ [{tmin}, {tmax}]°C)")

    """# Проверяем осадки за год NASA POWER
    if rmin and rmax:
        if rain < rmin:
            results.append(f"Недостаточно осадков ({rain} мм, нужно ≥ {rmin} мм)")
        elif rain > rmax:
            results.append(f"Слишком много осадков ({rain} мм, нужно ≤ {rmax} мм)")
        else:
            results.append(f"Осадки в норме ({rain} мм ∈ [{rmin}, {rmax}] мм)")
    """
    
    # Общий вывод
    suitable = not any("Слишком" in r or "Недостаточно" in r for r in results)

    return {
        "city": city, # weather.get("name")
        "crop": crop,
        "suitable": suitable,
        "details": results,
        "weather": {
            # "coord": weather.get("coord"),
            "weather": weather.get("weather"),
            "main": weather.get("main"),
            "wind": weather.get("wind"),
            "clouds": weather.get("clouds"),
            "rain": weather.get("rain"), # +-
            "snow": weather.get("snow"), # +-

            "sys": weather.get("sys"),
            # "name": weather.get("name"),
        },
        "requirements": {
            "TMIN": tmin,
            "TMAX": tmax,
            "RMIN": rmin,
            "RMAX": rmax,
        },
    }
