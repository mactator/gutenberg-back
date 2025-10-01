from fastapi import APIRouter, Query, HTTPException
from app.config import settings
from app.gutenberg import fetch_gutenberg_text, strip_headers
from app.analyzer import BookAnalyzer
from app.llm import get_available_models

# routes.py

router = APIRouter()



@router.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "provider": settings.PROVIDER,
        "available_providers": ["openai", "groq", "gemini", "ollama"]
    }

@router.get("/providers")
def list_providers():
    """List all available LLM providers and their configuration status."""
    providers = {
        "openai": {
            "name": "OpenAI",
            "configured": bool(settings.OPENAI_API_KEY),
            "default_model": settings.OPENAI_MODEL
        },
        "groq": {
            "name": "Groq",
            "configured": bool(settings.GROQ_API_KEY),
            "default_model": settings.GROQ_MODEL
        },
        # "sambanova": {
        #     "name": "SambaNova Cloud",
        #     "configured": bool(settings.SAMBANOVA_API_KEY),
        #     "default_model": settings.SAMBANOVA_MODEL
        # },
        "gemini": {
            "name": "Google Gemini",
            "configured": bool(settings.GEMINI_API_KEY),
            "default_model": settings.GEMINI_MODEL
        },
        "ollama": {
            "name": "Ollama (Local)",
            "configured": True,  # Always available if running
            "default_model": settings.OLLAMA_MODEL,
            "base_url": settings.OLLAMA_BASE_URL
        }
    }
    return {
        "providers": providers,
        "current_provider": settings.PROVIDER
    }

@router.get("/models")
def list_models(
    provider: str = Query(..., description="Provider name: openai, groq, sambanova, gemini, or ollama")
):
    """
    Get list of available models for a specific provider.
    
    For Ollama, this will fetch the actual models installed on your system.
    For other providers, it returns a curated list of popular models.
    """
    provider = provider.lower()
    
    valid_providers = ["openai", "groq", "sambanova", "gemini", "ollama"]
    if provider not in valid_providers:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid provider. Must be one of: {', '.join(valid_providers)}"
        )
    
    try:
        models = get_available_models(provider)
        return {
            "provider": provider,
            "models": models,
            "count": len(models)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch models for {provider}: {str(e)}"
        )

@router.get("/analyze")
def analyze(
    book_id: int = Query(..., description="Project Gutenberg book ID", example=1342),
    provider: str = Query(None, description="LLM provider: openai, groq, sambanova, gemini, or ollama"),
    model: str = Query(None, description="Specific model to use (optional, uses provider default if not specified)"),
):
    """
    Analyze a Project Gutenberg book to extract characters and their relationships.
    
    Examples:
    - /api/analyze?book_id=1342 (Pride and Prejudice with default provider)
    - /api/analyze?book_id=1342&provider=groq&model=llama-3.3-70b-versatile
    - /api/analyze?book_id=84&provider=ollama&model=llama3.2
    """
    try:
        # Fetch and clean book text
        raw_text = fetch_gutenberg_text(book_id)
        clean_text = strip_headers(raw_text)
        
        # Determine provider
        chosen_provider = provider.lower() if provider else settings.PROVIDER
        
        valid_providers = ["openai", "groq", "sambanova", "gemini", "ollama"]
        if chosen_provider not in valid_providers:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid provider: {chosen_provider}. Must be one of: {', '.join(valid_providers)}"
            )
        
        # Initialize analyzer and process
        analyzer = BookAnalyzer(provider=chosen_provider, model=model)
        result = analyzer.analyze(clean_text)
        
        # Add metadata
        result["book_id"] = book_id
        result["provider"] = chosen_provider
        result["model"] = model or f"default ({chosen_provider})"
        result["text_length"] = len(clean_text)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")