import json
import uuid
from datetime import datetime, timezone

from app.config import CHATS_FILE, DATA_DIR


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_chats() -> list[dict]:
    _ensure_data_dir()
    if not CHATS_FILE.exists():
        return []
    with open(CHATS_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_chats(chats: list[dict]) -> None:
    _ensure_data_dir()
    with open(CHATS_FILE, "w", encoding="utf-8") as f:
        json.dump(chats, f, indent=2, ensure_ascii=False)


def create_chat(title: str = "New chat") -> dict:
    return {
        "id": str(uuid.uuid4()),
        "title": title,
        "messages": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def title_from_message(text: str, max_len: int = 40) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= max_len:
        return cleaned or "New chat"
    return cleaned[: max_len - 3] + "..."
