# AI-VTuber – Phase 0
Minimalgerüst gemäß Roadmap: Python 3.11, uv, structlog, pydantic-settings, pytest.

## Quickstart (Windows / PowerShell)
irm https://astral.sh/uv/install.ps1 | iex
uv venv .venv
. .\.venv\Scripts\Activate.ps1
uv sync --all-extras
uv run pytest
uv run python -c "from core.logging import setup_logging; setup_logging(); import structlog; structlog.get_logger().info('boot_ok')"


# 1) Voraussetzungen
# - Python 3.11
# - ffmpeg im PATH (für Voice-Ausgabe)
# - Discord-Bot angelegt, Token & Intents gesetzt
# - ElevenLabs-Key + Voice-ID, OpenAI-API-Key

# 2) Abhängigkeiten
uv sync --all-extras

# 3) .env aus Beispiel erstellen & befüllen
Copy-Item .env.example .env
# (Datei öffnen und Token/Keys eintragen)

# 4) Starten
uv run bot

!join        # Bot joint deinem Voice-Channel + STT automatisch aktiv
# sprich im Voice-Channel → Kiku transkribiert und antwortet per Stimme


src/
  core/                 # config, logging
  apps/
    discord_bot/        # bot.py (+ stt_sink.py)
    obs_control/        # (später) OBS WebSocket
    game_agents/        # (später) SDK/Agents
  services/
    llm/                # OpenAI-Client
    tts/                # ElevenLabs-Client (+ Factory)
    stt/                # OpenAI STT (+ Factory)
    moderation/         # simple blocklist
ui/overlays/            # (später)
tests/
pyproject.toml
.env.example


Voraussetzungen
Windows 10/11

Python 3.11

ffmpeg (für Voice-Wiedergabe): ffmpeg -version muss im Terminal funktionieren

Discord Developer Portal

Bot → Privileged Gateway Intents: Message Content Intent: ON

Bot → Requires OAuth2 Code Grant: OFF

Installation oder OAuth2 URL Generator: Scopes bot (+ optional applications.commands)
Permissions (Minimal + Voice):

View Channels, Read Message History, Send Messages, Embed Links, Attach Files, Add Reactions

Connect, Speak

Installation
1) Pakete
powershell
Kopieren
Bearbeiten
uv sync --all-extras
(Wir nutzen httpx, discord.py, discord-ext-voice-recv, PyNaCl, structlog, pydantic-settings u. a.)

2) .env ausfüllen
Erzeuge .env (am besten aus Vorlage):

powershell
Kopieren
Bearbeiten
Copy-Item .env.example .env
Bearbeite .env:

env
Kopieren
Bearbeiten
# Basis
AI_ENV=dev
AI_LOG_LEVEL=INFO

# Discord
AI_DISCORD_TOKEN=DEIN_DISCORD_BOT_TOKEN

# OpenAI (LLM + STT)
AI_OPENAI_API_KEY=DEIN_OPENAI_API_KEY
AI_STT_PROVIDER=openai

# TTS (ElevenLabs)
AI_TTS_PROVIDER=elevenlabs
AI_ELEVENLABS_API_KEY=DEIN_ELEVENLABS_KEY
AI_ELEVENLABS_VOICE_ID=DEINE_VOICE_ID
AI_ELEVENLABS_MODEL_ID=eleven_multilingual_v2

# (später) OBS
# AI_OBS_HOST=127.0.0.1
# AI_OBS_PORT=4455
# AI_OBS_PASSWORD=changeme123
Nur ein OpenAI-Key nötig: AI_OPENAI_API_KEY wird für Chat und STT benutzt.

3) Bot einladen
Erzeuge einen Install/Invite-Link mit Scope bot (ohne Redirect).
Rechte wie oben („Voraussetzungen“). Link öffnen → Server wählen → autorisieren.

Start
powershell
Kopieren
Bearbeiten
uv run bot
Im Log sollte stehen:

nginx
Kopieren
Bearbeiten
discord_ready ... openai=true
Benutzung (Befehlsübersicht)
Voice / STT / TTS

!join – Bot tritt deinem aktuellen Voice-Channel bei (Auto-STT startet)

!leave – Voice verlassen

!autolisten on|off – Auto-STT (nach !join) an/aus (Standard: an)

!listen on|off – STT manuell an/aus

!voiceonly on|off – nur sprechen oder auch textlich antworten (Standard: nur sprechen)

!say <text> – generiert TTS-Audio und sendet Datei in den Textkanal

!sayv <text> – spricht den Text im Voice-Channel

Chat

Jede normale Nachricht im Textkanal wird vom LLM beantwortet
(bei voiceonly on spricht Kiku die Antwort; kein Text-Reply)
Nutzung (neu)
VAD

!vad status – zeigt aktuelle Werte

!vad on / !vad off

!vad mode 0|1|2|3 – 3 = aggressiv (härter filtert)

!vad min 300 – min. Sprachdauer (ms) im Segment

!vad ratio 0.6 – Anteil „Speech“ im Segment (0–1)

Filler/Kurztext-Filter

!filler status

!filler on / !filler off

!filler minwords 2

!filler minchars 6