from groq import Groq
from dotenv import load_dotenv
import os
import db

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
SUMMARY_MODEL = "llama-3.1-8b-instant"   # cheap model, this is just background bookkeeping
RECENT_LIMIT = 6

SUMMARY_SYSTEM_PROMPT = """You maintain a running summary of an ongoing conversation between a user and an AI assistant.
Rules:
1. Update the existing summary by folding in the new messages shown below.
2. Keep it concise: 4-8 sentences max, focused on topics discussed, decisions made, and anything the user said they care about.
3. Do not include commentary about the summarization process itself — output only the updated summary."""


def get_recent_chat(messages, limit=RECENT_LIMIT):
    history = []
    for message in messages[-limit:]:
        role = message['role']
        content = message['content']
        history.append(f"{role}:{content}")
    return "\n".join(history)


def _summarize(old_summary: str, new_messages: list[dict]) -> str:
    convo_text = "\n".join(f"{m['role']}: {m['content']}" for m in new_messages)
    prompt = f"""Existing summary so far:
{old_summary or '(none yet)'}

New messages to fold in:
{convo_text}

Write the updated summary:
"""
    try:
        response = client.chat.completions.create(
            model=SUMMARY_MODEL,
            messages=[
                {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=250,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Conversation summarization failed: {e}")
        return old_summary  # fail safe — keep the old summary rather than losing memory


def get_conversation_context(messages, limit=RECENT_LIMIT) -> str:
    """Returns a running summary of everything before the recent window, plus the
    recent messages verbatim — lets the model 'remember' far back into a long
    conversation without resending hundreds of messages every single call."""
    total = len(messages)
    older_cutoff = max(0, total - limit)

    state = db.get_chat_memory()
    summarized_count = state["summarized_count"]
    old_summary = state["summary"]

    if older_cutoff > summarized_count:
        new_older_messages = messages[summarized_count:older_cutoff]
        if new_older_messages:
            old_summary = _summarize(old_summary, new_older_messages)
            db.save_chat_memory(old_summary, older_cutoff)

    recent = get_recent_chat(messages, limit=limit)
    if old_summary:
        return f"Summary of earlier conversation:\n{old_summary}\n\nRecent messages:\n{recent}"
    return recent