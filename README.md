# Book Character Analyzer

Analyze books from Project Gutenberg to find characters and their relationships using AI.

## What it does

Give it a book ID from Project Gutenberg, and it will:
- Find all the characters
- Track how often they're mentioned
- Map their interactions
- Return everything as JSON for visualization

## Quick Start

### 1. Install

```bash
pip install -r requirements.txt
```

### 2. Setup API Keys

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
nano .env
```

You only need keys for the providers you want to use:

```bash
PROVIDER=openai                    # Default provider
OPENAI_API_KEY=sk-...             # For OpenAI
GROQ_API_KEY=gsk_...              # For Groq (optional)
SAMBANOVA_API_KEY=...             # For SambaNova (optional)
GEMINI_API_KEY=...                # For Gemini (optional)
OLLAMA_BASE_URL=http://localhost:11434  # For local Ollama
```

### 3. Run

```bash
uvicorn main:app --reload
```

Server runs at `http://localhost:8000`

## API Usage

### See what's available

```bash
# Check if server is running
curl http://localhost:8000/api/health

# See which providers you have configured
curl http://localhost:8000/api/providers

# See available models for a provider
curl http://localhost:8000/api/models?provider=ollama
curl http://localhost:8000/api/models?provider=groq
```

### Analyze a book

```bash
# Use default provider (from .env)
curl "http://localhost:8000/api/analyze?book_id=1342"

# Use a specific provider
curl "http://localhost:8000/api/analyze?book_id=1342&provider=groq"

# Use a specific provider and model
curl "http://localhost:8000/api/analyze?book_id=1342&provider=sambanova&model=Meta-Llama-3.1-70B-Instruct"
```

## Supported AI Providers

- **OpenAI** - GPT-4o, GPT-4o-mini (requires API key)
- **Groq** - Fast Llama models (requires API key, has free tier)
- **Gemini** - Google's models (requires API key)
- **Ollama** - Run models locally (no API key needed)

## Popular Books to Try

| ID | Book |
|----|------|
| 1342 | Pride and Prejudice |
| 84 | Frankenstein |
| 11 | Alice in Wonderland |
| 1661 | Sherlock Holmes |
| 98 | A Tale of Two Cities |
| 2701 | Moby Dick |

Find more at [gutenberg.org](https://www.gutenberg.org)

## Example Response

```json
{
  "nodes": [
    {
      "id": "Elizabeth Bennet",
      "label": "Elizabeth Bennet",
      "aliases": ["Lizzy", "Eliza"],
      "mention_count": 245
    },
    {
      "id": "Mr. Darcy",
      "label": "Mr. Darcy",
      "mention_count": 198
    }
  ],
  "edges": [
    {
      "source": "Elizabeth Bennet",
      "target": "Mr. Darcy",
      "weight": 87
    }
  ],
  "character_count": 15,
  "interaction_count": 42
}
```

## Using Ollama (Local Models)

1. Install Ollama from [ollama.com](https://ollama.com)
2. Download a model: `ollama pull llama3.2`
3. Start Ollama: `ollama serve`
4. Test it: `python test_ollama.py`

## Common Issues

**"Connection refused" with Ollama**
- Make sure Ollama is running: `ollama serve`
- Check models are installed: `ollama list`

**"Invalid API key"**
- Check your `.env` file has the right key
- Restart the server after changing `.env`

**Book takes too long to analyze**
- Try a smaller book first (book 11 is short)
- Use a faster model like `gpt-4o-mini` or `llama-3.1-8b-instant`
- Reduce chunk size in `.env`: `CHUNK_SIZE=1024`

**SambaNova model errors**
- Use the exact model names from `/api/models?provider=sambanova`
- Example: `Meta-Llama-3.1-8B-Instruct`

## What's Next?

This API returns character networks as JSON. You can:
- Build a web frontend with D3.js or Cytoscape for visualization
- Create a graph database of book characters
- Compare character networks across different books
- Use it for literature analysis or research

## License

MIT