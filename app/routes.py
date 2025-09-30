from fastapi import APIRouter, Query, HTTPException
from app.gutenberg import fetch_gutenberg_text, strip_headers
from app.analyzer import BookAnalyzer
from app.config import settings

router = APIRouter()

@router.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "provider": settings.PROVIDER,
        "model": settings.MODEL_NAME if settings.PROVIDER == "gpt" else settings.OLLAMA_MODEL
    }

@router.get("/analyze")
def analyze(
    book_id: int = Query(..., description="Project Gutenberg book ID", example=1342),
    provider: str = Query(None, description="LLM provider: 'gpt' or 'ollama'"),
):
    """
    Analyze a Project Gutenberg book to extract characters and their relationships.
    
    Example: /api/analyze?book_id=1342 (Pride and Prejudice)
    """
    try:
        # Fetch and clean book text
        raw_text = fetch_gutenberg_text(book_id)
        clean_text = strip_headers(raw_text)
        
        # Determine provider
        chosen_provider = provider.lower() if provider else settings.PROVIDER
        
        if chosen_provider not in ["gpt", "ollama"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid provider: {chosen_provider}. Must be 'gpt' or 'ollama'"
            )
        
        # Initialize analyzer and process
        analyzer = BookAnalyzer(provider=chosen_provider)
        result = analyzer.analyze(clean_text)
        
        # Add metadata
        result["book_id"] = book_id
        result["provider"] = chosen_provider
        result["text_length"] = len(clean_text)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")