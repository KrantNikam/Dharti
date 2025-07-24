from fastapi import Request, APIRouter, Query
from pydantic import BaseModel, Field
from typing import List
from handler.weather_forecast_agent import get_forecast

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
    response = get_forecast(city, days)
    return response
