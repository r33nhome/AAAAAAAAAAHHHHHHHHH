from __future__ import annotations

class SimpleLLM:
    async def generate(self, messages: list[dict], *, max_tokens: int = 120) -> str:
        # Echo/Stub – ersetzt in Phase 1b durch echte API (OpenAI/Anthropic)
        last = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        return f"Echo: {last[:200]}"

llm = SimpleLLM()