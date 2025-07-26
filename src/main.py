from fastapi import FastAPI
from src.routes.market_prices import router as market_prices_route
from src.routes.agents import router as agents_route
from src.routes.weather_forecast import router as weather_forecast_route


app = FastAPI()

app.include_router(market_prices_route, prefix="/api")
app.include_router(agents_route, prefix="/api")
app.include_router(weather_forecast_route, prefix="/api")


@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI application!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info", reload=True)