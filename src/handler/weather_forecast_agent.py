import requests
import re
from datetime import datetime
from google.cloud import aiplatform_v1beta1 as aiplatform
from vertexai.preview.generative_models import GenerativeModel, GenerationConfig
from src.config.vertexai_config import initializer
from src.config.config import config


initializer()

OPENWEATHER_API_URL="https://api.openweathermap.org/data/2.5"
OPENWEATHER_API_KEY="3037db4dd898fa6fc82acc60ae36223d"

def extract_city_and_intent(question: str):
    city_match = re.search(r"in\s+([a-zA-Z\s]+)", question)
    city = city_match.group(1).strip() if city_match else None
    intent = "forecast" if "forecast" in question.lower() else "current"
    return city, intent

def get_min_max_temps(forecast_data):
    # Group temperatures by date
    temps_by_date = dict()

    for entry in forecast_data:
        if not temps_by_date.get(entry['date']):
            temps_by_date[entry["date"]] = {"temps": [], "condition": entry['condition']}
        
        temps_by_date[entry["date"]]["temps"].append(entry['temp'])

    # For each date, get min and max temp
    min_max_by_date = []
    for date, obj in temps_by_date.items():
        min_max_by_date.append({
            'date': date,
            'condition': obj["condition"],
            'min': min(obj["temps"]),
            'max': max(obj["temps"])
        })
    return min_max_by_date

def get_current_weather(city):
    url = f"{OPENWEATHER_API_URL}/weather"
    api_key = OPENWEATHER_API_KEY

    params = {'q': f"{city},IN", 'appid': api_key, 'units': 'metric'}
    response = requests.get(url, params=params).json()
    dt_str = datetime.utcfromtimestamp(response['dt']).strftime('%Y-%m-%d %H:%M UTC')
    return {
        "datetime": dt_str,
        "temperature": response["main"]["temp"],
        "condition": response["weather"][0]["description"],
        "humidity": response["main"]["humidity"]
    }

def get_forecast(city, days=2):
    url = f"{OPENWEATHER_API_URL}/forecast"
    api_key = OPENWEATHER_API_KEY

    params = {'q': f"{city},IN", 'appid': api_key, 'units': 'metric'}
    response = requests.get(url, params=params).json()
    forecast_list = []
    for item in response["list"][:days * 8]:  # 8 intervals per day
        forecast_list.append({
            "datetime": datetime.utcfromtimestamp(item["dt"]).strftime('%Y-%m-%d %H:%M UTC'),
            "temp": item["main"]["temp"],
            "condition": item["weather"][0]["description"]
        })
    return forecast_list

def get_forecast_min_max(city, days=2):
    url = f"{OPENWEATHER_API_URL}/forecast"
    api_key = OPENWEATHER_API_KEY

    params = {'q': f"{city},IN", 'appid': api_key, 'units': 'metric'}
    response = requests.get(url, params=params).json()
    forecast_list = []
    for item in response["list"][:days * 8]:  # 8 intervals per day
        forecast_list.append({
            "date": datetime.utcfromtimestamp(item["dt"]).strftime('%Y-%m-%d'),
            "temp": item["main"]["temp"],
            "condition": item["weather"][0]["description"]
        })
    forecast_list = get_min_max_temps(forecast_list)
    return forecast_list

def ask_gemini_weather(question):
    city, intent = extract_city_and_intent(question)
    if not city:
        return "I couldn't detect the city in your question. Please mention a valid Indian city."

    try:
        if intent == "forecast":
            forecast_data = get_forecast(city)

            # Group forecast by date
            grouped_forecast = {}
            for item in forecast_data:
                date_key = item['datetime'].split()[0]
                grouped_forecast.setdefault(date_key, []).append(item)

            # Prepare structured forecast text
            forecast_summary = ""
            for date, entries in grouped_forecast.items():
                day_summary = f"Date: {date}\n"
                for entry in entries:
                    time = entry['datetime'].split()[1]
                    day_summary += f"  {time} - {entry['temp']}°C, {entry['condition']}\n"
                forecast_summary += day_summary + "\n"

            prompt = f"""
            You are a kind and respectful weather assistant helping users in India, especially from rural or semi-rural areas.

            Using the forecast data for **{city}**, provide a **clear and polite weather update**.

            For each date:
            - Start with the date clearly
            - Show time-wise weather (temperature and condition)
            - End with a **simple, polite sentence** summarizing the day's weather. Use kind language. Avoid technical terms. Mention if rain or heat is expected.

            Do **not** include data source or advanced suggestions.

            Forecast Data:
            {forecast_summary}
            """
        else:
            current = get_current_weather(city)
            prompt = f"""
            You are a respectful and kind weather assistant.

            Present the **current weather** in {city}, India:
            - Show the temperature, condition, humidity and time
            - Then add **a short, clear, polite summary**. Mention if it is hot, cool, rainy, etc. Be encouraging.

            Current Weather Data:
            - Temperature: {current['temperature']}°C
            - Condition: {current['condition']}
            - Humidity: {current['humidity']}%
            - Time: {current['datetime']}

            Avoid any technical jargon or source information.
            """

        vertex_model = GenerativeModel(config["generative_model"]["name"])
        generation_config = GenerationConfig(temperature=0.7)
        response = vertex_model.generate_content(prompt, generation_config=generation_config)
        return response.text.strip() if hasattr(response, "text") else "⚠️ No answer generated."

    except Exception as e:
        return f"⚠️ Error fetching weather for {city}: {str(e)}"
