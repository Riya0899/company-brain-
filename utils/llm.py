from openai import OpenAI
from dotenv import load_dotenv
from utils.evaluator import evaluate_answer
import os
import time

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

MODEL = "openrouter/free"

def generate_answer(context, question):
    prompt = f"""
    You are Company Brain AI.
    Rules:
    1. Use ONLY the provided knowledge.
    2. Use conversation history for follow-up questions.
    3. If information is unavailable, say: 'I could not find that information.'

    knowledge:
    {context}

    Question:
    {question}

    Give a clear, professional answer.
    """

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def generate_answer_with_retry(context, question, max_retries=3):
    context_chunks = [c.strip() for c in context.split("\n\n") if c.strip()]

    attempt = 0
    best_answer = None
    best_score = 0
    best_reason = ""

    while attempt < max_retries:
        attempt += 1
        time.sleep(1)

        if attempt == 1:
            prompt_instruction = "Give a clear, professional answer."
        elif attempt == 2:
            prompt_instruction = "Be more specific and detailed. Cite exact information from the knowledge base."
        else:
            prompt_instruction = "Give the most precise and complete answer possible using only the provided knowledge."

        prompt = f"""
        You are Company Brain AI.
        Rules:
        1. Use ONLY the provided knowledge.
        2. Use conversation history for follow-up questions.
        3. If information is unavailable, say: 'I could not find that information.'

        knowledge:
        {context}

        Question:
        {question}

        {prompt_instruction}
        """

        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content

        passed, score, reason = evaluate_answer(question, answer, context_chunks)

        if score > best_score:
            best_score = score
            best_answer = answer
            best_reason = reason

        if passed:
            return best_answer, best_score, attempt, best_reason

    return best_answer, best_score, attempt, f"Max retries reached. Best score: {best_score:.2f}"