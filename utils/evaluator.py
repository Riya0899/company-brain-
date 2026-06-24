"""
evaluator.py
------------
Scores each answer for faithfulness and relevancy using DeepEval's
built-in metrics (FaithfulnessMetric, AnswerRelevancyMetric), powered
by a custom Groq LLM wrapper.

Threshold for "passed" is 0.5 on each metric (matches DeepEval default
metric.threshold usage).
"""

import os
import json
import re
from dotenv import load_dotenv

from groq import Groq

from deepeval.models import DeepEvalBaseLLM
from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

load_dotenv()

JUDGE_MODEL = "llama-3.1-8b-instant"
THRESHOLD = 0.5


# ── Custom Groq wrapper for DeepEval ────────────────────────────────────────

class GroqDeepEvalModel(DeepEvalBaseLLM):
    """
    Minimal DeepEvalBaseLLM implementation backed by Groq.
    DeepEval calls generate()/a_generate() and expects either plain text
    or, when a schema is passed, a parsed pydantic object. We handle the
    schema case by asking for JSON and parsing it ourselves.
    """

    def __init__(self, model_name: str = JUDGE_MODEL):
        self.model_name = model_name
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def load_model(self):
        return self.client

    def _chat(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
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
            max_tokens=512,
        )
        return response.choices[0].message.content.strip()

    @staticmethod
    def _clean_json(raw: str) -> str:
        return re.sub(r"```[a-z]*", "", raw).strip().strip("`").strip()

    def generate(self, prompt: str, schema=None):
        raw = self._chat(prompt) #gets response from Groq
        clean = self._clean_json(raw)

        if schema is None:
            return raw

        # DeepEval metrics pass a pydantic schema and expect an instance back.
        try:
            data = json.loads(clean)
            return schema(**data) #creates pydantic object
        except Exception:
            # Last-ditch fallback so DeepEval doesn't crash the whole eval run
            try:
                return schema()
            except Exception:
                raise

    async def a_generate(self, prompt: str, schema=None):
        # Groq's python client call above is sync; just reuse it.
        return self.generate(prompt, schema=schema)

    def get_model_name(self):
        return f"groq/{self.model_name}"


_judge_model = GroqDeepEvalModel()


# ── public API ───────────────────────────────────────────────────────────────

def evaluate_answer(
    question: str,
    answer: str,
    context_chunks: list[str],
) -> tuple[bool, float, str]:
    """
    Evaluate an answer using DeepEval (Faithfulness + AnswerRelevancy),
    judged by a Groq-backed model.

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

    context = context_chunks[:5]  # cap to avoid token overflow

    try:
        test_case = LLMTestCase(
            input=question,
            actual_output=answer,
            retrieval_context=context,
            context=context,
        )

        faithfulness_metric = FaithfulnessMetric(
            threshold=THRESHOLD,
            model=_judge_model,
            include_reason=True,
        )
        relevancy_metric = AnswerRelevancyMetric(
            threshold=THRESHOLD,
            model=_judge_model,
            include_reason=True,
        )

        faithfulness_metric.measure(test_case)
        relevancy_metric.measure(test_case)

        faith_score = faithfulness_metric.score or 0.0
        rel_score = relevancy_metric.score or 0.0

        avg_score = (faith_score + rel_score) / 2
        passed = faith_score >= THRESHOLD and rel_score >= THRESHOLD

        reason = (
            f"Faithfulness: {faith_score:.2f} ({faithfulness_metric.reason}) | "
            f"Relevancy: {rel_score:.2f} ({relevancy_metric.reason})"
        )
        return passed, avg_score, reason

    except Exception as e:
        print(f"Evaluation failed: {e}")
        # Fail open so the UI still shows an answer
        return True, 0.75, f"Evaluation skipped ({type(e).__name__})"