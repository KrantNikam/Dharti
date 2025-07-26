from vertexai.generative_models import GenerativeModel, GenerationConfig
from src.config.config import config
from src.config.vertexai_config import initializer
from src.utils.common import clean_response

initializer()

def ask_gemini_farming_planner(payload):
    crop_name = payload.get("crop_name")
    farmland_length = payload.get("farmland_length")
    farmland_width = payload.get("farmland_width")
    spacing_distance = payload.get("spacing_distance")
    irrigation_type = payload.get("irrigation_type")
    soil_condition = payload.get("soil_condition")
    weather_condition = payload.get("weather_condition")

    system_prompt = """
    You are an AI assistant helping farmers optimize crop management by suggesting where and how to fertilize secondary crops (intercrops) on a given farmland.

    The inputs provided will include:
    1. **Farmland length** to determine the length available for crop planting.
    2. **Farmland width** to determine the width available for crop planting.
    3. **Primary crop's irrigation**: Information about how the primary crop is being irrigated (drip irrigation, sprinklers, rain-fed, etc.).
    4. **Spacing between primary crops**: The distance between individual plants of the primary crop, which will help calculate available space for the secondary crop.
    5. **Soil condition**: The soil type in the farmland (e.g., loamy, sandy, clay, acidic, etc.).
    6. **Weather condition**: The climate of the region (e.g., temperate, arid, rainfall).
    7. **Primary crop name**: The crop being cultivated as the primary crop.

    Based on these inputs, the system should:
    1. **Suggest where to fertilize or plant the secondary crop** based on the primary crop's spacing and irrigation method.
    2. Provide insights about:
        - **Intercrop compatibility**: How the secondary crop will fit into the irrigation and spacing pattern of the primary crop.
        - **Optimal fertilization zones**: Areas within the farmland that can support the secondary crop without interfering with the primary crop's needs.
        - **Watering needs**: How to ensure the secondary crop receives adequate irrigation without affecting the primary crop.

    Please ensure that the suggestions:
    1. **Do not interfere with the primary crop's growth**.
    2. **Consider irrigation methods** to ensure the secondary crop is properly watered.
    3. **Account for soil and weather conditions** to determine which secondary crops would perform best and where they can be planted for optimal yields.

    Generate the recommendations based on the user's input. Provide response in plain text format.
    """

    # Format the user input into a structured prompt
    user_input = f"""
    Farmland Length: {farmland_length}, Width: {farmland_width}
    Primary crop: {crop_name}
    Spacing between crops: {spacing_distance} meters
    Irrigation method: {irrigation_type}
    Soil condition: {soil_condition}
    Weather condition: {weather_condition}
    """
    
    prompt = f"{system_prompt}\n{user_input}\nPlease provide the intercrop suggestions and fertilization plan."

    
    # Call the OpenAI API (Gemini 2.5 or GPT-like model) to generate a response
    generation_config = GenerationConfig(
        temperature=0.7,
        top_p=0.95,
        top_k=40,
    )

    model = GenerativeModel(config["generative_model"]["name"])
    
    response = model.generate_content(prompt, generation_config=generation_config)
    response = response.text.strip() if response and hasattr(response, 'text') else "No response generated."
    response = clean_response(response)
    return response
