# config/ollama_config.py

import requests

OLLAMA_HOST = "http://localhost:11434"
MODEL_NAME = "mistral:latest"  # or "deepseek-chat:14b"

def chat_with_model(prompt: str, system_prompt: str = "", temperature: float = 0.7):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "system": system_prompt,
        "temperature": temperature,
        "stream": False
    }
    response = requests.post(f"{OLLAMA_HOST}/api/generate", json=payload)
    
    if response.status_code == 200:
        return response.json()["response"]
    else:
        raise Exception(f"Ollama Error: {response.status_code} → {response.text}")
