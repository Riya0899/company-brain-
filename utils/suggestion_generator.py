"""
suggestion_generator.py
-----------------------
Generates smart, document-aware question suggestions from PDF chunks
or URL-fetched content using Groq.

Two modes:
  1. generate_suggestions()       — called once at upload time (initial chips)
  2. generate_followup_suggestions() — called after each AI answer (contextual chips)
"""

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
    """
    Given a list of text chunks from a PDF or web page, return up to `n`
    natural questions a user might want to ask about that source.

    Parameters
    ----------
    chunks       : list of text chunks from the source
    n            : number of suggestions to generate
    source_label : human-readable label for the source

    Returns a plain list of question strings.
    """
    if len(chunks) <= 6:
        sample = chunks
    else:
        step = len(chunks) // 6
        sample = [chunks[i] for i in range(0, len(chunks), step)][:6]

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
            temperature=0.7,
            max_tokens=512,
        )
        raw = response.choices[0].message.content.strip()

        questions = []
        for line in raw.splitlines():
            line = line.strip()
            if not line or len(line) < 10:
                continue
            line = re.sub(r"^[\d\.\-\*\•]+\s*", "", line).strip()
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
    """
    Generate contextual follow-up question suggestions based on the most
    recent Q&A exchange. Called after every assistant response so the user
    always has relevant next steps to click.

    Parameters
    ----------
    last_question : the user's most recent question
    last_answer   : the assistant's most recent answer
    topic_name    : detected topic cluster name (optional, adds context)
    n             : number of follow-up suggestions to generate

    Returns a plain list of question strings (up to `n`).
    """
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