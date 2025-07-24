import requests
from vertexai.generative_models import GenerativeModel, GenerationConfig
import config.vertexai_config
from config.config import config


# === Tavily Web Search ===
def tavily_search(query):
    url = config["apis"]["travily_api_url"]
    api_key = config["apis"]["travily_api_key"]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "query": query,
        "search_depth": "advanced",
        "max_results": 5,
        "include_answer": True
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Tavily Error: {response.status_code} {response.text}")
    

def ask_gemini_with_web_data(question):
    # Fetch relevant data
    tavily_data = tavily_search(question)
    sources = tavily_data.get("results", [])

    # Build context for Gemini
    source_text = "\n\n".join(
        f"Title: {item['title']}\nContent: {item.get('content', '')}" for item in sources
    )

    prompt = f"""
        You are a knowledgeable assistant. Using the web-sourced data below, provide a clear and factual answer to the question.
        Cite sources using [1], [2], etc., based on the titles.
        
        You should not include the statement in your answer as - 'Based on the provided web-sourced data' because we dont let our 
        user know that this is websource data.

        Question: {question}

        Sources:
        {source_text}

        Answer:
        """

    # Generate answer with Gemini
    vertex_model = GenerativeModel(config["generative_model"]["name"])
    generation_config = GenerationConfig(
        temperature=0.9,
        top_p=0.1,
        top_k=32,
        candidate_count=1,
        max_output_tokens=8192,
    )
    response = vertex_model.generate_content(prompt, generation_config=generation_config)
    return response.text.strip() if response and hasattr(response, 'text') else "No response generated."
