import re

SENSITIVE_PATTERNS = [
    r"\bapi\s*key\b",
    r"\bz\.?ai\b",
    r"\bopenrouter\b",
    r"\bsource\s*code\b",
    r"\bcodebase\b",
    r"how\s+(were|are)\s+you\s+built",
    r"how\s+(were|are)\s+you\s+made",
    r"what\s+(api|language|languages|file|files|tech)",
    r"which\s+(api|language|languages|file|files)",
    r"programming\s+language",
    r"\bfastapi\b",
    r"\bsqlite\b",
    r"\bdatabase\b",
    r"\.env\b",
    r"tech\s*stack",
    r"\bbackend\b",
    r"\bfrontend\b",
    r"architecture",
    r"built\s+using",
    r"built\s+with",
    r"what\s+are\s+you\s+built",
    r"personal\s+information\s+about\s+(you|go\s*ai)",
    r"how\s+do\s+you\s+work\s+internally",
    r"what\s+model\s+do\s+you\s+use",
    r"glm-",
]


def is_sensitive_admin_query(text: str) -> bool:
    lower = (text or "").lower().strip()
    if not lower:
        return False
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, lower):
            return True
    return False


def last_user_message(messages: list[dict]) -> str:
    for msg in reversed(messages):
        if msg.get("role") == "user":
            return (msg.get("content") or "").strip()
    return ""
