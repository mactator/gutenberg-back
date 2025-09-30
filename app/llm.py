import requests
import json
from app.config import settings

# llm.py

PROMPT_TEMPLATE = """
You are a literary analyst. Analyze the following text and extract characters and their interactions.

Return the output strictly as JSON in the following format:
{{
  "characters": [
    {{
      "name": "Romeo",
      "interactions": {{"Juliet": 23, "Mercutio": 12}}
    }}
  ]
}}

Text:
{chunk}
"""



def analyze_chunk_with_llm(chunk: str, provider: str = None) -> dict:
    """Send a text chunk to GPT or Ollama and return parsed JSON dict."""
    if provider is None:
        provider = settings.PROVIDER.lower()

    if provider == "gpt":
        return _call_openai(chunk)
    elif provider == "ollama":
        return _call_ollama(chunk)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def _call_openai(chunk: str) -> dict:
    """Call OpenAI GPT endpoint."""
    prompt = PROMPT_TEMPLATE.format(chunk=chunk)
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": settings.MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are a helpful text analysis assistant."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
        "response_format": {"type": "json_object"},
    }
    resp = requests.post(settings.OPENAI_API_URL, headers=headers, json=body, timeout=60)
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    return json.loads(content)


def _call_ollama(chunk: str) -> dict:
    """Call local Ollama server."""
    prompt = PROMPT_TEMPLATE.format(chunk=chunk)
    body = {
    "model": settings.OLLAMA_MODEL,
    "messages": [
        {"role": "system", "content": "You are a helpful text analysis assistant."},
        {"role": "user", "content": prompt},
    ],
    "stream": False
    }

    resp = requests.post(settings.OLLAMA_API_URL, json=body, timeout=120)
    resp.raise_for_status()

    # Ollama streams chunks → final message is in 'message'
    data = resp.json()
    content = data["message"]["content"]
    return json.loads(content)
