import json
from mock_interview_chatbot import (
    generate_mock_question,
    analyze_interview_answer,
    reset_mock_interview
)

# ----------------------------
# 🔧 Configuration
# ----------------------------
USER_ID = "rakshak123"
TARGET_ROLE = "Full Stack Developer"
RESUME_SUMMARY = """
Rakshak Datta is a Full Stack Developer proficient in HTML, CSS, JavaScript, and React,
with experience in responsive UI, backend (Node.js, Express), MongoDB, and real-world projects like chat apps and EEG signal processing.
"""
NUM_QUESTIONS = 10
RESULT_FILE = f"interview_result_{USER_ID}.json"

# ----------------------------
# 🚀 Main Logic
# ----------------------------
def run_interview():
    print(f"🧠 Starting mock interview for: {TARGET_ROLE}\n")
    reset_mock_interview(USER_ID)
    results = []

    for i in range(NUM_QUESTIONS):
        print(f"\n👉 Question {i + 1}/{NUM_QUESTIONS}")
        question = generate_mock_question(RESUME_SUMMARY, TARGET_ROLE, user_id=USER_ID)

        if not question.strip():
            print("⚠️ Failed to generate a question. Skipping.")
            continue

        print(f"💬 {question}")
        answer = input("🗣️  Your answer: ").strip()

        if not answer:
            print("⚠️ Skipping blank answer.")
            continue

        score_result = analyze_interview_answer(answer, TARGET_ROLE)
        print(f"📊 Evaluation:\n{score_result['evaluation']}\n")

        results.append({
            "question": question,
            "answer": answer,
            "evaluation": score_result["evaluation"]
        })

    # ----------------------------
    # 💾 Save Results
    # ----------------------------
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Saved interview results to {RESULT_FILE}")

    # ----------------------------
    # 🧮 Final Verdict
    # ----------------------------
    total_score = 0
    valid_scores = 0

    for item in results:
        try:
            lines = item["evaluation"].splitlines()
            for line in lines:
                if "Overall role fit" in line:
                    percent = int(line.split("(")[-1].replace(")", "").replace("%", "").strip())
                    total_score += percent
                    valid_scores += 1
                    break
        except Exception:
            continue

    if valid_scores == 0:
        print("⚠️ No valid scores found.")
        return

    avg_score = total_score / valid_scores
    print(f"\n✅ Final Average Role Fit Score: {avg_score:.2f}%")

    if avg_score >= 80:
        print("🎉 Result: You would likely clear the interview!")
    else:
        print("❌ Result: You may need more preparation. Keep practicing!")

# ----------------------------
# ▶️ Entry Point
# ----------------------------
if __name__ == "__main__":
    run_interview()
