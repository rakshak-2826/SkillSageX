import os
import requests
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Caches
prerequisite_cache: Dict[str, List[str]] = {}
description_cache: Dict[str, str] = {}

# ------------------ Prerequisite Fetching ------------------ #

def fetch_prerequisites_openrouter(skill: str) -> List[str]:
    prompt = f"What are 2–3 prerequisite skills or technologies required to learn {skill}? Return only a comma-separated list."
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://chat.openai.com",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful AI that lists prerequisite technologies."},
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    response.raise_for_status()
    text = response.json()["choices"][0]["message"]["content"]
    return [s.strip() for s in text.split(",") if s.strip()]

def fetch_prerequisites_gemini(skill: str) -> List[str]:
    prompt = f"What are 2–3 prerequisite skills or technologies required to learn {skill}? Return only a comma-separated list."
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    payload = { "contents": [{ "parts": [{ "text": prompt }] }] }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
    return [s.strip() for s in text.split(",") if s.strip()]

def get_prerequisites(skill: str) -> List[str]:
    if skill in prerequisite_cache:
        return prerequisite_cache[skill]
    try:
        prereqs = fetch_prerequisites_openrouter(skill)
    except Exception as e:
        print(f"⚠️ OpenRouter failed for {skill}: {e}")
        try:
            prereqs = fetch_prerequisites_gemini(skill)
        except Exception as ge:
            print(f"❌ Gemini also failed for {skill}: {ge}")
            prereqs = []
    prerequisite_cache[skill] = prereqs
    return prereqs

# ------------------ Description Fetching ------------------ #

def fetch_description_openrouter(skill: str) -> str:
    prompt = f"Give a short 1-2 sentence professional description of the skill: {skill}"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://chat.openai.com",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You describe technical skills briefly."},
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()

def fetch_description_gemini(skill: str) -> str:
    prompt = f"Give a short 1-2 sentence professional description of the skill: {skill}"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    payload = { "contents": [{ "parts": [{ "text": prompt }] }] }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()

def get_description(skill: str) -> str:
    if skill in description_cache:
        return description_cache[skill]
    try:
        desc = fetch_description_openrouter(skill)
    except Exception as e:
        print(f"⚠️ OpenRouter description failed for {skill}: {e}")
        try:
            desc = fetch_description_gemini(skill)
        except Exception as ge:
            print(f"❌ Gemini description also failed for {skill}: {ge}")
            desc = "No description available."
    description_cache[skill] = desc
    return desc

# ------------------ Graph Builder ------------------ #

def build_graph_nodes_and_edges(matched: List[str], missing: List[str]) -> Dict:
    """
    Builds skill roadmap graph from both matched + missing skills.
    - Nodes: all matched and missing skills.
    - Edges: dynamic API-based prerequisites.
    - Colors: green for matched, red for missing.
    - Tooltip: short description of each skill.
    """
    all_skills = sorted(set(matched + missing))
    nodes = []
    edges = []

    for skill in all_skills:
        print(f"🔍 Fetching metadata for: {skill}")
        desc = get_description(skill)
        color = "#22c55e" if skill in matched else "#ef4444"
        nodes.append({
            "id": skill,
            "label": skill,
            "description": desc,
            "color": color
        })

    for skill in all_skills:
        prereqs = get_prerequisites(skill)
        for prereq in prereqs:
            match = next((s for s in all_skills if s.lower() == prereq.lower()), None)
            if match:
                edges.append({
                    "from": match,
                    "to": skill
                })

    return {
        "nodes": nodes,
        "edges": edges
    }
