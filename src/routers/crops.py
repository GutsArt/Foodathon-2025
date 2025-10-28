from fastapi import APIRouter, Query
from services.ecocrop_service import get_crop

router = APIRouter()

@router.get("/")
def check_crop(name: str = Query(..., description="Название культуры (carrot, okra, onion, Wheat, Maize , Papaya, Pineapple, Sugarcane,  Coffee, )")): # tomato, cabbage,
    result = get_crop(name=name)
    if not result:
        return {"error": f"Культура '{name}' не найдена"}
    return result
