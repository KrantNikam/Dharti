import re
from google.cloud import translate_v2 as translate
from src.config.vertexai_config import credentials

translator = translate.Client(credentials=credentials)

#Translation Utilities
def translate_to_english(text):
    result = translator.translate(text, target_language='en')
    return result['translatedText']

def translate_back(text, language):
    return translator.translate(text, target_language=language)['translatedText']


def clean_response(text):
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"(?<!\n)(\d+\.)", r"\n\n\1", text)
    text = re.sub(r"(?<!\n)(\s*-\s+)", r"\n\1", text)
    text = re.sub(r"\n{3,}", r"\n\n", text)
    return text.strip()