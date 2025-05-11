import os
import asyncio
import json
from utils.config import logger

# GPTQ CLI script path
GPTQ_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gptq_api.py")

# Local skill-wise cache directory
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# ---------------------
# Cache helpers
# ---------------------
def load_from_cache(skill: str, mode: str):
    path = os.path.join(CACHE_DIR, f"{skill.replace(' ', '_').lower()}_{mode}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_to_cache(skill: str, mode: str, data):
    path = os.path.join(CACHE_DIR, f"{skill.replace(' ', '_').lower()}_{mode}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ---------------------
# GPTQ subprocess runner
# ---------------------
async def run_gptq(mode: str, skill: str, max_tokens: int = 100) -> str:
    try:
        cmd = ["python3", GPTQ_SCRIPT, skill, str(max_tokens if mode == "learning" else 100)]
        if mode == "projects":
            cmd.append("project_idea")
        else:
            cmd.append("learning_path")
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if stderr:
            logger.warning(f"⚠️ GPTQ stderr: {stderr.decode()}")
        response = json.loads(stdout.decode())
        return response.get("response", "")
    except Exception as e:
        logger.error(f"❌ GPTQ generation failed for {skill} ({mode}): {e}")
        return ""

# ---------------------
# Public async methods
# ---------------------
async def generate_learning_path(skill: str) -> str:
    cached = load_from_cache(skill, "learning")
    if cached:
        return cached
    result = await run_gptq("learning", skill, max_tokens=60)
    if result:
        save_to_cache(skill, "learning", result)
    return result

async def generate_project_ideas(skill: str, min_ideas: int = 3) -> list:
    cached = load_from_cache(skill, "projects")
    if cached:
        return cached
    result = await run_gptq("projects", skill, max_tokens=100)
    ideas = result.split('\n')
    ideas = [line.strip('-•123. ').strip() for line in ideas if len(line.strip()) > 4]
    if ideas:
        ideas = ideas[:min_ideas]
        save_to_cache(skill, "projects", ideas)
    return ideas
