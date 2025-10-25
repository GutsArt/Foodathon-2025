from fastapi import APIRouter, Query
from services.ecocrop_service import get_crop

router = APIRouter()

@router.get("/")
def check_crop(
    name: str = Query(..., description="Название культуры (например, tomato)"),
    # city: str = Query(..., description="Город для определения погодных условий")
):
    """
    Проверяет, подходят ли текущие погодные условия для выращивания выбранной культуры.
    Использует OpenWeatherMap и базу FAO EcoCrop.
    """
    result = get_crop(name=name)
    if not result:
        return {"error": f"Культура '{name}' не найдена"}
    return result
