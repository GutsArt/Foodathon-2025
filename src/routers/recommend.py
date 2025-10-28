import logging
from fastapi import APIRouter, Query
from services.ecocrop_service import ecocrop_service
from services.weather_service import get_weather
from datetime import datetime

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
        # === OpenWeather Data ===
        "weather": {
            # "coord": weather.get("coord"), # lon, lat
            # id: int, main: Clouds, description: few clouds, icon: 02n
            "weather": weather.get("weather"), 
            # temp, feels_like, temp_min, temp_max, pressure, humidity, sea_level, grand_level
            "main": weather.get("main"), 
            # speed, deg, +- gust
            "wind": weather.get("wind"),
            
            "clouds": weather.get("clouds"), # %
            "rain": weather.get("rain"), # +-
            "snow": weather.get("snow"), # +-

            "sys": {
                "country": weather.get("sys", {}).get("country"), # DE
                "sunrise": datetime.utcfromtimestamp(weather.get("sys", {}).get("sunrise")).strftime('%Y-%m-%d %H:%M'),
                "sunset": datetime.utcfromtimestamp(weather.get("sys", {}).get("sunset")).strftime('%Y-%m-%d %H:%M'),
            },
            # "timezone": weather.get("timezone") # seconds shift from UTC     
        },

        "crop_info": crop_data

        # "crop_info": {
        #     "ScientificName": crop_data.get("ScientificName"),
        #     # Морфология и жизненный цикл
        #     "LIFO": crop_data.get("LIFO"), # форма растения 
        #     "HABIT": crop_data.get("HABIT"), # тип растения
        #     # +++
        #     "LISPA": crop_data.get("LISPA"), # срок жизни annual/biennial/perennial
        #     "PHYS": crop_data.get("PHYS"),   # физические свойства

        #     # 🧑‍🌾 Использование и выращивание
        #     "CAT": crop_data.get("CAT"),       # Категория культуры
        #     "PLAT": crop_data.get("PLAT"),     # Маштаб выращивания
        #     "PROSY": crop_data.get("PROSY"), # Сферы применения
        #     "GMIN": crop_data.get("GMIN"),   # Продолжительность вегетационного периода мин
        #     "GMAX": crop_data.get("GMAX"),   # Продолжительность вегетационного периода макс

        #     # 📸 Фотопериод
        #     "PHOTO": crop_data.get("PHOTO"),     # фотопериодические требования растения

        #     # 🌡️ Температура и 🌧️ Осадки 
        #     "TOPMN": crop_data.get("TOPMN"), # оптимальная температура мин
        #     "TOPMX": crop_data.get("TOPMX"), # оптимальная температура макс
        #     "ROPMN": crop_data.get("ROPMN"), # оптимальные осадки мин
        #     "ROPMX": crop_data.get("ROPMX"), # оптимальные осадки макс
        #     "TMIN": tmin,  # минимальная температура
        #     "TMAX": tmax,   # максимальная температура
        #     "RMIN": rmin,   # минимальные осадки
        #     "RMAX": rmax,   # максимальные осадки
            
        #     "PHMIN": crop_data.get("PHMIN"),   # Минимальное значение pH почвы
        #     "PHMAX": crop_data.get("PHMAX"),   # Максимальное значение pH почвы
        #     "PHOPMN": crop_data.get("PHOPMN"), # Оптимальное значение pH почвы мин
        #     "PHOPMX": crop_data.get("PHOPMX"), # Оптимальное значение pH почвы макс

        #     # 🌍 География
        #     "LATOPMN": crop_data.get("LATOPMN"), # Оптимальная широта мин
        #     "LATOPMX": crop_data.get("LATOPMX"), # Оптимальная широта макс
        #     "LATMN": crop_data.get("LATMN"),     # Абсолютный диапазон широты мин
        #     "LATMX": crop_data.get("LATMX"),     # Абсолютный диапазон широты макс
        #     "ALTMX": crop_data.get("ALTMX"),     # Максимальная высота над уровнем моря (м)
                
        #     # ☀️ Свет
        #     "LIOPMN": crop_data.get("LIOPMN"),  # Оптимальный минимум освещённости
        #     "LIOPMX": crop_data.get("LIOPMX"),  # Оптимальный максимум освещённости
        #     "LIMN": crop_data.get("LIMN"),      # Допустимый минимум освещённости
        #     "LIMX": crop_data.get("LIMX"),      # Допустимый максимум освещённости

        #     # 🧱 Почва
        #     "DEP": crop_data.get("DEP"),        # Оптимальная глубина почвы
        #     "DEPR": crop_data.get("DEPR"),      # Допустимая глубина почвы
        #     "TEXT": crop_data.get("TEXT"),      # Оптимальная текстура почвы
        #     "TEXTR": crop_data.get("TEXTR"),    # Допустимая текстура почвы
        #     "FER": crop_data.get("FER"),        # Требуемое плодородие
        #     "FERR": crop_data.get("FERR"),      # Допустимое плодородие
        #     "SAL": crop_data.get("SAL"),        # Устойчивость к солёности
        #     "SALR": crop_data.get("SALR"),      # Допустимая солёность
        #     "DRA": crop_data.get("DRA"),        # Требования к дренажу
        #     "DRAR": crop_data.get("DRAR"),      # Допустимый дренаж / засуха

        #     # ☠️ Токсичность
        #     "TOX": crop_data.get("TOX"),        # Устойчивость к токсичным условиям
        #     "TOXR": crop_data.get("TOXR"),      # Допустимая токсичность

        #     # 📸 Фотопериод
        #     "PHOTO": crop_data.get("PHOTO"),    # Требуемая длина дня

        #     # 🌦️ Климат
        #     "CLIZ": crop_data.get("CLIZ"),      # Климатические зоны по Кёппену

        #     # 🧬 Адаптация
        #     "ABITOL": crop_data.get("ABITOL"),  # Толерантность к абиотическим стрессам
        #     "ABISUS": crop_data.get("ABISUS"),  # Основной абиотический фактор
        #     "INTRI": crop_data.get("INTRI"),    # История интродукции
        # }
    }
