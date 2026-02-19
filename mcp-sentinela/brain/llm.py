import requests
import json

class OllamaClient:
    """
    Client for interacting with a local Ollama instance.
    """
    def __init__(self, model="qwen2.5:7b", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.api_chat = f"{base_url}/api/chat"
        self.api_tags = f"{base_url}/api/tags"

    def is_running(self) -> bool:
        """Checks if Ollama service is running."""
        try:
            response = requests.get(self.base_url, timeout=2)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def is_model_available(self) -> bool:
        """Checks if the configured model is available locally."""
        try:
            response = requests.get(self.api_tags, timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                for m in models:
                    # Ollama model names can be 'qwen2.5:7b' or just 'qwen2.5'
                    # We check if self.model is part of the name
                    if self.model in m.get("name", ""):
                        return True
            return False
        except requests.RequestException:
            return False

    def chat(self, message: str, system_prompt: str = "") -> str:
        """
        Sends a message to the model and streams or returns the response.
        For simplicity in HUD, we return the full string currently.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": message})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False 
        }

        try:
            response = requests.post(self.api_chat, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "")
        except requests.RequestException as e:
            return f"Error: {e}"
