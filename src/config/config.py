from dotenv import load_dotenv
import os

load_dotenv()

config = {
    'postgres': {
        'host': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME', 'postgres'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD'),
        'port': os.getenv('DB_PORT', 5432),
    },
    'apis':{
        'travily_api_url': os.getenv('TRAVILY_API_URL'),
        'travily_api_key': os.getenv('TRAVILY_API_KEY'),
        'daily_market_prices_api_url': os.getenv('DAILY_MARKET_PRICES_API_URL'),
        'daily_market_prices_api_key': os.getenv('DAILY_MARKET_PRICES_API_KEY'),
        'openweather_api_url': os.getenv('OPENWEATHER_API_URL'),
        'openweather_api_key': os.getenv('OPENWEATHER_API_KEY')
    },
    'generative_model': {
        'name': 'gemini-2.5-pro'
    }
    # 'postgres': {
    #     'host':  'localhost',
    #     'database':  'postgres',
    #     'user': 'postgres',
    #     'password': 'Kranti@26',
    #     'port': 5432
    # }

}


