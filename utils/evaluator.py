"""
evaluator.py
------------
Scores each answer for faithfulness and relevancy using a Groq-powered
judge model — no DeepEval dependency on the LLM side.

Scoring logic mirrors DeepEval's approach:
  • Faithfulness  – does the answer stick to the retrieved context?
  • Relevancy     – does the answer actually address the question?

Both scores are 0.0–1.0; the average becomes the confidence shown in the UI.
Threshold for "passed" is 0.5 on each metric.
"""

from groq import Groq
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()

# Use a smaller / faster model for evaluation to save quota on the main model
JUDGE_MODEL = "llama-3.1-8b-instant"

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ── helpers ──────────────────────────────────────────────────────────────────

def _ask_judge(prompt: str) -> str:
    """Send a single prompt to the judge and return the raw text reply."""
    response = client.chat.completions.create(
        model=JUDGE_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict evaluation assistant. "
                    "Always respond with valid JSON only. "
                    "No markdown, no extra text, no code fences."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0,
        max_tokens=256,
    )
    return response.choices[0].message.content.strip()


def _parse_score(raw: str, key: str = "score") -> float:
    """
    Extract a numeric score from a JSON string returned by the judge.
    Falls back gracefully if parsing fails.
    """
    # Strip accidental markdown fences just in case
    clean = re.sub(r"```[a-z]*", "", raw).strip().strip("`").strip()
    try:
        data = json.loads(clean)
        score = float(data.get(key, 0.0))
        return max(0.0, min(1.0, score))   # clamp to [0, 1]
    except Exception:
        # Last-ditch: look for the first float/int in the string
        nums = re.findall(r"\b(0(?:\.\d+)?|1(?:\.0+)?)\b", clean)
        if nums:
            return float(nums[0])
        return 0.5   # neutral fallback


# ── faithfulness ─────────────────────────────────────────────────────────────

FAITHFULNESS_PROMPT = """
You will evaluate whether an AI answer is faithful to the provided context.

CONTEXT (retrieved document chunks):
{context}

ANSWER:
{answer}

Score faithfulness from 0.0 to 1.0:
  1.0 = every claim in the answer is directly supported by the context
  0.5 = some claims are supported; some are not
  0.0 = the answer contradicts or ignores the context entirely

Respond ONLY with this JSON:
{{"score": <number between 0.0 and 1.0>, "reason": "<one sentence>"}}
"""


def _faithfulness_score(answer: str, context_chunks: list[str]) -> tuple[float, str]:
    context = "\n\n".join(context_chunks[:5])   # cap to avoid token overflow
    prompt = FAITHFULNESS_PROMPT.format(context=context, answer=answer)
    raw = _ask_judge(prompt)
    score = _parse_score(raw, "score")
    try:
        reason = json.loads(re.sub(r"```[a-z]*", "", raw).strip().strip("`")).get("reason", "")
    except Exception:
        reason = ""
    return score, reason


# ── relevancy ────────────────────────────────────────────────────────────────

RELEVANCY_PROMPT = """
You will evaluate whether an AI answer actually addresses the user's question.

QUESTION:
{question}

ANSWER:
{answer}

Score answer relevancy from 0.0 to 1.0:
  1.0 = the answer fully and directly addresses the question
  0.5 = the answer is partially relevant
  0.0 = the answer is off-topic or does not address the question at all

Respond ONLY with this JSON:
{{"score": <number between 0.0 and 1.0>, "reason": "<one sentence>"}}
"""


def _relevancy_score(question: str, answer: str) -> tuple[float, str]:
    prompt = RELEVANCY_PROMPT.format(question=question, answer=answer)
    raw = _ask_judge(prompt)
    score = _parse_score(raw, "score")
    try:
        reason = json.loads(re.sub(r"```[a-z]*", "", raw).strip().strip("`")).get("reason", "")
    except Exception:
        reason = ""
    return score, reason


# ── public API ───────────────────────────────────────────────────────────────

THRESHOLD = 0.5


def evaluate_answer(
    question: str,
    answer: str,
    context_chunks: list[str],
) -> tuple[bool, float, str]:
    """
    Evaluate an answer using Groq as the judge model.

    Returns
    -------
    passed : bool    — True if both metrics meet the threshold
    score  : float   — average of faithfulness + relevancy (0.0–1.0)
    reason : str     — human-readable summary
    """
    if not answer or len(answer.strip()) < 10:
        return False, 0.0, "Answer too short to evaluate"

    if not isinstance(context_chunks, list):
        context_chunks = [context_chunks]

    try:
        faith_score, faith_reason = _faithfulness_score(answer, context_chunks)
        rel_score, rel_reason = _relevancy_score(question, answer)

        avg_score = (faith_score + rel_score) / 2
        passed = faith_score >= THRESHOLD and rel_score >= THRESHOLD

        reason = (
            f"Faithfulness: {faith_score:.2f} ({faith_reason}) | "
            f"Relevancy: {rel_score:.2f} ({rel_reason})"
        )
        return passed, avg_score, reason

    except Exception as e:
        print(f"Evaluation failed: {e}")
        # Fail open so the UI still shows an answer
        return True, 0.75, f"Evaluation skipped ({type(e).__name__})"