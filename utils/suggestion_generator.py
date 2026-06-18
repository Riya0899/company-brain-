"""
suggestion_generator.py
-----------------------
Generates smart, document-aware question suggestions from PDF chunks
or URL-fetched content using Groq. Called once per uploaded source during indexing.
"""

from groq import Groq
from dotenv import load_dotenv
import os
import re

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


def generate_suggestions(
    chunks: list[str],
    n: int = 8,
    source_label: str = "document",   # e.g. "PDF" or the URL/page title
) -> list[str]:
    """
    Given a list of text chunks from a PDF or web page, return up to `n`
    natural questions a user might want to ask about that source.

    Parameters
    ----------
    chunks       : list of text chunks from the source
    n            : number of suggestions to generate
    source_label : human-readable label for the source (used in the prompt
                   so the model knows whether it's reading a PDF or a web page)

    Returns a plain list of question strings.
    """
    # Sample a spread of chunks so we cover the whole document / page
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
            # Strip leading numbers/bullets just in case the model adds them
            line = re.sub(r"^[\d\.\-\*\•]+\s*", "", line).strip()
            if line:
                questions.append(line)

        return questions[:n]

    except Exception as e:
        print(f"Suggestion generation failed: {e}")
        return []