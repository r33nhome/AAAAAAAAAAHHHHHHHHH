# src/services/tts/base.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol

@dataclass
class TTSResult:
    audio: bytes
    mime: str = "audio/mpeg"
    ext: str = "mp3"

class TTSClient(Protocol):
    async def synthesize(self, text: str) -> TTSResult: ...

