from fastapi import FastAPI
from routers import weather #, crops

app = FastAPI(title="Agro Intelligence API")

# Подключаем роутеры
app.include_router(weather.router, prefix="/weather", tags=["Weather"])
# app.include_router(crops.router, prefix="/crops", tags=["Crops"])

@app.get("/")
def root():
    return {"message": "Agro Intelligence API is running. Go to /docs 🚀"}
