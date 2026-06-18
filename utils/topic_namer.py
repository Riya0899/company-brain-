from groq import Groq
from dotenv import load_dotenv
import os
import time

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "llama-3.3-70b-versatile"


def generate_topic_name(sample_chunks, retries=3):
    context = "\n".join(sample_chunks[:3])
    prompt = f"""
    The following text chunks belong to the same topic.
    Give a short topic name (2-4 words only). Reply with the topic name only — no explanation, no punctuation.

    chunks:
    {context}

    Topic Name:
    """

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=20,   # topic name is short — no need for more
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            error_msg = str(e)
            # Groq rate-limit is 429, same as OpenRouter
            if "429" in error_msg or "rate_limit" in error_msg.lower():
                wait = 30 * (attempt + 1)   # 30 s, 60 s, 90 s
                print(f"Rate limited. Waiting {wait}s before retry {attempt + 1}/{retries}...")
                time.sleep(wait)
            else:
                raise e

    return "General Topic"   # fallback if all retries fail