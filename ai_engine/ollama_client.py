import requests
import json

OLLAMA_API = "http://localhost:11434/api/generate"

def call_ollama(prompt: str, mode: str = "default") -> str:
    model_map = {
        "career": "mistral",      # for role/skill suggestions
        "question": "mistral",   # for interview questions
        "score": "gemma:7b",     # for scoring answers
        "default": "mistral"
    }

    model = model_map.get(mode, "mistral")

    print(f"\n⚙️ Calling model: {model} | mode: {mode}\n")

    try:
        response = requests.post(
            OLLAMA_API,
            json={
                "model": model,
                "prompt": prompt,
                "stream": True
            },
            stream=True
        )
        response.raise_for_status()

        full_output = ""

        for line in response.iter_lines():
            if line:
                try:
                    decoded = json.loads(line.decode("utf-8"))  # ✅ Use safe JSON decoding
                    token = decoded.get("response", "")
                    print(token, end='', flush=True)  # Live output
                    full_output += token
                except json.JSONDecodeError as e:
                    print(f"\n⚠️ JSON decode error: {e}")
                except Exception as e:
                    print(f"\n⚠️ Unexpected error: {e}")

        return full_output.strip()

    except Exception as e:
        print(f"\n Ollama call failed: {e}")
        return ""
