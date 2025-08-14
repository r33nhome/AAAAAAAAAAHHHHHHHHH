# src/services/moderation/policy.py
from __future__ import annotations
import os, re, datetime, asyncio
from dataclasses import dataclass
from typing import Literal, Tuple, Optional, Set
import discord

# --- Schwellen (änderbar via Bot-Befehle) ---
TOX_WARN  = 0.70
TOX_KICK  = 0.85
TOX_BAN   = 0.95

# In-Memory-Zustände (flüchtig)
USER_STRIKES: dict[int, int] = {}
MOD_AUTO: bool = True
WHITELIST: Set[int] = set()

# Harte Regex
BAD_PATTERNS = [
    r"\b(kys|kill\s+yourself)\b",
    r"\b(naz[iy]|hitler|gas\s+the)\b",
]
BAD_REGEX = re.compile("|".join(BAD_PATTERNS), re.IGNORECASE)

Action = Literal["none","warn","timeout","kick","ban"]

@dataclass
class ModResult:
    score: float
    label: str
    action: Action
    reason: str

# Provider-Routing
_MOD_PROVIDER = os.getenv("AI_MOD_PROVIDER", "heuristic").lower()
_MOD_MODEL_PATH = os.getenv("AI_MOD_MODEL_PATH") or ""
_MOD_LABEL_TOXIC = os.getenv("AI_MOD_LABEL_TOXIC") or None
_TORCH = None

def _ensure_torch_model():
    global _TORCH
    if _TORCH is None and _MOD_PROVIDER == "torch":
        from .torch_model import TorchModerator
        _TORCH = TorchModerator(_MOD_MODEL_PATH, label_toxic=_MOD_LABEL_TOXIC)

def _regex_hit(text: str) -> bool:
    return bool(BAD_REGEX.search(text or ""))

async def _score_openai(text: str) -> Tuple[float, str]:
    key = os.getenv("AI_OPENAI_API_KEY")
    if not key:
        return 0.0, "ok"
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=key)
        resp = await client.moderations.create(model="omni-moderation-latest", input=text[:4000])
        res = getattr(resp, "results", None) or []
        if not res:
            return 0.0, "ok"
        r0 = res[0]
        scores = getattr(r0, "category_scores", {}) or {}
        if not scores:
            flagged = bool(getattr(r0, "flagged", False))
            return (0.9 if flagged else 0.0), "openai"
        label, score = max(scores.items(), key=lambda kv: kv[1])
        return float(score), str(label)
    except Exception:
        return (1.0 if _regex_hit(text) else 0.0), "heuristic"

async def _score_heuristic(text: str) -> Tuple[float, str]:
    if _regex_hit(text):
        return 1.0, "regex"
    caps = sum(1 for w in re.findall(r"\w+", text) if len(w) >= 3 and w.isupper())
    return min(1.0, 0.3 + 0.1 * caps), "heuristic"

async def score_text_for_policy(text: str) -> ModResult:
    if _regex_hit(text):
        return ModResult(1.0, "regex", "ban", "regex")

    if _MOD_PROVIDER == "torch":
        _ensure_torch_model()
        try:
            loop = asyncio.get_running_loop()
            score, label = await loop.run_in_executor(None, _TORCH.score, text)
        except Exception:
            score, label = await _score_heuristic(text)
        reason = "torch"
    elif _MOD_PROVIDER == "openai":
        score, label = await _score_openai(text)
        reason = "openai"
    else:
        score, label = await _score_heuristic(text)
        reason = "heuristic"

    if score >= TOX_BAN:
        action: Action = "ban"
    elif score >= TOX_KICK:
        action = "kick"
    elif score >= TOX_WARN:
        action = "warn"
    else:
        action = "none"

    return ModResult(score=score, label=label, action=action, reason=reason)

async def apply_action(message: discord.Message, res: ModResult, *, strikes_first: bool = True) -> Optional[str]:
    member = message.author
    guild = message.guild
    if not guild or not isinstance(member, discord.Member):
        return "skip:no_guild_or_member"
    if member.id in WHITELIST or member.guild_permissions.administrator:
        return "skip:whitelisted"

    strikes = USER_STRIKES.get(member.id, 0)
    action = res.action
    if strikes_first:
        if strikes >= 3: action = "ban"
        elif strikes == 2 and action in ("none","warn"): action = "kick"
        elif strikes == 1 and action == "none": action = "warn"

    # Assist-Modus?
    if not MOD_AUTO and action != "none":
        return f"suggest:{action}:{res.label}:{res.score:.2f}"

    try:
        if action == "warn":
            USER_STRIKES[member.id] = strikes + 1
            await message.channel.send(f"⚠️ Bitte höflich bleiben, {member.display_name}. ({res.label}, {res.score:.2f})")
            return "done:warn"
        if action == "timeout":
            USER_STRIKES[member.id] = strikes + 1
            until = discord.utils.utcnow() + datetime.timedelta(minutes=10)
            await member.timeout(until, reason=f"AutoMod: {res.label} ({res.score:.2f})")
            if member.voice and member.voice.channel:
                try: await member.move_to(None)
                except: pass
            await message.channel.send(f"⏳ {member.display_name} 10 Min. Timeout. ({res.label})")
            return "done:timeout"
        if action == "kick":
            USER_STRIKES[member.id] = strikes + 1
            if member.voice and member.voice.channel:
                try: await member.move_to(None)
                except: pass
            await member.kick(reason=f"AutoMod: {res.label} ({res.score:.2f})")
            await message.channel.send(f"👢 {member.display_name} wurde gekickt. ({res.label})")
            return "done:kick"
        if action == "ban":
            USER_STRIKES[member.id] = strikes + 1
            if member.voice and member.voice.channel:
                try: await member.move_to(None)
                except: pass
            await member.ban(reason=f"AutoMod: {res.label} ({res.score:.2f})", delete_message_days=0)
            await message.channel.send(f"🔨 {member.display_name} wurde gebannt. ({res.label})")
            return "done:ban"
        return "skip:none"
    except discord.Forbidden:
        return "fail:forbidden"
    except Exception as e:
        return f"fail:{type(e).__name__}"

# ----- Helfer für Bot-Kommandos -----
def get_status() -> str:
    return f"AUTO={'ON' if MOD_AUTO else 'OFF'} | thres warn={TOX_WARN:.2f} kick={TOX_KICK:.2f} ban={TOX_BAN:.2f} | whitelist={len(WHITELIST)}"

def set_thresholds(warn: float, kick: float, ban: float) -> None:
    global TOX_WARN, TOX_KICK, TOX_BAN
    TOX_WARN, TOX_KICK, TOX_BAN = float(warn), float(kick), float(ban)

def set_mode_auto(on: bool) -> None:
    global MOD_AUTO
    MOD_AUTO = bool(on)

def whitelist_add(user_ids: list[int]) -> None:
    for uid in user_ids: WHITELIST.add(int(uid))

def whitelist_remove(user_ids: list[int]) -> None:
    for uid in user_ids: WHITELIST.discard(int(uid))
