from ollama_client import call_ollama
import redis
import json
import re

# ✅ Setup Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# ✅ Redis key patterns
def get_mock_questions_key(user_id: str):
    return f"mock_questions:{user_id}"

def get_question_count_key(user_id: str):
    return f"mock_question_count:{user_id}"

def get_total_score_key(user_id: str):
    return f"mock_total_score:{user_id}"

# ✅ Load asked questions
def load_mock_questions(user_id: str):
    key = get_mock_questions_key(user_id)
    data_json = redis_client.get(key)
    if data_json:
        try:
            return json.loads(data_json)
        except Exception as e:
            print(f"Error loading mock questions JSON from Redis: {e}")
    return []

# ✅ Save asked questions
def save_mock_questions(user_id: str, questions: list):
    key = get_mock_questions_key(user_id)
    redis_client.set(key, json.dumps(questions))

# ✅ Load question count
def get_question_count(user_id: str) -> int:
    count = redis_client.get(get_question_count_key(user_id))
    return int(count) if count else 0

# ✅ Increment question count
def increment_question_count(user_id: str):
    redis_client.incr(get_question_count_key(user_id))

# ✅ Add to total role fit score
def add_to_total_score(user_id: str, role_fit_score: int):
    key = get_total_score_key(user_id)
    current = redis_client.get(key)
    total = int(current) if current else 0
    total += role_fit_score
    redis_client.set(key, total)

# ✅ Load total score
def get_total_score(user_id: str) -> int:
    score = redis_client.get(get_total_score_key(user_id))
    return int(score) if score else 0

# ✅ Reset all mock interview progress
def reset_mock_interview(user_id: str):
    redis_client.delete(get_mock_questions_key(user_id))
    redis_client.delete(get_question_count_key(user_id))
    redis_client.delete(get_total_score_key(user_id))

# ✅ Extract Role Fit Score from analysis text
def extract_role_fit_from_analysis(analysis_text: str) -> int:
    match = re.search(r'Role fit.*?(\d+)%', analysis_text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 0

# ✅ Generate a new interview question
def generate_mock_question(resume_summary: str, target_role: str, last_answer: str = "", user_id: str = "default") -> str:
    question_count = get_question_count(user_id)

    if question_count >= 10:
        return "✅ Mock Interview Completed. Please evaluate your overall performance."

    questions = load_mock_questions(user_id)
    previous = "\n".join(questions)

    prompt = f"""
You are an AI Interviewer for the role of a {target_role}.

Candidate Summary:
{resume_summary}

Their last answer (if any): "{last_answer}"

Already asked questions:
{previous if previous else "None"}

Please generate a new, unique technical or behavioral interview question (1 at a time) that:
- Is relevant for the role
- Is not repeated
- Tests either technical depth or thinking ability
- Is concise and clear

Return only the question, no extra commentary.
"""

    question = call_ollama(prompt, mode="question")

    # ✅ Save the new question
    questions.append(question.strip())
    save_mock_questions(user_id, questions)

    # ✅ Increment question count
    increment_question_count(user_id)

    return question.strip()

# ✅ Analyze interview answer
def analyze_interview_answer(answer: str, target_role: str, user_id: str) -> dict:
    prompt = f"""
You are an AI interviewer for the role of {target_role}.
Evaluate the candidate's answer to an interview question.

Answer:
{answer}

Rate on:
- Technical depth (0-10)
- Communication clarity (0-10)
- Confidence/professionalism (0-10)
- Overall role fit (0-100%)

Also, provide:
- Strengths of the answer
- Areas for improvement
- Final recommendation

Return the result in structured, readable format.
"""

    analysis = call_ollama(prompt, mode="score")

    # ✅ Extract Role Fit score and add to total
    role_fit_score = extract_role_fit_from_analysis(analysis)
    add_to_total_score(user_id, role_fit_score)

    return {
        "evaluation": analysis.strip()
    }

# ✅ Calculate final interview result
def calculate_final_result(user_id: str) -> str:
    total_score = get_total_score(user_id)
    if total_score == 0:
        return "❌ No scores found. Please complete the interview first."

    average = total_score / 10

    if average >= 80:
        return f"✅ Congratulations! You passed the mock interview with an average score of {average:.2f}%."
    else:
        return f"🔄 You scored an average of {average:.2f}%. Keep practicing and try harder next time!"
