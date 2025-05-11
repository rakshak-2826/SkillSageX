import os
import requests
from dotenv import load_dotenv

# Load from .env
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ------------------------------
# OpenRouter (GPT) summarizer
# ------------------------------
def summarize_with_openrouter(text: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://chat.openai.com",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an AI resume summarizer. Write a professional and detailed summary "
                    "of the candidate's resume in 4–6 sentences. Highlight their skills, technologies, "
                    "education, experience, notable projects, and work ethic. Use a confident tone."
                )
            },
            {
                "role": "user",
                "content": f"Resume text:\n{text[:4000]}"
            }
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# ------------------------------
# Gemini summarizer fallback
# ------------------------------
def summarize_with_gemini(text: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            "Please write a detailed and well-structured resume summary (4–6 sentences). "
                            "Include the candidate’s technical skills, education, experience, notable projects, and strengths.\n\n"
                            f"Resume:\n{text[:4000]}"
                        )
                    }
                ]
            }
        ]
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]

# ------------------------------
# Combined fallback logic
# ------------------------------
def summarize_resume(text: str) -> str:
    try:
        print("Trying OpenRouter GPT...")
        return summarize_with_openrouter(text)
    except Exception as e1:
        print(f"⚠️ OpenRouter failed: {e1}")
        try:
            print("🔁 Trying Gemini fallback...")
            return summarize_with_gemini(text)
        except Exception as e2:
            print(f"Gemini also failed: {e2}")
            return "⚠️ Resume summarization failed from both models."
