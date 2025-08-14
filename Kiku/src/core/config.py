# src/core/config.py
from __future__ import annotations
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Präfix AI_ (in .env):
      - AI_ENV, AI_LOG_LEVEL
      - AI_DISCORD_TOKEN
      - AI_OPENAI_API_KEY
      - AI_TTS_PROVIDER
      - AI_ELEVENLABS_API_KEY, AI_ELEVENLABS_VOICE_ID, AI_ELEVENLABS_MODEL_ID
      - (später OBS) AI_OBS_HOST, AI_OBS_PORT, AI_OBS_PASSWORD
    """
    env: Literal["dev", "prod", "test"] = "dev"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # Discord / LLM
    discord_token: str | None = None
    openai_api_key: str | None = None

    # TTS
    tts_provider: Literal["elevenlabs", "stub"] | None = "elevenlabs"
    elevenlabs_api_key: str | None = None
    elevenlabs_voice_id: str | None = None
    elevenlabs_model_id: str | None = "eleven_multilingual_v2"

    # OBS (kommt später)
    obs_host: str | None = None
    obs_port: int | None = None
    obs_password: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="AI_",
        case_sensitive=False,
        extra="ignore",
    )

settings = Settings()
