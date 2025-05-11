from ollama_client import call_ollama

def guide_career_decision(conversation_history: str, user_message: str, resume_data: dict = None) -> str:
    print("\n🛠 [guide_career_decision] Building prompt...")

    # ✅ Prepare resume context only once if needed
    resume_context = ""
    if resume_data:
        goal = resume_data.get('goal', 'N/A')
        fit_score = resume_data.get('fit_score', 'N/A')
        alt_roles = resume_data.get('alternate_roles', [])

        resume_context += f"\nTarget Role: {goal}"
        resume_context += f"\nFit Score: {fit_score}%"
        if alt_roles:
            resume_context += "\nAlternate Role Suggestions:\n"
            for entry in alt_roles:
                role = entry.get("role", "Unknown")
                score = entry.get("score", "N/A")
                resume_context += f"- {role} ({score}%)\n"

    # ✅ Detect if it's a new conversation
    is_first_message = conversation_history.strip() == ""

    if is_first_message:
        intro_message = "You are a friendly AI career coach. This is the start of a new conversation with a user seeking career advice."
    else:
        intro_message = "You are continuing an ongoing career guidance chat. Use the conversation history only for background, but always focus on answering the user's latest question."

    # ✅ Build final prompt properly (insert actual variables)
    prompt = f"""
{intro_message}

Here is the user's background for your internal reference only:
{resume_context}

Here is the conversation history for background only:
{conversation_history}

Now, focus only on answering the user's latest question:
User: {user_message}

⚡ Important: Do not repeat the full resume details or background unless specifically asked. 
Base your suggestions (roles, learning paths, projects) on the user's latest needs. 
Be concise, natural, supportive, and professional.
"""

    print("\n✅ [guide_career_decision] Prompt built successfully. Sending to model...\n")

    # ✅ Send to model and get response
    reply = call_ollama(prompt, mode="career")

    print("\n✅ [guide_career_decision] Response received from model.\n")

    return reply
