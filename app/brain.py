import asyncio
import random
import re
from typing import AsyncIterator

GREETINGS = {"hi", "hello", "hey", "hola", "good morning", "good evening", "yo"}

RESPONSES = {
    "name": "I'm **Go Ai**, your personal AI assistant. I'm here to help with questions, writing, coding, planning, and more.",
    "help": "You can ask me anything — explain topics, write or debug code, brainstorm ideas, draft emails, summarize text, or chat casually. Just type your question below.",
    "thanks": "You're welcome! Let me know if there's anything else I can help with.",
    "bye": "Goodbye! Come back anytime you need help.",
}


def _last_user_text(messages: list[dict]) -> str:
    for m in reversed(messages):
        if m.get("role") == "user":
            return (m.get("content") or "").strip()
    return ""


def _build_reply(messages: list[dict]) -> str:
    text = _last_user_text(messages)
    lower = text.lower().strip()

    if not text:
        return "I'm listening — what would you like to talk about?"

    if lower in GREETINGS or lower.startswith(("hi ", "hey ", "hello ")):
        return (
            "Hello! I'm **Go Ai**. How can I help you today?\n\n"
            "You can ask me to explain something, write code, help plan a project, or just chat."
        )

    for key, reply in RESPONSES.items():
        if key in lower and len(lower) < 40:
            if key == "name" and ("your name" in lower or "who are you" in lower or "what are you" in lower):
                return reply
            if key == "help" and ("help" in lower or "what can you" in lower):
                return reply
            if key == "thanks" and ("thank" in lower):
                return reply
            if key == "bye" and lower in ("bye", "goodbye", "see you"):
                return reply

    if "python" in lower and ("code" in lower or "function" in lower or "write" in lower):
        return (
            "Here's a simple Python example:\n\n"
            "```python\ndef greet(name: str) -> str:\n    return f\"Hello, {name}!\"\n\n"
            "if __name__ == \"__main__\":\n    print(greet(\"World\"))\n```\n\n"
            "Tell me what you'd like the code to do and I'll tailor it for you."
        )

    if "javascript" in lower or "java " in lower or "typescript" in lower:
        lang = "JavaScript"
        if "java " in lower and "javascript" not in lower:
            lang = "Java"
        return (
            f"I can help with **{lang}** too. Share your goal or paste a snippet "
            f"and I'll explain, fix, or write it step by step."
        )

    if "error" in lower or "bug" in lower or "debug" in lower:
        return (
            "I'd be happy to help debug that. Please share:\n\n"
            "1. What you're trying to do\n"
            "2. What happens instead\n"
            "3. Any error message or relevant code\n\n"
            "I'll walk through it with you."
        )

    if text.endswith("?"):
        topic = text.rstrip("?").strip()
        return (
            f"Great question about **{topic[:80]}**.\n\n"
            "Here's a clear way to think about it:\n\n"
            f"- **Overview:** {topic} is a topic worth breaking into smaller parts.\n"
            "- **Key idea:** Start with the basics, then go deeper where you need detail.\n"
            "- **Next step:** Tell me your level (beginner / intermediate / expert) and I can give a tailored explanation.\n\n"
            "Want a short summary, a detailed guide, or examples?"
        )

    if len(text) > 200:
        return (
            "Thanks for the detailed message. Here's my take:\n\n"
            f"{text[:300]}{'...' if len(text) > 300 else ''}\n\n"
            "---\n\n"
            "I've read through what you shared. The main themes seem to be what you described above. "
            "If you tell me your goal (learn, decide, build, or fix something), I can give a more focused answer."
        )

    return (
        "I'm Go Ai. I couldn't reach the AI service for a full reply right now. "
        "We are facing some errors check your connection or may be our server is closed due to update"
    )


async def stream_reply(messages: list[dict]) -> AsyncIterator[str]:
    full = _build_reply(messages)
    words = re.split(r"(\s+)", full)
    i = 0
    while i < len(words):
        chunk_size = random.randint(1, 3)
        chunk = "".join(words[i : i + chunk_size])
        i += chunk_size
        if chunk:
            yield chunk
            await asyncio.sleep(random.uniform(0.012, 0.035))
