import logging
from fastapi import APIRouter, Query
from services.ecocrop_service import ecocrop_service
from services.weather_service import get_weather

# === ЛОГИРОВАНИЕ С ЦВЕТАМИ В КОНСОЛИ ===
class ColorFormatter(logging.Formatter):
    GREEN = "\033[92m"
    RED = "\033[31m"
    RESET = "\033[0m"

    def format(self, record):
        # Если уровень выше INFO — красный цвет
        if record.levelno > logging.INFO:
            color = self.RED
        else:
            color = self.GREEN

        log_format = f"{color}%(asctime)s [%(levelname)s]{self.RESET} %(message)s"
        formatter = logging.Formatter(log_format, "%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


# Настройка логирования
handler = logging.StreamHandler()
handler.setFormatter(ColorFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])


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
    if not weather or ("error" in weather):
        return weather if isinstance(weather, dict) else {"error": f"Unable to retrieve weather data for city '{city}'."}

    crop_data = ecocrop_service.get_crop(crop)
    if not crop_data:
        return {"error": f"Crop '{crop}' not found in EcoCrop database."}

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
    suitable = False
    results = []
    if tmin and tmax:
        if temp < tmin:
            results.append(f"Too cold (current {temp}°C, needs ≥ {tmin}°C)")
        elif temp > tmax:
            results.append(f"Too hot (current {temp}°C, needs ≤ {tmax}°C)")
        else:
            results.append(f"Temperature is suitable ({temp}°C ∈ [{tmin}, {tmax}]°C)")
            suitable = True
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
