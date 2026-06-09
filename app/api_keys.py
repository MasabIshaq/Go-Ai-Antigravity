import hashlib
import secrets
import uuid
from datetime import datetime, timezone

from app.database import get_db


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode()).hexdigest()


def create_api_key(user_id: str, name: str = "Default") -> dict:
    raw_key = f"goai_{secrets.token_urlsafe(32)}"
    key_id = str(uuid.uuid4())
    prefix = raw_key[:12]
    with get_db() as conn:
        conn.execute(
            """INSERT INTO user_api_keys
               (id, user_id, key_hash, key_prefix, name, created_at)
               VALUES (?,?,?,?,?,?)""",
            (key_id, user_id, _hash_key(raw_key), prefix, name[:40], _now()),
        )
    return {"id": key_id, "name": name[:40], "key": raw_key, "prefix": prefix}


def list_api_keys(user_id: str) -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            """SELECT id, key_prefix, name, created_at, last_used
               FROM user_api_keys WHERE user_id = ?
               ORDER BY created_at DESC""",
            (user_id,),
        ).fetchall()
    return [
        {
            "id": r["id"],
            "prefix": r["key_prefix"],
            "name": r["name"],
            "created_at": r["created_at"],
            "last_used": r["last_used"],
        }
        for r in rows
    ]


def revoke_api_key(key_id: str, user_id: str) -> bool:
    with get_db() as conn:
        row = conn.execute(
            "SELECT id FROM user_api_keys WHERE id = ? AND user_id = ?",
            (key_id, user_id),
        ).fetchone()
        if not row:
            return False
        conn.execute("DELETE FROM user_api_keys WHERE id = ?", (key_id,))
    return True


def user_from_api_key(raw_key: str | None) -> dict | None:
    if not raw_key or not raw_key.startswith("goai_"):
        return None
    key_hash = _hash_key(raw_key)
    with get_db() as conn:
        row = conn.execute(
            """SELECT k.user_id, u.id, u.username, u.email
               FROM user_api_keys k
               JOIN users u ON u.id = k.user_id
               WHERE k.key_hash = ?""",
            (key_hash,),
        ).fetchone()
        if not row:
            return None
        conn.execute(
            "UPDATE user_api_keys SET last_used = ? WHERE key_hash = ?",
            (_now(), key_hash),
        )
    return {"id": row["id"], "username": row["username"], "email": row["email"]}
