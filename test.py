import requests
import json

body = {
    "model": "llama2",
    "messages": [
        {"role": "system", "content": "You are a helpful text analysis assistant."},
        {"role": "user", "content": "Analyze the following text and provide a summary, main themes, and key characters in JSON format."},
    ],
    "stream": False
}
response = requests.post("http://localhost:11434/api/chat", json=body, timeout=120)

response.raise_for_status()
content = response.json()["message"]["content"]
print(content)
