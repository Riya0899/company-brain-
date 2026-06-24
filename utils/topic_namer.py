from groq import Groq
from dotenv import load_dotenv
import os
import time  # it will pause the program when rate limit exceeds

load_dotenv()  # load the value to memory

client = Groq(api_key=os.getenv("GROQ_API_KEY")) # groq is creating the connection

MODEL = "llama-3.3-70b-versatile"


def generate_topic_name(sample_chunks, retries=3):  # retries means if something fails it will try upto three times
    context = "\n".join(sample_chunks[:3]) # takes first three chunks
    prompt = f"""
    The following text chunks belong to the same topic.
    Give a short topic name (2-4 words only). Reply with the topic name only — no explanation, no punctuation.
    Give a short topic name (2-4 words only). Reply with the topic name only — no explanation, no punctuation.

    chunks:
    {context}

    Topic Name:
    """

    for attempt in range(retries):
        try:
            response = client.chat.completions.create( # api call happens
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,  # creativity
                max_tokens=20,  #Limits response length
            )
            return response.choices[0].message.content.strip()


        except Exception as e:
            error_msg = str(e)
            # Groq rate-limit is 429
            if "429" in error_msg or "rate_limit" in error_msg.lower():
                wait = 30 * (attempt + 1)   # 30 s, 60 s, 90 s
                print(f"Rate limited. Waiting {wait}s before retry {attempt + 1}/{retries}...")
                time.sleep(wait)
            else:
                raise e

    return "General Topic"   # fallback if all retries fail
    return "General Topic"   # fallback if all retries fail