import os
import sys
import json
import requests
import random
from time import sleep
from dotenv import load_dotenv

# ✅ Ensure UTF-8 output (for Windows terminals)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ✅ Load API keys from .env
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ✅ Cache directory setup
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", ".cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# ✅ API rotation logic
api_sequence = ["openrouter", "gemini"]
rotation_counter = {api: 0 for api in api_sequence}
ROTATE_AFTER = random.randint(10, 15)  # change after every 10–15 requests

# -------------------------
# 📁 Cache Helpers
# -------------------------
def get_skill_folder(skill: str) -> str:
    return os.path.join(CACHE_DIR, skill.replace(" ", "_").lower())

def load_from_cache(skill: str, mode: str):
    folder = get_skill_folder(skill)
    file_path = os.path.join(folder, f"{mode}.json")
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Corrupted cache for {skill}: {e}")
    return None

def save_to_cache(skill: str, mode: str, data):
    folder = get_skill_folder(skill)
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f"{mode}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# -------------------------
# ✍️ Prompt Template
# -------------------------
def build_prompt(skill: str):
    return f"""
Skill: {skill}

Provide a clear 3-step learning path and 3 realistic project ideas.

Format:
Learning Path:
- Step 1...
- Step 2...
- Step 3...

Project Ideas:
- Idea 1...
- Idea 2...
- Idea 3...
"""

# -------------------------
# 🔌 API Calls
# -------------------------
def call_openrouter(prompt: str):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://chat.openai.com",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are an expert career guide AI."},
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def call_gemini(prompt: str):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]

# -------------------------
# 🧠 Smart API Router
# -------------------------
def smart_generate(prompt: str):
    global api_sequence, rotation_counter

    for i in range(len(api_sequence)):
        api = api_sequence[i]
        try:
            print(f"⚙️ Trying {api} GPT...")
            if api == "openrouter":
                result = call_openrouter(prompt)
            elif api == "gemini":
                result = call_gemini(prompt)
            else:
                raise ValueError("Unknown API in sequence")

            # ✅ Successful
            rotation_counter[api] += 1
            if rotation_counter[api] >= ROTATE_AFTER:
                api_sequence.append(api_sequence.pop(0))
                rotation_counter[api] = 0

            return result

        except Exception as e:
            print(f"[{api.upper()}] ❌ Error: {e}")
            sleep(1)
            continue

    return None

# -------------------------
# 🧹 Parse Result
# -------------------------
def parse_learning_and_projects(text: str):
    lp = []
    pi = []
    section = None

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.lower().startswith("learning path"):
            section = "lp"
        elif line.lower().startswith("project ideas"):
            section = "pi"
        elif line.startswith("-") or line[:2].isdigit():
            content = line.lstrip("-•0123456789. ").strip()
            if section == "lp" and len(content) > 4:
                lp.append(content)
            elif section == "pi" and len(content) > 4:
                pi.append(content)

    return lp[:3], pi[:3]

# -------------------------
# 🚀 Main Skill Handler
# -------------------------
def generate_learning_and_projects(skill: str):
    folder = get_skill_folder(skill)
    cache = load_from_cache(skill, "learning_and_projects")

    if cache:
        if isinstance(cache, dict) and "learning_path" in cache and "project_ideas" in cache:
            if cache["learning_path"] or cache["project_ideas"]:
                print(f"⚠️ Skipping {skill} — already generated.")
                return cache
            else:
                print(f"⚠️ Invalid or empty result for {skill}")
        else:
            print(f"⚠️ Corrupted or old cache format for {skill}")

    prompt = build_prompt(skill)
    text_result = smart_generate(prompt)

    if not text_result or len(text_result.strip()) < 30:
        print(f"❌ Failed to generate valid output for {skill}")
        return None

    learning, projects = parse_learning_and_projects(text_result)
    if not learning and not projects:
        print(f"⚠️ No valid learning path or project ideas found for {skill}")
        return None

    result = {
        "skill": skill,
        "learning_path": learning,
        "project_ideas": projects
    }

    save_to_cache(skill, "learning_and_projects", result)
    return result

# -------------------------
# 🧪 CLI Test
# -------------------------
if __name__ == "__main__":
    skill = input("🔍 Enter a skill: ").strip()
    output = generate_learning_and_projects(skill)
    print("\n✅ OUTPUT:\n", json.dumps(output, indent=2, ensure_ascii=False))
