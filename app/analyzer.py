from typing import Dict, List
from llama_index.core import Document, VectorStoreIndex, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.llms import LLM
from llama_index.llms.openai import OpenAI
from llama_index.llms.ollama import Ollama
from llama_index.core.prompts import PromptTemplate
import json
from app.config import settings

ANALYSIS_PROMPT = PromptTemplate(
    """You are a literary analyst. Extract character information from this text excerpt.

IMPORTANT: Respond with ONLY a JSON object. No other text before or after.

Required JSON format:
{{
  "characters": [
    {{
      "name": "Full Character Name",
      "aliases": ["nickname1", "nickname2"],
      "mention_count": 3,
      "sample_quotes": ["A brief quote about this character"]
    }}
  ],
  "interactions": [
    {{
      "source": "Character1 Name",
      "target": "Character2 Name",
      "weight": 2,
      "sample_quotes": ["Quote showing their interaction"]
    }}
  ]
}}

Rules:
- Use complete character names (first and last if available)
- Count how many times each character appears in THIS excerpt
- Weight = number of times two characters interact or are mentioned together
- Keep quotes under 100 characters
- If no characters found, return empty arrays: {{"characters": [], "interactions": []}}
- DO NOT include any text outside the JSON object

Text to analyze:
{text}"""
)

class BookAnalyzer:
    def __init__(self, provider: str = None):
        """Initialize the analyzer with specified LLM provider."""
        self.provider = provider or settings.PROVIDER
        self.llm = self._setup_llm()
        
        # Configure LlamaIndex settings
        Settings.llm = self.llm
        Settings.chunk_size = settings.CHUNK_SIZE
        Settings.chunk_overlap = settings.CHUNK_OVERLAP
    
    def _setup_llm(self) -> LLM:
        """Set up the LLM based on provider."""
        if self.provider == "gpt":
            return OpenAI(
                api_key=settings.OPENAI_API_KEY,
                model=settings.MODEL_NAME,
                temperature=settings.TEMPERATURE,
            )
        elif self.provider == "ollama":
            return Ollama(
                base_url=settings.OLLAMA_BASE_URL,
                model=settings.OLLAMA_MODEL,
                temperature=settings.TEMPERATURE,
                request_timeout=120.0,
            )
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def analyze(self, text: str) -> Dict:
        """
        Analyze a book text to extract characters and relationships.
        """
        # Create document and split into chunks
        document = Document(text=text)
        parser = SentenceSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )
        nodes = parser.get_nodes_from_documents([document])
        
        # Analyze each chunk
        chunk_results = []
        for i, node in enumerate(nodes):
            try:
                result = self._analyze_chunk(node.text)
                chunk_results.append(result)
            except Exception as e:
                print(f"Error analyzing chunk {i}: {e}")
                continue
        
        # Merge results
        merged = self._merge_results(chunk_results)
        merged["chunks_analyzed"] = len(nodes)
        merged["chunks_successful"] = len(chunk_results)
        
        return merged
    
    def _analyze_chunk(self, chunk_text: str) -> Dict:
        """Analyze a single chunk of text."""
        prompt = ANALYSIS_PROMPT.format(text=chunk_text)
        
        response = self.llm.complete(prompt)
        content = response.text.strip()
        
        # Clean up response - handle various markdown/formatting
        if "```json" in content:
            # Extract content between ```json and ```
            start = content.find("```json") + 7
            end = content.find("```", start)
            if end != -1:
                content = content[start:end]
        elif "```" in content:
            # Extract content between ``` markers
            parts = content.split("```")
            if len(parts) >= 2:
                content = parts[1]
        
        content = content.strip()
        
        # Try to find JSON object if there's extra text
        if not content.startswith("{"):
            start = content.find("{")
            if start != -1:
                content = content[start:]
        if not content.endswith("}"):
            end = content.rfind("}")
            if end != -1:
                content = content[:end+1]
        
        try:
            parsed = json.loads(content)
            # Validate structure
            if "characters" not in parsed:
                parsed["characters"] = []
            if "interactions" not in parsed:
                parsed["interactions"] = []
            return parsed
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            print(f"Raw response: {response.text[:500]}")
            print(f"Cleaned content: {content[:500]}")
            return {"characters": [], "interactions": []}
    
    def _merge_results(self, results: List[Dict]) -> Dict:
        """Merge character and interaction data from multiple chunks."""
        characters = {}
        interactions = {}
        
        for result in results:
            # Merge characters
            for char in result.get("characters", []):
                name = char["name"].strip()
                if name not in characters:
                    characters[name] = {
                        "name": name,
                        "aliases": set(char.get("aliases", [])),
                        "mention_count": char.get("mention_count", 0),
                        "sample_quotes": []
                    }
                else:
                    characters[name]["aliases"].update(char.get("aliases", []))
                    characters[name]["mention_count"] += char.get("mention_count", 0)
                
                # Add quotes (limit to avoid duplication)
                for quote in char.get("sample_quotes", [])[:2]:
                    if quote and len(characters[name]["sample_quotes"]) < 3:
                        characters[name]["sample_quotes"].append(quote)
            
            # Merge interactions
            for interaction in result.get("interactions", []):
                source = interaction["source"].strip()
                target = interaction["target"].strip()
                key = tuple(sorted([source, target]))
                
                if key not in interactions:
                    interactions[key] = {
                        "source": key[0],
                        "target": key[1],
                        "weight": interaction.get("weight", 1),
                        "sample_quotes": []
                    }
                else:
                    interactions[key]["weight"] += interaction.get("weight", 1)
                
                # Add quotes
                for quote in interaction.get("sample_quotes", [])[:2]:
                    if quote and len(interactions[key]["sample_quotes"]) < 3:
                        interactions[key]["sample_quotes"].append(quote)
        
        # Convert to final format
        nodes = [
            {
                "id": char["name"],
                "label": char["name"],
                "aliases": list(char["aliases"]),
                "mention_count": char["mention_count"],
                "sample_quotes": char["sample_quotes"]
            }
            for char in characters.values()
        ]
        
        edges = list(interactions.values())
        
        return {
            "nodes": nodes,
            "edges": edges,
            "character_count": len(nodes),
            "interaction_count": len(edges)
        }