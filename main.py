import sys
import json
import io
import os
import contextlib

# ✅ Force stdout to UTF-8 (still needed)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ✅ Import your chatbot modules
from career_guide_chatbot import guide_career_decision
from mock_interview_chatbot import (
    generate_mock_question,
    analyze_interview_answer,
    reset_mock_interview,
    calculate_final_result  # ✅ Now imported here
)
from chatbot_session import (
    append_message,
    format_conversation,
    reset_conversation,
    ensure_session_structure
)

def read_input_from_stdin():
    """Reads the full JSON input sent by Spring Boot via stdin."""
    try:
        input_data = sys.stdin.read()
        return json.loads(input_data)
    except Exception as e:
        return {"error": f"Failed to parse stdin input: {str(e)}"}

def process_request():
    if len(sys.argv) < 2:
        return {"error": "Usage: python main.py <mode>"}

    mode = sys.argv[1]
    payload = read_input_from_stdin()

    try:
        if mode == "decide-role":
            user_id = payload.get("user_id")
            user_message = payload.get("user_message")
            resume_data = payload.get("resume_data")

            if not user_id or not user_message:
                raise ValueError("Missing 'user_id' or 'user_message' in payload.")

            if user_message.strip().lower() in ["reset", "restart"]:
                reset_conversation(user_id)
                return {"response": "Career guidance session reset."}

            ensure_session_structure(user_id)
            append_message(user_id, "User", user_message)
            history = format_conversation(user_id)
            ai_reply = guide_career_decision(history, user_message, resume_data)
            append_message(user_id, "AI", ai_reply)
            return {"response": ai_reply}

        elif mode == "get-question":
            user_id = payload.get("user_id", "default")
            resume_summary = payload.get("resume_summary")
            target_role = payload.get("target_role")
            last_answer = payload.get("last_answer", "")

            if not resume_summary or not target_role:
                raise ValueError("Missing 'resume_summary' or 'target_role' in payload.")

            question = generate_mock_question(resume_summary, target_role, last_answer, user_id)
            return {"question": question}

        elif mode == "score-answer":
            answer = payload.get("answer")
            target_role = payload.get("target_role")
            user_id = payload.get("user_id", "default")

            if not answer or not target_role:
                raise ValueError("Missing 'answer' or 'target_role' in payload.")

            result = analyze_interview_answer(answer, target_role, user_id)
            return result

        elif mode == "get-final-result":
            user_id = payload.get("user_id", "default")
            result = calculate_final_result(user_id)
            return {"result": result}

        elif mode == "reset-interview":
            user_id = payload.get("user_id", "default")
            reset_mock_interview(user_id)
            return {"response": "Mock interview session reset."}

        else:
            return {"error": f"Invalid mode: {mode}"}

    except Exception as e:
        return {"error": str(e)}

def main():
    # ✅ Suppress all other internal prints
    with contextlib.redirect_stdout(io.StringIO()):
        response = process_request()

    # ✅ Now print only the clean JSON once
    print(json.dumps(response, ensure_ascii=False))

if __name__ == "__main__":
    main()
