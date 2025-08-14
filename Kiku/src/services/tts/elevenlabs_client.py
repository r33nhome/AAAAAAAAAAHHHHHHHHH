# src/services/tts/elevenlabs_client.py
from __future__ import annotations

import httpx
from .base import TTSResult, TTSClient

_BASE = "https://api.elevenlabs.io/v1"

class ElevenLabsTTS(TTSClient):
    def __init__(self, api_key: str | None, voice_id: str | None, model_id: str | None):
        if not api_key or not voice_id:
            raise RuntimeError("ElevenLabs API-Key oder Voice-ID fehlt (siehe .env).")
        self.api_key = api_key
        self.voice_id = voice_id
        self.model_id = model_id or "eleven_multilingual_v2"

    async def synthesize(self, text: str) -> TTSResult:
        headers = {
            "xi-api-key": self.api_key,
            "accept": "audio/mpeg",
            "content-type": "application/json",
        }
        payload = {
            "text": text,
            "model_id": self.model_id,
            "voice_settings": {"stability": 0.4, "similarity_boost": 0.9},
        }
        url = f"{_BASE}/text-to-speech/{self.voice_id}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            return TTSResult(audio=r.content, mime="audio/mpeg", ext="mp3")
