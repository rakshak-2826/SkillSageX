import os
import logging
from dotenv import load_dotenv

# ---------- Load .env configuration ----------
load_dotenv()

# ---------- Base directory (project root) ----------
# Go up one level from /utils/ to /career-guidance-py/
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# ---------- Path Constants ----------
CUSTOM_MODEL_PATH = os.path.join(BASE_DIR, "output", "model-best")
SKILL_MAP_PATH = os.path.join(BASE_DIR, "skill_map.json")
HF_API_KEY = os.getenv("HF_API_KEY", "").strip()

# ---------- Logger Setup ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("skill_graph")

# ---------- Hugging Face API Key Check ----------
if not HF_API_KEY:
    logger.warning("⚠️ Hugging Face API key (HF_API_KEY) not found in .env. Summarization will fail.")
