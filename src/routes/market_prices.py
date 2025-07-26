from fastapi import Request, APIRouter, Query
from pydantic import BaseModel, Field
from typing import List
from src.handler.market_prices import (fetch_current_daily_market_prices,
                                       get_market_trend,
                                       market_trend_qna,
                                       import_market_prices_data)

router = APIRouter(
    prefix="/market-prices",
    tags=["Market Prices"],
    responses={500: {"description": "Something went wrong"}}
)

class MarketPriceTrendQnA(BaseModel):
    query: str = Field("", description="Question to ask about market prices")

class MarketPricesModel(BaseModel):
    state: str = Field(..., description="State where the market is located")
    district: str = Field(..., description="District where the market is located")
    market: str = Field(..., description="Market name")
    commodity: str = Field(..., description="Commodity name")
    variety: str = Field(..., description="Variety of the commodity")
    arrival_date: str = Field(..., description="Date of arrival in DD-MM-YYYY format")
    min_price: float = Field(..., description="Minimum price of the commodity")
    max_price: float = Field(..., description="Maximum price of the commodity")
    modal_price: float = Field(..., description="Modal price of the commodity")
    grade: str = Field(..., description="Grade of the commodity")

class ImportMarketPricesData(BaseModel):
    data: List[MarketPricesModel] = Field(..., description="List of market prices data to be imported")

@router.get("/daily")
def get_daily_market_prices(request: Request,
                            state: str = Query(),
                           district: str = Query(None),
                           market: str = Query(None),
                           commodity: str = Query(None),
                           variety: str = Query(None)):
    response = fetch_current_daily_market_prices(request, state, district, market, commodity, variety)
    return response

@router.get("/trend")
def get_market_prices_trend(request: Request,
                            state: str = Query(),
                           district: str = Query(),
                           market: str = Query(),
                           commodity: str = Query(),
                           variety: str = Query(None),
                           type_of_trend: str = Query("weekly")):
    response = get_market_trend(request, state, district, market, commodity, variety, type_of_trend)
    return response

@router.post("/trend/qna")
def get_market_prices_trend(request: Request,
                            payload: MarketPriceTrendQnA,
                            state: str = Query(),
                           district: str = Query(),
                           market: str = Query(),
                           commodity: str = Query(),
                           variety: str = Query(None),
                           type_of_trend: str = Query("weekly")):
    payload = payload.model_dump()
    query = payload.get("query")
    if not query:
        return {"message": "Please provide a question to get an answer."}

    response = market_trend_qna(state, commodity, query, district, market, variety, type_of_trend)
    return response

@router.post("/import-data")
def import_market_data(request: Request, payload: ImportMarketPricesData):
    payload = payload.model_dump()
    data = payload.get("data")

    response = import_market_prices_data(data)
    return response