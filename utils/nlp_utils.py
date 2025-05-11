import re
import spacy
from typing import List, Dict
from sentence_transformers import SentenceTransformer
from utils.config import CUSTOM_MODEL_PATH, logger

# ---------- Load NLP Models Once ----------
nlp_md = spacy.load("en_core_web_md")  # Used for sentence parsing
semantic_model = SentenceTransformer("all-MiniLM-L6-v2")  # Optional backup if needed

# Load your custom trained spaCy NER model
try:
    nlp_custom = spacy.load(CUSTOM_MODEL_PATH)
    logger.info(f"✅ Loaded custom spaCy model from: {CUSTOM_MODEL_PATH}")
except OSError:
    logger.error(f"❌ Failed to load custom spaCy model at: {CUSTOM_MODEL_PATH}")
    nlp_custom = None

# Optional alias normalization
ALIAS_MAP = {
    "react.js": "react",
    "postgres": "postgresql",
    "js": "javascript",
    "html5": "html",
    "css3": "css",
    "node": "node.js",
    "typescript": "type script",
    "vs code": "visual studio code"
}


def normalize_skill(skill: str) -> str:
    """Applies alias mapping and case normalization."""
    return ALIAS_MAP.get(skill.strip().lower(), skill.strip().lower())


def extract_named_entities(text: str) -> Dict[str, List[str]]:
    """
    Extracts named entities for skills, education, certifications, and name using spaCy NER.
    Also includes regex-based fallback for skills listed under 'Skills:' or 'Programming:'.
    """
    doc_md = nlp_md(text)
    doc_custom = nlp_custom(text) if nlp_custom else None

    skills, certs, education, names = [], [], [], []

    def is_valid_entity(ent_text: str) -> bool:
        ent_text = ent_text.strip().strip("•-•:,.\n\t ")
        if not ent_text or len(ent_text) < 2:
            return False
        if ent_text.lower() in {"skills", "objective", "summary"}:
            return False
        if ent_text.isdigit() or (any(char.isdigit() for char in ent_text) and len(ent_text) <= 5):
            return False
        return True

    all_ents = list(doc_md.ents)
    if doc_custom:
        all_ents += list(doc_custom.ents)

    for ent in all_ents:
        label = ent.label_.upper()
        ent_text = ent.text.strip().replace('\n', ' ').replace('\t', ' ').strip("•-•:,. ")
        if not is_valid_entity(ent_text):
            continue

        if label in {"SKILL", "TECH", "TOOL", "PRODUCT", "ORG", "FRAMEWORK"}:
            skills.append(ent_text)
        elif label in {"EDUCATION", "DEGREE", "SCHOOL", "INSTITUTE", "INSTITUTION"}:
            education.append(ent_text)
        elif "CERT" in label or "LICENSE" in label:
            certs.append(ent_text)
        elif label == "NAME":
            names.append(ent_text)

    # 🔁 Fallback: match comma-separated skill lines under 'Skills' or 'Programming'
    fallback_pattern = r"(Programming|Skills|Technologies)[^\n:]*[:\-]\s*(.+)"
    fallback_matches = re.findall(fallback_pattern, text, flags=re.IGNORECASE)

    for _, line in fallback_matches:
        items = [normalize_skill(s) for s in line.split(',')]
        for item in items:
            if is_valid_entity(item):
                skills.append(item)

    # Normalize and deduplicate
    skills = sorted(set(normalize_skill(s) for s in skills if is_valid_entity(s)))
    certs = sorted(set(certs))
    education = sorted(set(education))
    names = sorted(set(names))

    # ⚠️ Add warning if nothing meaningful was extracted
    if not skills and not education and not certs:
        logger.warning("⚠️ No entities extracted — model may be missing or resume formatting poor.")

    return {
        "detected_skills": skills,
        "certifications": certs,
        "education": education,
        "name": names
    }
