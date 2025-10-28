from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routers import weather, crops, recommend

app = FastAPI(
    title="Agro Intelligence API",
    description="API для проверки пригодности условий выращивания по данным FAO EcoCrop",
    version="1.0.0"
)

# Подключаем роутеры
app.include_router(weather.router, prefix="/weather", tags=["Weather"])
app.include_router(crops.router, prefix="/crops", tags=["Crops"])
app.include_router(recommend.router, prefix="/recommend", tags=["Recommend"])

# Подключаем папку с веб-страницами
app.mount("/web", StaticFiles(directory="web"), name="web")

@app.get("/")
def root():
    return {"message": "Agro Intelligence API is running. Go to /docs 🚀"}

# Эндпоинт для отображения веб-интерфейса Recommend
@app.get("/recommend-ui", include_in_schema=False)
def recommend_ui():
    """
    Отображает веб-интерфейс для проверки пригодности условий выращивания.
    """
    return FileResponse("web/recommend.html")