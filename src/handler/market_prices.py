import requests
from datetime import datetime
import io
import base64
from vertexai.generative_models import GenerativeModel
from src.config.config import config
from src.dbconnector.dbconnector import save_market_data, get_market_trend_data
import matplotlib.pyplot as plt
from src.config.vertexai_config import initializer

initializer()

DAILY_MARKET_PRICES_API_URL="https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
DAILY_MARKET_PRICES_API_KEY="579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b"


def fetch_current_daily_market_prices(request, state, district=None, market=None, commodity=None, variety=None, offset=1, limit=10):
    """
    Fetch current market prices for a given state and district.
    
    Parameters:
    - state: The state for which to fetch prices.
    - district: The district for which to fetch prices (optional).
    - commodity: The commodity for which to fetch prices (optional).
    - variety: The variety of the commodity (optional).
    - offset: The offset for pagination (default is 1).
    - limit: The number of records to return (default is 10).
    
    Returns:
    - A list of records containing market prices.
    """
    
    api_key = DAILY_MARKET_PRICES_API_KEY
    
    api_endpoint = f"{DAILY_MARKET_PRICES_API_URL}?api-key={api_key}&format=json"
    if state:
        api_endpoint += f"&filters[state.keyword]={state}"
    if district:
        api_endpoint += f"&filters[district]={district}"
    if market:
        api_endpoint += f"&filters[market]={market}"
    if commodity:
        api_endpoint += f"&filters[commodity]={commodity}"
    if variety:
        api_endpoint += f"&filters[variety]={variety}"
    if offset:
        api_endpoint += f"&offset={offset}"
    else:
        api_endpoint += f"&offset=1"
    if limit:
        api_endpoint += f"&limit={limit}"
    else:
        api_endpoint += f"&limit=10"

    res = requests.get(api_endpoint)
    response_body = res.json()
    save_market_data(response_body["records"])
    return response_body["records"]

def get_market_trend(request, state, district, market, commodity, variety=None, type_of_trend="weekly"):
    data = get_market_trend_data(state, commodity, district, market, variety, type_of_trend)
    if not data:
        return {"message": "No data found for the given parameters."}
    else:
        response = []
        for row in data:
            row = {
                "state": row[0],
                "district": row[1],
                "market": row[2],
                "commodity": row[3],
                "variety": row[4],
                "arrival_date": row[5],
                "min_price": row[6],
                "max_price": row[7],
                "modal_price": row[8],
                "created_at": row[9]
            }
            response.append(row)

        # Prepare data for plotting
        dates = [row["arrival_date"] for row in response]
        modal_prices = [row["modal_price"] for row in response]

        type_of_trend = "Weekly" if type_of_trend == "weekly" else "Monthly"
        # Plot the trend
        plt.figure(figsize=(8, 4))
        plt.plot(dates, modal_prices, marker='o')
        plt.title(f"{type_of_trend} price trend for {commodity}")
        plt.xlabel("Date")
        plt.ylabel("Modal Price")
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save plot to a bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')

        return {
            "trend_data": response,
            "trend_chart_base64": img_base64
        }

def market_trend_qna(state, commodity, query, district, market, variety=None, type_of_trend="weekly"):
    market_prices = get_market_trend_data(state, commodity, district, market, variety, type_of_trend)
    model = GenerativeModel(config["generative_model"]["name"])
    
    if not market_prices:
        return {"message": "No data found for the given parameters."}
    else:
        res = model.generate_content(f"""Analyze the provided mandi prices data {market_prices}, which includes the following fields:
                                    state, district, market, commodity, variety, arrival_date, min_price, max_price, modal_price, and created_at.
                                    Focus on identifying trends over the {type_of_trend} period. Answer the following question based on your analysis:
                                    {query}. 
                                    The response should be concise and directly address the question asked, providing clear insights based on the data provided.
                                    Ensure that the answer is easy to understand.
                                """)
        return {"answer": res.text}
    
def import_market_prices_data(data):
    data = save_market_data(data)
    return {"message": "Market prices data imported successfully."}
