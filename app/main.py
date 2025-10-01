from fastapi import FastAPI
from app.routes import router
from fastapi.middleware.cors import CORSMiddleware
# main.py

app = FastAPI(
    title="Gutenberg Character Analyzer API",
    description="Analyze Project Gutenberg books for characters and relationships using LlamaIndex",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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