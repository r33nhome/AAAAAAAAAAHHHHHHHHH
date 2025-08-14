# src/apps/discord_bot/bot.py
from __future__ import annotations

import os, re, time, shutil, tempfile
from typing import Dict

import discord
from discord.ext import voice_recv

from core.config import settings
from core.logging import setup_logging
from services.moderation.simple import is_blocked
from services.tts import get_tts
from services.stt import get_stt
from apps.discord_bot.stt_sink import TranscriptionSink

# Moderations-Policy (TORCH/OpenAI/Heuristic via ENV steuerbar)
from services.moderation.policy import (
    score_text_for_policy, apply_action,
    get_status as mod_status,
    set_thresholds as mod_set_thresholds,
    set_mode_auto as mod_set_auto,
    whitelist_add as mod_whitelist_add,
    whitelist_remove as mod_whitelist_remove,
)

# LLM-Auswahl (Chat)
USE_OPENAI = bool(settings.openai_api_key)
if USE_OPENAI:
    from services.llm.openai_client import get_llm
else:
    from services.llm.simple import llm as echo_llm

DISCORD_HARD_LIMIT = 1900
FILLERS = {"äh","ähm","hm","hmm","öh","öhm","um","uh","uhm","erm","mmh","mmm","tja","naja","joa","mhm"}

def _shorten(text: str, n: int = 400) -> str:
    text = re.sub(r"\s+", " ", (text or "")).strip()
    return text if len(text) <= n else (text[: n - 1] + "…").rstrip()

def _safe_unlink(p: str | None) -> None:
    try:
        if p and os.path.exists(p): os.remove(p)
    except Exception:
        pass

