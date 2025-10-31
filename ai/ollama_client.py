import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma:2b"  # 예: Ollama에서 설치한 모델 이름

def query_ollama(prompt: str) -> str:
    payload = {"model": MODEL_NAME, "prompt": prompt}
    response = requests.post(OLLAMA_URL, json=payload, stream=True)

    output = ""
    for line in response.iter_lines():
        if line:
            try:
                data = json.loads(line)
                if "response" in data:
                    output += data["response"]
            except:
                pass
    return output.strip()
