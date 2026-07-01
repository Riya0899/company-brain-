from groq import Groq
from dotenv import load_dotenv
import os #to access environment variables
import re

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


def generate_suggestions(
    chunks: list[str],
    n: int = 8,
    source_label: str = "document",
) -> list[str]:
    if len(chunks) <= 6:
        sample = chunks
    else:
        step = len(chunks) // 6
        sample = [chunks[i] for i in range(0, len(chunks), step)][:6] #avoids token overload

    context = "\n\n---\n\n".join(sample)

    prompt = f"""
You are reading excerpts from a {source_label}. Based ONLY on the content below,
generate exactly {n} specific, useful questions that a user might ask about this source.

Rules:
- Questions must be directly answerable from this content
- Be specific — mention actual topics, names, processes, or figures found in the text
- Do NOT generate generic questions like "What is this document about?"
- Each question on its own line
- No numbering, no bullets, no extra text — just the questions

Content excerpts:
{context}

Generate {n} questions:
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7, #balanced creativity
            max_tokens=512, #max answer size
        )
        raw = response.choices[0].message.content.strip() #extract response

        questions = []
        for line in raw.splitlines():
            line = line.strip()
            if not line or len(line) < 10:
                continue
            line = re.sub(r"^[\d\.\-\*\•]+\s*", "", line).strip() #Removes prefixes
            if line:
                questions.append(line)

        return questions[:n]

    except Exception as e:
        print(f"Suggestion generation failed: {e}")
        return []


def generate_followup_suggestions(
    last_question: str,
    last_answer: str,
    topic_name: str = "",
    n: int = 3,
) -> list[str]:
 
    topic_hint = f" The topic cluster detected was: '{topic_name}'." if topic_name else ""

    prompt = f"""
You are a helpful assistant. A user just had this exchange with an AI knowledge base:{topic_hint}

User question: {last_question}

AI answer: {last_answer}

Based on this exchange, generate exactly {n} short, specific follow-up questions
the user would naturally want to ask next to dig deeper or explore related aspects.

Rules:
- Each question must logically follow from the answer above
- Be specific — reference actual content from the answer (names, figures, processes)
- Do NOT repeat the original question or rephrase it
- No numbering, no bullets, no extra text — just the questions, one per line
- Keep each question under 15 words

Generate {n} follow-up questions:
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=256,
        )
        raw = response.choices[0].message.content.strip()

        questions = []
        for line in raw.splitlines():
            line = line.strip()
            if not line or len(line) < 8:
                continue
            line = re.sub(r"^[\d\.\-\*\•]+\s*", "", line).strip()
            if line:
                questions.append(line)

        return questions[:n]

    except Exception as e:
        print(f"Follow-up suggestion generation failed: {e}")
        return []
    