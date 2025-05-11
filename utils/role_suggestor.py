from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer, util
import os
import requests

# Load model once
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load API keys from environment
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Temporary in-memory cache (can be replaced with Redis or DB)
role_description_cache: Dict[str, str] = {}


def detect_role_from_jd(jd_text: str, skill_map: Dict[str, Dict]) -> str:
    role_names = list(skill_map.keys())
    role_embeddings = model.encode(role_names, convert_to_tensor=True)
    jd_embedding = model.encode(jd_text, convert_to_tensor=True)

    scores = util.cos_sim(jd_embedding, role_embeddings)[0]
    ranked_roles = sorted(zip(role_names, scores), key=lambda x: x[1], reverse=True)

    return ranked_roles[0][0]


def get_alternate_roles(user_summary: str, current_role: str, skill_map: Dict[str, Dict], top_n: int = 3) -> List[Tuple[str, float]]:
    role_names = list(skill_map.keys())
    role_embeddings = model.encode(role_names, convert_to_tensor=True)
    user_embedding = model.encode(user_summary, convert_to_tensor=True)

    scores = util.cos_sim(user_embedding, role_embeddings)[0]
    ranked_roles = sorted(zip(role_names, scores), key=lambda x: x[1], reverse=True)

    suggestions = [
        (role, round(score.item() * 100, 2))
        for role, score in ranked_roles if role != current_role
    ]

    return suggestions[:top_n]


# --- Description Fetching Utilities ---

def get_role_description(role: str) -> str:
    """
    Returns a description of the role using OpenRouter or Gemini fallback.
    """
    # Check cache
    if role in role_description_cache:
        return role_description_cache[role]

    prompt = f"Give a short, 2-3 sentence professional description of the job role: {role}"

    try:
        description = fetch_from_openrouter(prompt)
    except Exception as e:
        print(f"[OpenRouter failed] {e}")
        try:
            description = fetch_from_gemini(prompt)
        except Exception as ge:
            print(f"[Gemini fallback failed] {ge}")
            description = "No description available at the moment."

    # Cache it
    role_description_cache[role] = description
    return description


def fetch_from_openrouter(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://chat.openai.com",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are an AI that describes job roles professionally."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()


def fetch_from_gemini(prompt: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()


# --- Combined Output Function ---

def get_alternate_roles_with_descriptions(user_summary: str, current_role: str, skill_map: Dict[str, Dict], top_n: int = 3) -> List[Tuple[str, float, str]]:
    roles = get_alternate_roles(user_summary, current_role, skill_map)
    enriched = []

    for role, score in roles:
        description = get_role_description(role)
        enriched.append((role, score, description))

    return enriched
