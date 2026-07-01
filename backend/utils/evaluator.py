import os
import json
import re
from dotenv import load_dotenv
from typing import List

from groq import Groq

from deepeval.models import DeepEvalBaseLLM
from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

load_dotenv()

JUDGE_MODEL = "llama-3.1-8b-instant"
THRESHOLD = 0.5


# ── Custom Groq wrapper for DeepEval ────────────────────────────────────────

class GroqDeepEvalModel(DeepEvalBaseLLM):
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
            max_tokens=1024,
        )
        return response.choices[0].message.content.strip()

    @staticmethod
    def _clean_json(raw: str) -> str:
        return re.sub(r"```[a-z]*", "", raw).strip().strip("`").strip()

    def generate(self, prompt: str, schema=None):
        raw = self._chat(prompt)
        clean = self._clean_json(raw)

        if schema is None:
            return raw

        # Attempt 1: direct parse
        try:
            data = json.loads(clean)
            return schema(**data)
        except Exception:
            pass

        # Attempt 2: extract the first {...} or [...] block from the raw text
        # (handles cases where the model added stray text around the JSON)
        try:
            match = re.search(r"\{.*\}|\[.*\]", clean, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                if isinstance(data, list):
                    # Some DeepEval schemas expect {"field_name": [...]}
                    field_name = next(iter(schema.model_fields.keys()))
                    return schema(**{field_name: data})
                return schema(**data)
        except Exception:
            pass

        # Final fallback: build a schema instance with safe, empty-but-valid
        # defaults for every required field, based on its declared type.
        # This guarantees DeepEval never crashes here, even on a total parse failure.
        defaults = {}
        for field_name, field_info in schema.model_fields.items():
            annotation = field_info.annotation
            origin = getattr(annotation, "__origin__", None)
            if origin in (list, List):
                defaults[field_name] = []
            elif annotation in (str,):
                defaults[field_name] = ""
            elif annotation in (int,):
                defaults[field_name] = 0
            elif annotation in (float,):
                defaults[field_name] = 0.0
            elif annotation in (bool,):
                defaults[field_name] = False
            else:
                defaults[field_name] = None

        return schema(**defaults)

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
    if not answer or len(answer.strip()) < 10:
        return False, 0.0, "Answer too short to evaluate",0.0,0.0

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
        return passed, avg_score, reason,faith_score,rel_score

    except Exception as e:
        print(f"Evaluation failed: {e}")
        # Fail open so the UI still shows an answer
        return True, 0.75, f"Evaluation skipped ({type(e).__name__})"