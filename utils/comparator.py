from typing import List, Dict

def calculate_fit_score(resume_skills: List[str], must_have: List[str]) -> str:
    """
    Calculates how many must-have skills the resume covers as a percentage.
    Normalizes skill names to lowercase for reliable comparison.
    """
    if not must_have:
        return "0%"

    # Normalize and clean skill names
    resume_normalized = set(skill.strip().lower() for skill in resume_skills)
    must_have_normalized = set(skill.strip().lower() for skill in must_have)

    matched = resume_normalized & must_have_normalized
    score = round((len(matched) / len(must_have_normalized)) * 100)
    return f"{score}%"


def get_skill_gaps(resume_skills: List[str], must_have: List[str], optional: List[str]) -> Dict[str, List[str]]:
    """
    Returns:
    - missing must-have skills
    - missing optional skills
    - covered must-have skills
    All values are normalized for case-insensitive, consistent comparison.
    """
    resume_set = set(skill.strip().lower() for skill in resume_skills)
    must_have_set = set(skill.strip().lower() for skill in must_have)
    optional_set = set(skill.strip().lower() for skill in optional)

    return {
        "missing_skills": sorted(list(must_have_set - resume_set)),
        "optional_missing": sorted(list(optional_set - resume_set)),
        "covered": sorted(list(resume_set & must_have_set))
    }
