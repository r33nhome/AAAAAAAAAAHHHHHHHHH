# src/services/stt/__init__.py
from __future__ import annotations
from core.config import settings

def get_stt():
    provider = (getattr(settings, "stt_provider", None) or "openai").lower()
    if provider == "openai":
        from .openai_client import OpenAIStt
        return OpenAIStt()
    # weitere Provider hier später ergänzen
    from .openai_client import OpenAIStt
    return OpenAIStt()
