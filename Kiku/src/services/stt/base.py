# src/services/stt/base.py
from __future__ import annotations
from typing import Protocol

class STTClient(Protocol):
    async def transcribe(self, wav_bytes: bytes) -> str:
        """Nimmt WAV-Bytes (48 kHz, 16-bit, 2ch) und liefert das Transkript zurück."""
        ...
