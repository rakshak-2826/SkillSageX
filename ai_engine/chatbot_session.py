import json
import redis

# ✅ Setup Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# ✅ Redis key pattern
def get_session_key(user_id: str):
    return f"career_chat:{user_id}"

# ✅ Ensure session structure exists (optional in Redis)
def ensure_session_structure(user_id: str):
    key = get_session_key(user_id)
    if not redis_client.exists(key):
        save_conversation(user_id, [])

# ✅ Load conversation from Redis
def load_conversation(user_id: str):
    key = get_session_key(user_id)
    data_json = redis_client.get(key)
    if data_json:
        try:
            data = json.loads(data_json)
            if isinstance(data, dict) and "conversation" in data:
                return data
            elif isinstance(data, list):  # old format fallback
                return {"conversation": data}
        except Exception as e:
            print(f"⚠️ Error decoding JSON from Redis: {e}")
    return {"conversation": []}

# ✅ Save conversation to Redis
def save_conversation(user_id: str, history: list):
    key = get_session_key(user_id)
    redis_client.set(key, json.dumps({"conversation": history}))

# ✅ Append new message to conversation
def append_message(user_id: str, sender: str, message: str):
    data = load_conversation(user_id)
    if "conversation" not in data or not isinstance(data["conversation"], list):
        data["conversation"] = []
    data["conversation"].append({"sender": sender, "text": message})
    save_conversation(user_id, data["conversation"])

# ✅ Reset conversation
def reset_conversation(user_id: str):
    save_conversation(user_id, [])

# ✅ Format conversation history into a prompt string
def format_conversation(user_id: str) -> str:
    data = load_conversation(user_id)
    return "\n".join([f"{msg['sender']}: {msg['text']}" for msg in data["conversation"]])