def _clean_text(t: str) -> str:
    t = re.sub(r"\b([a-zäöü]+)(-\1){1,}\b", r"\1", t, flags=re.I)
    t = re.sub(r"\.{3,}", "…", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()

def _should_ignore_transcript(t: str, *, min_words: int, min_chars: int, fillers_on: bool) -> bool:
    if not t: return True
    txt = _clean_text(t.lower())
    if fillers_on:
        words = [w.strip(".,!?;:()[]{}'\"") for w in txt.split()]
        if words and all((w in FILLERS or len(w) <= 1) for w in words): return True
    if len(txt) < max(1, min_chars): return True
    words = [w for w in re.findall(r"[a-zäöüA-ZÄÖÜ0-9]+", txt) if w not in FILLERS]
    return len(words) < max(1, min_words)

class Bot(discord.Client):
    def __init__(self, *args, **kwargs):
        intents = kwargs.get("intents") or discord.Intents.default()
        super().__init__(*args, **kwargs)
        self.user_last_reply: Dict[int, float] = {}
        self.user_last_tts: Dict[int, float] = {}

        # Verhalten
        self.auto_listen: bool = True
        self.listening_enabled: bool = False
        self.voice_only: bool = True
        self.show_transcript: bool = False

        # VAD
        self.vad_enabled: bool = True
        self.vad_mode: int = 2
        self.vad_min_ms: int = 400
        self.vad_ratio: float = 0.6
        self.vad_frame_ms: int = 30

        # Filler/Kurztext
        self.filler_filter_on: bool = True
        self.min_words: int = 2
        self.min_chars: int = 6

        self._active_sink: TranscriptionSink | None = None
        self.log = __import__("structlog").get_logger()

    async def on_ready(self):
        try:
            await self.change_presence(
                status=discord.Status.online,
                activity=discord.Activity(type=discord.ActivityType.listening, name="deinem Chat & Voice"),
            )
        except Exception:
            pass
        self.log.info("discord_ready", user=str(self.user), openai=USE_OPENAI,
                      voice_only=self.voice_only, vad=self.vad_enabled, transcript=self.show_transcript)

    # ---------- Voice Helpers ----------
    async def _join_voice(self, m: discord.Message):
        if not m.author.voice or not m.author.voice.channel:
            await m.channel.send("Du bist in keinem Voice-Channel."); return
        ch = m.author.voice.channel
        vc = m.guild.voice_client

        if vc and vc.channel.id != ch.id:
            await vc.move_to(ch)
        elif not vc:
            # WICHTIG: für Receive muss self_deaf=False gesetzt sein
            vc = await ch.connect(self_deaf=False, cls=voice_recv.VoiceRecvClient)

        await m.channel.send(f"🎙️ Bin **{ch.name}** beigetreten.")

        # sicherstellen, dass Listening aktiv ist
        if self.auto_listen and not self.listening_enabled:
            await self._start_listen(m, announce=False)
            await m.channel.send("👂 STT ist **aktiv** (Auto).")

    async def _leave_voice(self, m: discord.Message):
        self.listening_enabled = False
        self._active_sink = None
        vc = m.guild.voice_client
        if not vc:
            await m.channel.send("Ich bin in keinem Voice-Channel."); return
        try: vc.stop_listening()
        except Exception: pass
        await vc.disconnect(force=True)
        await m.channel.send("👋 Voice verlassen.")

    async def _speak_text(self, m: discord.Message, text: str):
        vc = m.guild.voice_client
        if not vc:
            await m.channel.send("🔇 Ich bin in keinem Voice-Channel. `!join` zuerst."); return
        if not shutil.which("ffmpeg"):
            await m.channel.send("⚠️ FFmpeg fehlt."); return
        if not text: return
        tts = get_tts()
        res = await tts.synthesize(text)
        f = tempfile.NamedTemporaryFile(delete=False, suffix=f".{res.ext}")
        try: f.write(res.audio)
        finally: f.close()
        path = f.name
        if vc.is_playing(): vc.stop()
        source = discord.FFmpegPCMAudio(path)
        vc.play(source, after=lambda err: _safe_unlink(path))

    # ---------- Voice State Guards ----------
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        # falls Bot (self_)deaf gesetzt wird → ent-deafen
        if member.id == self.user.id and (after.deaf or after.self_deaf):
            try:
                await member.edit(mute=False, deaf=False)
                self.log.info("auto_undeafen")
            except Exception:
                pass

    # ---------- STT ----------
    async def _start_listen(self, m: discord.Message, announce: bool = True):
        vc = m.guild.voice_client
        if not vc:
            if announce: await m.channel.send("Ich bin in keinem Voice-Channel. `!join` zuerst.")
            return
        if self.listening_enabled:
            if announce: await m.channel.send("Ich höre bereits zu.")
            return

        async def on_segment(user: discord.Member | discord.User, wav_bytes: bytes):
            try:
                stt = get_stt()
                transcript = await stt.transcribe(wav_bytes)
                if not transcript or not transcript.strip(): return
                transcript = _clean_text(transcript)
                if _should_ignore_transcript(transcript, min_words=self.min_words, min_chars=self.min_chars, fillers_on=self.filler_filter_on):
                    return

                if self.show_transcript:
                    name = getattr(user, "display_name", user.name)
                    await m.channel.send(f"🗣️ **{name}**: {transcript}")

                # Auto-Moderation
                mod_res = await score_text_for_policy(transcript)
                if mod_res.action != "none":
                    status = await apply_action(m, mod_res, strikes_first=True)
                    self.log.info("auto_mod_voice", status=status, score=mod_res.score, label=mod_res.label)
                    if status and status.startswith("done:"):
                        return

                # Antwort
                now = time.time()
                last = self.user_last_reply.get(user.id, 0.0)
                if now - last < 1.5: return
                if USE_OPENAI:
                    lm = get_llm()
                    reply = await lm.generate([{"role":"user","content":transcript}], max_tokens=160)
                else:
                    reply = await echo_llm.generate([{"role":"user","content":transcript}], max_tokens=120)
                reply = _shorten(reply or "", 400)
                if is_blocked(reply): reply = "⚠️"
                if len(reply) > DISCORD_HARD_LIMIT: reply = reply[:DISCORD_HARD_LIMIT-1] + "…"
                if self.voice_only: await self._speak_text(m, reply)
                else: await m.channel.send(reply)
                self.user_last_reply[user.id] = time.time()
            except Exception as e:
                self.log.error("stt_on_segment_error", err=str(e))

        sink = TranscriptionSink(
            loop=self.loop,
            on_segment=on_segment,
            use_vad=self.vad_enabled,
            vad_mode=self.vad_mode,
            vad_min_ms=self.vad_min_ms,
            vad_ratio=self.vad_ratio,
            frame_ms=self.vad_frame_ms,
        )
        vc.listen(sink)
        self._active_sink = sink
        self.listening_enabled = True
        self.log.info("stt_listen_started", vad=self.vad_enabled, mode=self.vad_mode, min_ms=self.vad_min_ms, ratio=self.vad_ratio)
        if announce: await m.channel.send("👂 STT aktiviert.")

    async def _stop_listen(self, m: discord.Message):
        vc = m.guild.voice_client
        if not vc: await m.channel.send("Ich bin in keinem Voice-Channel."); return
        try: vc.stop_listening()
        except Exception: pass
        self._active_sink = None
        self.listening_enabled = False
        await m.channel.send("🛑 STT deaktiviert.")

    # ---------- Message Handling ----------
    async def on_message(self, m: discord.Message):
        if m.author.bot: return
        text = (m.content or "").strip()
        if not text: return
        low = text.lower()

        # Voice / Listen
        if low.startswith("!join"):  await self._join_voice(m);  return
        if low.startswith("!leave"): await self._leave_voice(m); return

        # Auto-Listen toggeln
        if low.startswith("!autolisten on"):
            self.auto_listen = True
            if m.guild.voice_client and not self.listening_enabled:
                await self._start_listen(m, announce=False)
            await m.channel.send("⚙️ Auto-STT: **an**"); return
        if low.startswith("!autolisten off"):
            self.auto_listen = False; await m.channel.send("⚙️ Auto-STT: **aus**"); return

        # Manuelles STT
        if low.startswith("!listen on"):  await self._start_listen(m); return
        if low.startswith("!listen off"): await self._stop_listen(m);  return

        # Transcript toggles
        if low.startswith("!transcript status"):
            await m.channel.send(f"Transcript: {'ON' if self.show_transcript else 'OFF'}"); return
        if low.startswith("!transcript on"):
            self.show_transcript = True;  await m.channel.send("Transcript: **ON**");  return
        if low.startswith("!transcript off"):
            self.show_transcript = False; await m.channel.send("Transcript: **OFF**"); return

        # VAD
        if low.startswith("!vad status"):
            if self._active_sink:
                s = self._active_sink
                await m.channel.send(f"🎚️ VAD={'ON' if s.use_vad else 'OFF'} | mode={s.vad_mode} | min_ms={s.vad_min_ms} | ratio={s.vad_ratio:.2f} | frame={s.frame_ms}ms")
            else:
                await m.channel.send("VAD: (kein aktiver Sink) – `!listen on` oder `!join`")
            return
        if low.startswith("!vad on"):
            self.vad_enabled = True
            if self._active_sink: self._active_sink.use_vad = True
            await m.channel.send("VAD: **ON**"); return
        if low.startswith("!vad off"):
            self.vad_enabled = False
            if self._active_sink: self._active_sink.use_vad = False
            await m.channel.send("VAD: **OFF**"); return
        if low.startswith("!vad mode"):
            try:
                mode = int(text.split()[-1]); mode = max(0, min(3, mode))
                self.vad_mode = mode
                if self._active_sink: self._active_sink.vad_mode = mode
                await m.channel.send(f"VAD mode: **{mode}** (0..3)")
            except Exception:
                await m.channel.send("Nutze: `!vad mode 0|1|2|3`"); return
            return
        if low.startswith("!vad min"):
            try:
                ms = int(text.split()[-1]); ms = max(0, ms)
                self.vad_min_ms = ms
                if self._active_sink: self._active_sink.vad_min_ms = ms
                await m.channel.send(f"VAD min_ms: **{ms}**")
            except Exception:
                await m.channel.send("Nutze: `!vad min <ms>`"); return
            return
        if low.startswith("!vad ratio"):
            try:
                r = float(text.split()[-1]); r = max(0.0, min(1.0, r))
                self.vad_ratio = r
                if self._active_sink: self._active_sink.vad_ratio = r
                await m.channel.send(f"VAD ratio: **{r:.2f}**")
            except Exception:
                await m.channel.send("Nutze: `!vad ratio <0.0-1.0>`"); return
            return

        # Filler/Kurztext
        if low.startswith("!filler status"):
            await m.channel.send(f"Filler-Filter={'ON' if self.filler_filter_on else 'OFF'} | min_words={self.min_words} | min_chars={self.min_chars}"); return
        if low.startswith("!filler on"):
            self.filler_filter_on = True;  await m.channel.send("Filler-Filter: **ON**"); return
        if low.startswith("!filler off"):
            self.filler_filter_on = False; await m.channel.send("Filler-Filter: **OFF**"); return
        if low.startswith("!filler minwords"):
            try:
                n = int(text.split()[-1]); self.min_words = max(1, n)
                await m.channel.send(f"min_words: **{self.min_words}**")
            except Exception:
                await m.channel.send("Nutze: `!filler minwords <n>`"); return
            return
        if low.startswith("!filler minchars"):
            try:
                n = int(text.split()[-1]); self.min_chars = max(1, n)
                await m.channel.send(f"min_chars: **{self.min_chars}**")
            except Exception:
                await m.channel.send("Nutze: `!filler minchars <n>`"); return
            return

        # Voice/Text Verhalten
        if low.startswith("!voiceonly on"):
            self.voice_only = True;  await m.channel.send("🔊 Voice-only: **an**");  return
        if low.startswith("!voiceonly off"):
            self.voice_only = False; await m.channel.send("📝 Voice-only: **aus** (ich schreibe wieder)"); return

        # Moderation Commands
        if low.startswith("!mod status"):
            await m.channel.send(f"AutoMod: {mod_status()}"); return
        if low.startswith("!mod auto on"):
            mod_set_auto(True); await m.channel.send("AutoMod: **AUTO**"); return
        if low.startswith("!mod auto off"):
            mod_set_auto(False); await m.channel.send("AutoMod: **ASSIST**"); return
        if low.startswith("!mod thres"):
            try:
                parts = text.split()
                w, k, b = float(parts[-3]), float(parts[-2]), float(parts[-1])
                mod_set_thresholds(w, k, b)
                await m.channel.send(f"Schwellen: warn={w:.2f} kick={k:.2f} ban={b:.2f}")
            except Exception:
                await m.channel.send("Nutze: `!mod thres <warn> <kick> <ban>`"); return
            return
        if low.startswith("!mod whitelist"):
            if not m.mentions: await m.channel.send("Nutze: `!mod whitelist @User`"); return
            mod_whitelist_add([u.id for u in m.mentions])
            await m.channel.send("Whitelist+ ok"); return
        if low.startswith("!mod unwhitelist"):
            if not m.mentions: await m.channel.send("Nutze: `!mod unwhitelist @User`"); return
            mod_whitelist_remove([u.id for u in m.mentions])
            await m.channel.send("Whitelist- ok"); return

        # --- Normale Textmessage: erst Moderation, dann Antwort ---
        mod_res = await score_text_for_policy(text)
        if mod_res.action != "none":
            status = await apply_action(m, mod_res, strikes_first=True)
            self.log.info("auto_mod_text", status=status, score=mod_res.score, label=mod_res.label)
            if status and status.startswith("done:"):
                return

        if is_blocked(text): return
        now = time.time()
        if now - self.user_last_reply.get(m.author.id, 0.0) < 2.0:
            try: await m.channel.send("⏳ bitte kurz warten (Cooldown 2s).")
            except Exception: pass
            return
        try:
            if USE_OPENAI:
                lm = get_llm()
                reply = await lm.generate([{"role":"user","content":text}], max_tokens=160)
            else:
                reply = await echo_llm.generate([{"role":"user","content":text}], max_tokens=120)
            reply = _shorten(reply or "", 400)
        except Exception:
            reply = "Uff, da ist gerade etwas schiefgelaufen. Bitte gleich nochmal."
        if is_blocked(reply): reply = "⚠️"
        if len(reply) > DISCORD_HARD_LIMIT: reply = reply[:DISCORD_HARD_LIMIT-1] + "…"
        if self.voice_only: await self._speak_text(m, reply)
        else: await m.channel.send(reply)
        self.user_last_reply[m.author.id] = time.time()

def main() -> None:
    setup_logging()
    token = settings.discord_token
    if not token: raise RuntimeError("AI_DISCORD_TOKEN fehlt (.env)")
    intents = discord.Intents.default(); intents.message_content = True
    Bot(intents=intents).run(token)

if __name__ == "__main__":
    main()
