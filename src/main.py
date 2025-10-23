from ecocrop_service import EcoCropService
from weather_service import get_weather
from analyzer import compute_suitability
import os


BASE_DIR = os.path.dirname(__file__)
ECOCROP_PATH = os.path.join(BASE_DIR, "data", "EcoCrop_DB.csv")


print(os.path.exists(ECOCROP_PATH))  # True


ecocrop = EcoCropService(ECOCROP_PATH)
weather = get_weather("Kyiv")

crop_name = "Abelmoschus esculentus"  

params = ecocrop.get_growth_params(crop_name)
suitability = compute_suitability(weather, params)

print(f"Crop: {crop_name}")
print(f"Weather: {weather}")
print(f"Growth params: {params}")
print(f"Suitability index: {suitability}")
