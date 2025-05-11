import os
import sys
import json
import asyncio
from typing import Optional

sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # Ensure local imports

from utils.config import logger
from utils.text_extraction import extract_text
from utils.summarizer import summarize_resume
from utils.nlp_utils import extract_named_entities
from utils.utils import load_skill_map
from utils.comparator import calculate_fit_score
from utils.graph_builder import build_graph_nodes_and_edges
from utils.role_suggestor import detect_role_from_jd, get_alternate_roles_with_descriptions
from utils.learning_project_generator import generate_learning_and_projects


async def generate_recommendations(resume_text: str, jd_text: Optional[str] = None, goal: Optional[str] = None):
    skill_map = load_skill_map()
    summary = summarize_resume(resume_text)

    # 🧠 Detect goal if not provided
    if not goal and jd_text:
        logger.info("No role provided. Detecting role from JD...")
        goal = detect_role_from_jd(jd_text, skill_map)
    elif not goal:
        logger.warning("Neither role nor JD provided. Cannot proceed.")
        return {"error": "Please provide either a target role or a job description."}

    goal_data = skill_map.get(goal)
    if not goal_data:
        return {"error": f"Role '{goal}' not found in skill map."}

    # 📊 Extract skill data from goal
    must_have = goal_data.get("must_have", [])
    optional = goal_data.get("optional", [])
    role_skills = set(must_have + optional)

    # 📥 Extract JD skills via NER (if JD provided)
    jd_skills = set()
    if jd_text:
        jd_ner = extract_named_entities(jd_text)
        jd_skills = set(s.lower() for s in jd_ner.get("detected_skills", []))

    # Combine goal and JD skills
    combined_required_skills = set(s.lower() for s in role_skills.union(jd_skills))

    # 📥 Resume skill extraction via custom NER
    ner_results = extract_named_entities(resume_text)
    resume_skills = set(s.lower() for s in ner_results.get("detected_skills", []))

    matched_skills = sorted(list(resume_skills & combined_required_skills))
    missing_skills = sorted(list(combined_required_skills - resume_skills))
    optional_missing = sorted(list(set(s.lower() for s in optional) - resume_skills))
    recommended_skills = sorted(set(missing_skills + optional_missing))

    # 🔄 Generate learning paths and project ideas
    learning_path = []
    project_ideas = {}

    for skill in recommended_skills:
        logger.info(f"Generating learning path and project ideas for: {skill}")
        try:
            result = generate_learning_and_projects(skill)
            if not result or not isinstance(result, dict):
                logger.warning(f"⚠️ Invalid or empty result for {skill}")
                continue

            lp = result.get("learning_path", [])
            pi = result.get("project_ideas", [])

            if lp:
                learning_path.append({
                    "skill": skill,
                    "steps": lp
                })
            if pi:
                project_ideas[skill] = pi[:3]

        except Exception as e:
            logger.warning(f"❌ Failed to generate content for {skill}: {e}")

    # 🧠 Final response
    fit_score = calculate_fit_score(list(resume_skills), must_have)
    graph = build_graph_nodes_and_edges(matched_skills, missing_skills)
    alternate_roles = get_alternate_roles_with_descriptions(summary, goal, skill_map)

    return {
        "goal": goal,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "optional_missing": optional_missing,
        "recommended_skills": recommended_skills,
        "learning_path": learning_path,
        "project_ideas": project_ideas,
        "fit_score": fit_score,
        "graph": graph,
        "job_skills": sorted(list(jd_skills)) if jd_text else None,
        "ner_results": ner_results,
        "resume_summary": summary,
        "alternate_roles": [
            {"role": role, "score": score, "description": description}
            for (role, score, description) in alternate_roles
        ],
        "name": ner_results.get("name", []),
        "education": ner_results.get("education", []),
        "certifications": ner_results.get("certifications", [])
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Usage: python skill_graph.py <resume_path> [<goal>] [<jd_path>]")
        sys.exit(1)

    resume_path = sys.argv[1]
    goal = sys.argv[2] if len(sys.argv) > 2 else None
    jd_path = sys.argv[3] if len(sys.argv) > 3 else None

    resume_text = extract_text(resume_path)
    if not resume_text.strip():
        logger.error("Resume is empty or unreadable.")
        sys.exit("❌ Error: Resume file is empty or invalid.")

    jd_text = extract_text(jd_path) if jd_path else None

    result = asyncio.run(generate_recommendations(resume_text, jd_text, goal))
    sys.stdout.buffer.write(json.dumps(result, indent=2, ensure_ascii=False).encode("utf-8"))
