# src/services/llm/openai_client.py
from __future__ import annotations

import os
import re
from typing import List, Dict

from core.config import settings

try:
    from openai import AsyncOpenAI  # OpenAI SDK (>=1.x)
except Exception:
    AsyncOpenAI = None  # wird unten abgefangen


SYSTEM_PROMPT = (
    "Du bist ein freundlicher, prägnanter KI-Chatbot für Discord. "
    "Wenn der Nutzer Deutsch schreibt, antworte auf Deutsch. "
    "Antworte kurz (max. 2–3 Sätze), hilfreich und vermeide sensible Inhalte."
)


def shorten(text: str, max_len: int = 400) -> str:
    """
    Whitespace normalisieren und auf max_len kürzen.
    """
    if not text:
        return ""
    # Mehrfach-Whitespace zu Einzel-Whitespace
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_len:
        return text
    # Hart kürzen mit Ellipsis
    return (text[: max(0, max_len - 1)] + "…").rstrip()


class OpenAILLM:
    def __init__(self) -> None:
        if not settings.openai_api_key or AsyncOpenAI is None:
            raise RuntimeError("OpenAI nicht konfiguriert oder Paket fehlt.")
        os.environ.setdefault("OPENAI_API_KEY", settings.openai_api_key)
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def generate(
        self,
        messages: List[Dict],
        *,
        max_tokens: int = 180,
        temperature: float = 0.7,
    ) -> str:
        msgs = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
        try:
            resp = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=msgs,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            content = resp.choices[0].message.content if resp.choices else ""
            content = (content or "").strip()
            return shorten(content, 400) or "…"
        except Exception:
            return "Entschuldige, ich habe gerade ein Problem mit dem Sprachmodell."


_llm_singleton: OpenAILLM | None = None


def get_llm() -> OpenAILLM:
    global _llm_singleton
    if _llm_singleton is None:
        _llm_singleton = OpenAILLM()
    return _llm_singleton