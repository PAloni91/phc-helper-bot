"""OpenRouter client with input/output limits and output validation."""
from typing import Dict, List

import httpx

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = (
    "You are a helpful assistant for a rural primary health centre (PHC) in India. "
    "Use simple, short sentences that someone with basic schooling can follow. "
    "Answer ONLY using the information in the CONTEXT block when it is relevant; "
    "if the context does not cover the question, say you are not sure and advise "
    "the person to ask a doctor or health worker at the PHC. "
    "You are not a doctor: never diagnose and never give medicine doses. "
    "If the question suggests an emergency (chest pain, trouble breathing, heavy "
    "bleeding, unconsciousness, snake bite, seizure), tell the person to call 108 "
    "(ambulance) or 112 immediately and give only basic first-aid steps from the context."
)


class LLMError(Exception):
    """Raised for any problem calling or validating the LLM response."""


def build_messages(question: str, context_chunks: List[str]) -> List[Dict[str, str]]:
    context = "\n\n".join(context_chunks) if context_chunks else "(no matching context found)"
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"CONTEXT:\n{context}\n\nQUESTION:\n{question}"},
    ]


async def ask_llm(question: str, context_chunks: List[str], *, api_key: str, model: str,
                  max_input_chars: int, max_output_tokens: int,
                  timeout: float = 30.0) -> str:
    """Ask the model and return a non-empty string answer, or raise LLMError."""
    if len(question) > max_input_chars:
        raise LLMError(f"Question too long (max {max_input_chars} characters).")

    payload = {
        "model": model,
        "messages": build_messages(question, context_chunks),
        "max_tokens": max_output_tokens,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(OPENROUTER_URL, headers=headers, json=payload)
            response.raise_for_status()
            text = response.json()["choices"][0]["message"]["content"]
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
        raise LLMError(f"LLM request failed: {exc.__class__.__name__}") from exc

    if not isinstance(text, str) or not text.strip():
        raise LLMError("LLM returned an empty or non-text answer.")
    return text.strip()
