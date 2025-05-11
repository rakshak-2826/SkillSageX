import json
from utils.config import SKILL_MAP_PATH, logger

def load_skill_map() -> dict:
    """
    Loads the role-to-skill mapping from skill_map.json.
    """
    try:
        with open(SKILL_MAP_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        logger.error(f"❌ Failed to load skill_map.json: {str(e)}")
        return {}
