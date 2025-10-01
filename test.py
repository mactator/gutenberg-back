#!/usr/bin/env python3
"""
Test script to check Ollama connection and list available models.
Run this to verify your Ollama setup before using the API.
"""

import requests
import json
from app.config import settings

def test_ollama_connection():
    """Test if Ollama server is running and accessible."""
    print(f"Testing Ollama connection at: {settings.OLLAMA_BASE_URL}")
    print("-" * 60)
    
    try:
        # Test basic connection
        response = requests.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=5)
        response.raise_for_status()
        
        data = response.json()
        models = data.get("models", [])
        
        if not models:
            print("❌ No models found in Ollama!")
            print("\nTo download models, run:")
            print("  ollama pull llama3.2")
            print("  ollama pull mistral")
            return
        
        print(f"✅ Successfully connected to Ollama!")
        print(f"✅ Found {len(models)} model(s)\n")
        
        print("Available Models:")
        print("-" * 60)
        
        for model in models:
            name = model.get("name", "Unknown")
            size = model.get("size", 0)
            size_gb = size / (1024**3)
            modified = model.get("modified_at", "")
            
            print(f"\n📦 {name}")
            print(f"   Size: {size_gb:.2f} GB")
            print(f"   Modified: {modified[:19] if modified else 'Unknown'}")
            
            # Show details if available
            details = model.get("details", {})
            if details:
                family = details.get("family", "")
                param_size = details.get("parameter_size", "")
                if family:
                    print(f"   Family: {family}")
                if param_size:
                    print(f"   Parameters: {param_size}")
        
        print("\n" + "-" * 60)
        print("\n✨ To use a model in the API:")
        print(f"   GET /api/analyze?book_id=1342&provider=ollama&model={models[0].get('name')}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama!")
        print(f"\nMake sure Ollama is running at {settings.OLLAMA_BASE_URL}")
        print("\nTo start Ollama:")
        print("  ollama serve")
        print("\nOr check if it's running on a different port:")
        print("  ps aux | grep ollama")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check if Ollama is installed: ollama --version")
        print("2. Start Ollama service: ollama serve")
        print("3. Verify base URL in .env file")

if __name__ == "__main__":
    test_ollama_connection()