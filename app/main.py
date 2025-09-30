from fastapi import FastAPI
from app.routes import router

app = FastAPI(
    title="Gutenberg Character Analyzer API",
    description="Analyze Project Gutenberg books for characters and relationships using LlamaIndex",
    version="2.0.0"
)

app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {
        "message": "Gutenberg Character Analyzer API",
        "endpoints": {
            "analyze": "/api/analyze?book_id=1342&provider=gpt",
            "health": "/api/health"
        }
    }