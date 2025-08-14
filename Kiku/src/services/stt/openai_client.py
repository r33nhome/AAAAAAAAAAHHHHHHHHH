# src/services/stt/openai_client.py
from __future__ import annotations
import io
from openai import AsyncOpenAI
from core.config import settings

MODEL = "gpt-4o-mini-transcribe"  # Fallback möglich: "whisper-1"

class OpenAIStt:
    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise RuntimeError("AI_OPENAI_API_KEY fehlt.")
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def transcribe(self, wav_bytes: bytes) -> str:
        bio = io.BytesIO(wav_bytes)
        bio.name = "audio.wav"
        resp = await self.client.audio.transcriptions.create(
            model=MODEL,
            file=bio,
        )
        text = getattr(resp, "text", None) or ""
        return text.strip()
