from vertexai.generative_models import GenerativeModel, GenerationConfig, Part, Image
from src.utils.common import translate_to_english, translate_back, clean_response
from src.config.vertexai_config import initializer
from src.config.config import config

initializer()

def agronomist_agent(crop_type: str,
                     crop_age: str,
                     language: str = "en",
                     symptoms_description: str = None,
                     image_bytes: bytes = None,
                     mime_type: str = "image/jpeg"):
    """
    Handles both text and image crop diagnosis using Gemini.

    Args:
        crop_type (str): Type of crop (e.g., 'टमाटर', 'tomato').
        crop_age (str): Age in weeks (e.g., '5').
        language (str): 'en', 'hi', etc.
        symptoms_description (str): Optional. Text description of symptoms.
        image_bytes (bytes): Optional. image bytes.

    Returns:
        str: Formatted, translated diagnosis response.
    """
    # Language handling
    crop_type_en = translate_to_english(crop_type) if language != 'en' else crop_type

    # Common prompt format
    prompt_header = f"""
    You are an expert Indian agronomist.

    Please respond in clear numbered points, each starting on a new line.
    Use line breaks between points and subpoints for clarity.

    Example:

    1. Diagnosis: Early blight, a fungal disease affecting tomatoes.
    2. Treatment options:
    - Use fungicide Mancozeb.
    - Organic option: Neem oil spray.
    3. Prevention tips:
    - Avoid overhead watering.
    - Rotate crops yearly.
    """

    # Decide which Gemini model and input to use
    generation_config = GenerationConfig(
        temperature=0.7, 
        top_p=0.95, 
        top_k=40,
    )

    model = GenerativeModel(config["generative_model"]["name"])

    if image_bytes:
        image_part = Part.from_data(data=image_bytes, mime_type=mime_type)

        prompt = f"""{prompt_header}

        The farmer is growing {crop_type_en}, approximately {crop_age} weeks old.
        Below is an image of the affected crop. Diagnose the problem and provide suggestions.
        """
        response = model.generate_content(
            contents=[prompt, image_part],
            generation_config=generation_config
        )

    elif symptoms_description:
        symptoms_en = translate_to_english(symptoms_description) if language != 'en' else symptoms_description

        prompt = f"""{prompt_header}

        The farmer is growing {crop_type_en}, approximately {crop_age} weeks old.
        They report these symptoms:
        "{symptoms_en}"
        """
        response = model.generate_content(prompt, generation_config=generation_config)

    else:
        raise ValueError("Either `symptoms_description` or `image` must be provided.")

    result = clean_response(response.text)

    answer = translate_back(result, language) if language != 'en' else result
    return {"answer": answer}
