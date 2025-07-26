
from vertexai.generative_models import GenerativeModel, GenerationConfig, Part, Image
from src.utils.common import translate_back
from src.handler.weather_forecast_agent import ask_gemini_weather
from src.handler.schemes_agent import ask_gemini_with_web_data
from src.handler.agronomist_agent import agronomist_agent
from src.config.config import config
from src.config.vertexai_config import initializer

initializer()

def scheme_agent(query: str, language="en"):
    response = ask_gemini_with_web_data(query)
    answer = translate_back(response, language) if language != "en" else response
    return {"answer": answer}

def weather_agent(query: str, language="en"):
    response = ask_gemini_weather(query)
    answer = translate_back(response, language) if language != "en" else response
    return {"answer": answer}


def detect_intent(user_query):
    prompt = f"""
    You are an intent classifier. Categorize the user's query into one of the following 4 categories:

    - **weather** → if the query is about weather, rain, forecast, temperature, or climate
    - **agronomist** → if it is about crop health, diseases, pests, or plant symptoms
    - **scheme** → if it is about government schemes, PM-Kisan, subsidies, insurance, etc.

    User Query: "{user_query}"

    Respond with just one word: weather, agronomist, market, or scheme.
    """
    model = GenerativeModel(config["generative_model"]["name"])
    response = model.generate_content(
        prompt,
        generation_config=GenerationConfig(temperature=0.2)
    )
    return response.text.strip().lower()

def kisan_agent_router(query: str, crop_type=None, crop_age=None, image_bytes=None, language="en"):
    intent = detect_intent(query)

    print(f"======QUERY IS ROUTED TO {intent} AGENT======")

    if intent == "agronomist":
        return agronomist_agent(
            crop_type=crop_type or "tomato",
            crop_age=crop_age or "5",
            language=language,
            symptoms_description=query,
            image_bytes=image_bytes
        )
    elif intent == "scheme":
        return scheme_agent(query, language)
    elif intent == "weather":
        return weather_agent(query, language)
    else:
        return {"message": "❓ Sorry, I could not understand the query. Please ask about crop issues, weather, or government schemes."}

