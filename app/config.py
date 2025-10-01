import os
from pydantic_settings import BaseSettings
from typing import Literal

# config.py

class Settings(BaseSettings):
    # General
    PROVIDER: Literal["openai", "ollama", "groq", "gemini"] = os.getenv("PROVIDER", "openai")
    
    # OpenAI settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_API_URL: str = "https://api.openai.com/v1/chat/completions"
    
    # Groq settings
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    GROQ_API_URL: str = "https://api.groq.com/openai/v1/chat/completions"
    
    # SambaNova settings
    SAMBANOVA_API_KEY: str = os.getenv("SAMBANOVA_API_KEY", "")
    SAMBANOVA_MODEL: str = os.getenv("SAMBANOVA_MODEL", "Meta-Llama-3.1-8B-Instruct")
    SAMBANOVA_API_URL: str = "https://api.sambanova.ai/v1/chat/completions"
    
    # Gemini settings
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    GEMINI_API_URL: str = "https://generativelanguage.googleapis.com/v1beta/models"
    
    # Ollama settings
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    OLLAMA_API_URL: str = f"{OLLAMA_BASE_URL}/api/chat"
    OLLAMA_MODELS_URL: str = f"{OLLAMA_BASE_URL}/api/tags"
    
    # Text processing
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "2048"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # LLM parameters
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.1"))
    
    class Config:
        env_file = ".env"

settings = Settings()