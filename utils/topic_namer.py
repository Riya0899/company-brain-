from openai import OpenAI
from dotenv import load_dotenv
import os
import time

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

MODEL = "openrouter/free"

def generate_topic_name(sample_chunks, retries=3):
    context = "\n".join(sample_chunks[:3])
    prompt = f"""
    The following text chunks belong to the same topic.
    Give a short topic name (2-4 words only).

    chunks:
    {context}

    Topic Name:
    """

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            if "429" in str(e):
                wait = 30 * (attempt + 1)  # 30s, 60s, 90s
                print(f"Rate limited. Waiting {wait}s before retry...")
                time.sleep(wait)
            else:
                raise e

    return "General Topic"  # fallback if all retries fail