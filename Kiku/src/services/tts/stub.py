# src/services/tts/stub.py
from __future__ import annotations
from .base import TTSResult, TTSClient

class StubTTS(TTSClient):
    async def synthesize(self, text: str) -> TTSResult:
        # Platzhalter – gibt leeren Ton "zurück"
        return TTSResult(audio=b"", mime="audio/mpeg", ext="mp3")

tts = StubTTS()
