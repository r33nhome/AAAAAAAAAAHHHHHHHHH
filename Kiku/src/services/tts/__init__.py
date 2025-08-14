# src/services/tts/__init__.py
from __future__ import annotations
from core.config import settings

def get_tts():
    if (settings.tts_provider or "").lower() == "elevenlabs":
        from .elevenlabs_client import ElevenLabsTTS
        return ElevenLabsTTS(
            api_key=settings.elevenlabs_api_key,
            voice_id=settings.elevenlabs_voice_id,
            model_id=settings.elevenlabs_model_id,
        )
    else:
        from .stub import tts
        return tts
