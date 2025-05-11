import spacy
from sentence_transformers import SentenceTransformer, util
from typing import Dict
from utils.config import CUSTOM_MODEL_PATH, logger
from utils.nlp_utils import extract_named_entities

# ---------- Load models only once ----------
model = SentenceTransformer("all-MiniLM-L6-v2")
nlp = spacy.load(CUSTOM_MODEL_PATH)

# ---------- Skill extraction from custom model ----------
def get_skills(text: str) -> set:
    return set(s.lower() for s in extract_named_entities(text).get("detected_skills", []))


# ---------- Embedding-based similarity ----------
def compare_embeddings(text1: str, text2: str) -> float:
    emb1 = model.encode(text1, convert_to_tensor=True)
    emb2 = model.encode(text2, convert_to_tensor=True)
    score = util.cos_sim(emb1, emb2).item()
    return round(score * 100, 2)


# ---------- Resume vs JD Comparison ----------
def analyze_resume_vs_jd_text(resume_text: str, jd_text: str) -> Dict:
    logger.info("🔍 Running in-memory resume vs JD comparison...")

    # Compute overall text similarity
    full_text_similarity = compare_embeddings(resume_text, jd_text)

    # Extract skills from both
    resume_skills = get_skills(resume_text)
    jd_skills = get_skills(jd_text)

    matched_skills = sorted(resume_skills & jd_skills)
    missing_skills = sorted(jd_skills - resume_skills)
    skill_similarity = round(len(matched_skills) / len(jd_skills) * 100, 2) if jd_skills else 0.0

    return {
        "full_text_similarity": full_text_similarity,
        "skill_similarity": skill_similarity,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }
