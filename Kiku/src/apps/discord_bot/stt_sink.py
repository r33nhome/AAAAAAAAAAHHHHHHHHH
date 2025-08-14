# src/apps/discord_bot/stt_sink.py
from __future__ import annotations
import os, time, io, wave, audioop
from collections import defaultdict
from typing import Callable, Dict
from discord.ext.voice_recv.sinks import AudioSink

# Optionales VAD
try:
    import webrtcvad
    _HAVE_VAD = True
except Exception:
    _HAVE_VAD = False

PCM_RATE = 48000
PCM_CH = 2
PCM_WIDTH = 2  # s16le

OUT_RATE = 16000
OUT_CH = 1

AI_STT_DEBUG = os.getenv("AI_STT_DEBUG") in ("1","true","True","YES","yes")

class _UserBuf:
    __slots__ = ("chunks","speech_frames","total_frames","start_ts","last_speech_ts")
    def __init__(self):
        self.chunks: list[bytes] = []
        self.speech_frames = 0
        self.total_frames = 0
        self.start_ts = time.time()
        self.last_speech_ts: float = 0.0

class TranscriptionSink(AudioSink):
    def __init__(
        self,
        loop,
        on_segment: Callable,   # async def on_segment(user, wav_bytes: bytes)
        use_vad: bool = True,
        vad_mode: int = 2,
        vad_min_ms: int = 400,
        vad_ratio: float = 0.6,
        frame_ms: int = 30,
    ):
        super().__init__()
        self.encoding = "pcm"
        self.wav = False

        self.loop = loop
        self.on_segment = on_segment
        self.use_vad = bool(use_vad and _HAVE_VAD)
        self.vad_mode = max(0, min(3, int(vad_mode)))
        self.vad_min_ms = max(0, int(vad_min_ms))
        self.vad_ratio = max(0.0, min(1.0, float(vad_ratio)))
        self.frame_ms = 30 if frame_ms not in (10, 20, 30) else int(frame_ms)

        self.fallback_min_ms_no_speech = max(600, self.vad_min_ms)
        self.fallback_min_ms_some_speech = max(250, self.vad_min_ms // 2)

        self._buffers: Dict[int, _UserBuf] = defaultdict(_UserBuf)
        self._vad = webrtcvad.Vad(self.vad_mode) if self.use_vad else None
        self._dbg_first_rx = False

    def wants_opus(self) -> bool:
        return False

    def write(self, user, data):
        # PCM extrahieren (VoiceData.pcm oder bytes)
        raw = None
        try:
            if isinstance(data, (bytes, bytearray, memoryview)):
                raw = bytes(data)
            else:
                raw = getattr(data, "pcm", None) or getattr(data, "data", None) or getattr(data, "opus", None)
                if isinstance(raw, memoryview):
                    raw = raw.tobytes()
        except Exception:
            raw = None
        if not raw:
            return

        if AI_STT_DEBUG and not self._dbg_first_rx:
            print("[stt_sink] rx_frame bytes=", len(raw))
            self._dbg_first_rx = True

        frame_bytes = int(PCM_RATE * (self.frame_ms / 1000.0) * PCM_CH * PCM_WIDTH)
        uid = getattr(user, "id", 0)
        buf = self._buffers[uid]
        now = time.time()

        for i in range(0, len(raw), frame_bytes):
            chunk = raw[i:i + frame_bytes]
            if len(chunk) < frame_bytes:
                break

            buf.total_frames += 1
            if self._is_speech_frame(chunk):
                buf.speech_frames += 1
                buf.last_speech_ts = now

            buf.chunks.append(chunk)

            if (buf.speech_frames > 0) and ((now - buf.last_speech_ts) > (2 * self.frame_ms / 1000.0)):
                self._finalize(uid, user)

        if buf.chunks and (now - buf.start_ts) > 10.0:
            self._finalize(uid, user)

    def cleanup(self):
        self._buffers.clear()

    def _is_speech_frame(self, chunk: bytes) -> bool:
        if self.use_vad and self._vad:
            try:
                mono = audioop.tomono(chunk, PCM_WIDTH, 0.5, 0.5)
                down = audioop.ratecv(mono, PCM_WIDTH, 1, PCM_RATE, 16000, None)[0]
                need = int(16000 * (self.frame_ms / 1000.0)) * PCM_WIDTH
                if len(down) < need:
                    down = down + b"\x00" * (need - len(down))
                elif len(down) > need:
                    down = down[:need]
                return self._vad.is_speech(down, 16000)
            except Exception:
                return False
        try:
            rms = audioop.rms(chunk, PCM_WIDTH)
            return rms > 150
        except Exception:
            return False

    def _finalize(self, uid: int, user):
        buf = self._buffers.get(uid)
        if not buf or not buf.chunks:
            return

        dur_ms = len(buf.chunks) * self.frame_ms
        ratio = buf.speech_frames / max(1, buf.total_frames)

        if self.use_vad:
            ok = (dur_ms >= self.vad_min_ms) and (ratio >= self.vad_ratio)
        else:
            ok = (dur_ms >= (self.fallback_min_ms_no_speech if buf.speech_frames == 0 else self.fallback_min_ms_some_speech))

        pcm = b"".join(buf.chunks)
        self._buffers[uid] = _UserBuf()
        if not ok:
            return

        try:
            mono = audioop.tomono(pcm, PCM_WIDTH, 0.5, 0.5)
            down, _ = audioop.ratecv(mono, PCM_WIDTH, 1, PCM_RATE, OUT_RATE, None)
            bio = io.BytesIO()
            with wave.open(bio, "wb") as wf:
                wf.setnchannels(OUT_CH)
                wf.setsampwidth(PCM_WIDTH)
                wf.setframerate(OUT_RATE)
                wf.writeframes(down)
            wav_bytes = bio.getvalue()
        except Exception:
            return

        if user is None:
            return

        if AI_STT_DEBUG:
            print(f"[stt_sink] segment dur_ms={dur_ms} ratio={ratio:.2f} bytes={len(wav_bytes)}")

        try:
            import asyncio
            coro = self.on_segment(user, wav_bytes)
            if coro:
                asyncio.run_coroutine_threadsafe(coro, self.loop)
        except Exception:
            pass
