from fastapi import Request, APIRouter, Query
from pydantic import BaseModel, Field
from typing import List
from src.handler.weather_forecast_agent import get_forecast_min_max, get_current_weather

router = APIRouter(
    prefix="/weather-forecast",
    tags=["Weather Forecast"],
    responses={500: {"description": "Something went wrong"}}
)

@router.get("/")
def get_weather_forecast(request: Request,
                            city: str = Query(),
                           days: int = Query(7)):
    if not city:
        return {"message": "City parameter is required"}
    if not days or days < 1:
        return {"message": "Days parameter must be a positive integer"}
    response = get_forecast_min_max(city, days)
    return response

@router.get("/weather")
def get_weather(request: Request,
                            city: str = Query()):
    if not city:
        return {"message": "City parameter is required"}
    response = get_current_weather(city)
    return response