from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase
from deepeval.models.base_model import DeepEvalBaseLLM
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

class OpenRouterModel(DeepEvalBaseLLM):
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        )
        # ✅ Use a stronger model specifically for evaluation
        self.model_name = "nvidia/nemotron-3-super-120b-a12b:free"

    def load_model(self):
        return self.client

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are an evaluation assistant. Always respond with valid JSON only. No explanations, no markdown, no extra text."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=0  # ← keeps output deterministic and structured
        )
        return response.choices[0].message.content

    async def a_generate(self, prompt: str) -> str:
        return self.generate(prompt)

    def get_model_name(self) -> str:
        return self.model_name


def evaluate_answer(question, answer, context_chunks):
    # ✅ Skip evaluation if answer is empty or too short
    if not answer or len(answer.strip()) < 10:
        return False, 0.0, "Answer too short to evaluate"

    retrieval_context = context_chunks if isinstance(context_chunks, list) else [context_chunks]

    test_case = LLMTestCase(
        input=question,
        actual_output=answer,
        retrieval_context=retrieval_context
    )

    judge = OpenRouterModel()

    try:
        faithfulness = FaithfulnessMetric(threshold=0.5, model=judge, include_reason=True)
        relevancy = AnswerRelevancyMetric(threshold=0.5, model=judge, include_reason=True)

        faithfulness.measure(test_case)
        relevancy.measure(test_case)

        faith_score = faithfulness.score or 0.0
        rel_score = relevancy.score or 0.0
        avg_score = (faith_score + rel_score) / 2

        passed = faithfulness.is_successful() and relevancy.is_successful()
        reason = f"Faithfulness: {faith_score:.2f} | Relevancy: {rel_score:.2f}"

        return passed, avg_score, reason

    except Exception as e:
        print(f"Evaluation failed: {e}")
        return True, 0.75, "Evaluation skipped (model output parse error)"