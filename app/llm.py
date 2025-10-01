import json
import requests
from typing import Dict, List
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


def get_available_models(provider: str) -> List[Dict[str, str]]:
    """Get list of available models for a provider."""
    if provider == "ollama":
        return _get_ollama_models()
    elif provider == "openai":
        return [
            {"id": "gpt-4o", "name": "GPT-4o"},
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini"},
            {"id": "gpt-4-turbo", "name": "GPT-4 Turbo"},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo"},
        ]
    elif provider == "groq":
        return [
            {"id": "llama-3.3-70b-versatile", "name": "Llama 3.3 70B"},
            {"id": "llama-3.1-70b-versatile", "name": "Llama 3.1 70B"},
            {"id": "llama-3.1-8b-instant", "name": "Llama 3.1 8B"},
            {"id": "qwen/qwen3-32b", "name": "qwen3-32b"},
            {"id": "gemma2-9b-it", "name": "Gemma 2 9B"},
        ]
    elif provider == "sambanova":
        return [
            {"id": "Meta-Llama-3.1-8B-Instruct", "name": "Llama 3.1 8B Instruct"},
            {"id": "Meta-Llama-3.1-70B-Instruct", "name": "Llama 3.1 70B Instruct"},
            {"id": "Meta-Llama-3.1-405B-Instruct", "name": "Llama 3.1 405B Instruct"},
        ]
    elif provider == "gemini":
        return [
            {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash"},
            {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro"},
            {"id": "gemini-2.0-flash-exp", "name": "Gemini 2.0 Flash (Experimental)"},
        ]
    return []


def _get_ollama_models() -> List[Dict[str, str]]:
    """Fetch available models from Ollama."""
    try:
        resp = requests.get(settings.OLLAMA_MODELS_URL, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        
        models = []
        for model in data.get("models", []):
            # Extract model name and size info
            model_name = model.get("name", "")
            model_size = model.get("size", 0)
            model_modified = model.get("modified_at", "")
            
            # Format size in GB
            size_gb = model_size / (1024**3) if model_size else 0
            display_name = f"{model_name} ({size_gb:.1f}GB)" if size_gb > 0 else model_name
            
            models.append({
                "id": model_name,
                "name": display_name,
                "size_bytes": model_size,
                "modified_at": model_modified
            })
        
        return models
    except requests.exceptions.ConnectionError:
        print(f"Cannot connect to Ollama at {settings.OLLAMA_BASE_URL}")
        print("Make sure Ollama is running: ollama serve")
        return []
    except Exception as e:
        print(f"Error fetching Ollama models: {e}")
        return [{"id": settings.OLLAMA_MODEL, "name": settings.OLLAMA_MODEL}]


def analyze_chunk_with_llm(chunk: str, provider: str = None, model: str = None) -> dict:
    """Send a text chunk to LLM and return parsed JSON dict."""
    if provider is None:
        provider = settings.PROVIDER.lower()

    if provider == "openai":
        return _call_openai(chunk, model)
    elif provider == "groq":
        return _call_groq(chunk, model)
    elif provider == "sambanova":
        return _call_sambanova(chunk, model)
    elif provider == "gemini":
        return _call_gemini(chunk, model)
    elif provider == "ollama":
        return _call_ollama(chunk, model)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def _call_openai(chunk: str, model: str = None) -> dict:
    """Call OpenAI API."""
    prompt = PROMPT_TEMPLATE.format(chunk=chunk)
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": model or settings.OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful text analysis assistant."},
            {"role": "user", "content": prompt},
        ],
        "temperature": settings.TEMPERATURE,
        "response_format": {"type": "json_object"},
    }
    resp = requests.post(settings.OPENAI_API_URL, headers=headers, json=body, timeout=60)
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    return json.loads(content)


def _call_groq(chunk: str, model: str = None) -> dict:
    """Call Groq API (OpenAI-compatible)."""
    prompt = PROMPT_TEMPLATE.format(chunk=chunk)
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": model or settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful text analysis assistant."},
            {"role": "user", "content": prompt},
        ],
        "temperature": settings.TEMPERATURE,
        "response_format": {"type": "json_object"},
    }
    resp = requests.post(settings.GROQ_API_URL, headers=headers, json=body, timeout=60)
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    return json.loads(content)


def _call_sambanova(chunk: str, model: str = None) -> dict:
    """Call SambaNova Cloud API."""
    prompt = PROMPT_TEMPLATE.format(chunk=chunk)
    headers = {
        "Authorization": f"Bearer {settings.SAMBANOVA_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": model or settings.SAMBANOVA_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful text analysis assistant."},
            {"role": "user", "content": prompt},
        ],
        "temperature": settings.TEMPERATURE,
    }
    resp = requests.post(settings.SAMBANOVA_API_URL, headers=headers, json=body, timeout=60)
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    
    # Clean up response if needed
    if "```json" in content:
        start = content.find("```json") + 7
        end = content.find("```", start)
        content = content[start:end].strip()
    
    return json.loads(content)


def _call_gemini(chunk: str, model: str = None) -> dict:
    """Call Google Gemini API."""
    model_name = model or settings.GEMINI_MODEL
    url = f"{settings.GEMINI_API_URL}/{model_name}:generateContent?key={settings.GEMINI_API_KEY}"
    
    prompt = PROMPT_TEMPLATE.format(chunk=chunk)
    body = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": settings.TEMPERATURE,
            "responseMimeType": "application/json"
        }
    }
    
    resp = requests.post(url, json=body, timeout=60)
    resp.raise_for_status()
    
    data = resp.json()
    content = data["candidates"][0]["content"]["parts"][0]["text"]
    return json.loads(content)


def _call_ollama(chunk: str, model: str = None) -> dict:
    """Call local Ollama server."""
    prompt = PROMPT_TEMPLATE.format(chunk=chunk)
    body = {
        "model": model or settings.OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful text analysis assistant."},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "format": "json"
    }

    resp = requests.post(settings.OLLAMA_API_URL, json=body, timeout=120)
    resp.raise_for_status()

    data = resp.json()
    content = data["message"]["content"]
    return json.loads(content)