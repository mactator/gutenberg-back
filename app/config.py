import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # General
    PROVIDER: str = os.getenv("PROVIDER", "gpt")  # "gpt" or "ollama"
    
    # OpenAI/GPT settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gpt-4o-mini")
    
    # Ollama settings
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    
    # Text processing
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "2048"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # LLM parameters
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.1"))
    
    class Config:
        env_file = ".env"

settings = Settings()