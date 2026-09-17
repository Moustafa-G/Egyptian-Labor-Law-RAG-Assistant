import logging

import ollama

from app.core.config import settings

logger = logging.getLogger(__name__)


def build_prompt(question: str, retrieved_chunks: list[dict]) -> str:
    context_blocks = []
    for i, chunk in enumerate(retrieved_chunks, start=1):
        context_blocks.append(
            f"[{i}] (Article {chunk['article']}, {chunk['source']})\n{chunk['text']}"
        )
    context = "\n\n".join(context_blocks)

    return f"""You are a legal information assistant for Egyptian Labor Law.
Answer the question using ONLY the context provided below. If the context does not
contain the answer, say you don't have enough information in the provided law text.
Always cite which article(s) your answer is based on, like (Article 54).

Context:
{context}

Question: {question}

Answer (with article citations):"""


def generate_answer(question: str, retrieved_chunks: list[dict]) -> str:
    prompt = build_prompt(question, retrieved_chunks)
    try:
        response = ollama.chat(
            model=settings.llm_model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response["message"]["content"]
    except Exception as e:
        logger.error("LLM generation failed: %s", e)
        raise
