from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are a document summarization assistant.
Rules:
1. Summarize only what is present in the provided excerpts — never add outside knowledge or assumptions.
2. Keep summaries concise: 4-6 sentences, covering purpose, key points, and any important names/figures/dates mentioned.
3. Write in clear, professional, neutral language.
4. Do not include commentary about the summarization process itself — output only the summary."""

def summarize_document(chunks: list[str], source_label: str = "document", max_chunks: int = 10) -> str:
    if len(chunks) <= max_chunks:
        sample = chunks
    else:
        step = len(chunks) // max_chunks
        sample = [chunks[i] for i in range(0, len(chunks), step)][:max_chunks]
    context = "\n\n---\n\n".join(sample)

    prompt = f"""
You are summarizing a {source_label}. Based ONLY on the excerpts below,
write a concise summary in 4-6 sentences covering:
- The main purpose/topic of the document
- Key points, processes, or findings mentioned
- Any important names, figures, or dates

Excerpts:
{context}

Summary:
"""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=300,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Summarization failed: {e}")
        return "Summary unavailable."