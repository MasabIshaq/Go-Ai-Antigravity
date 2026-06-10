import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone

from app.config import DATA_DIR, DB_PATH, TURSO_DATABASE_URL, TURSO_AUTH_TOKEN

_USE_TURSO = bool(TURSO_DATABASE_URL and TURSO_AUTH_TOKEN)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_db() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with get_db() as conn:
        # Create all tables
        statements = [
            """CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                memory_notes TEXT NOT NULL DEFAULT ''
            )""",
            """CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                expires_at TEXT NOT NULL
            )""",
            """CREATE TABLE IF NOT EXISTS chats (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL DEFAULT 'New chat',
                is_temp INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )""",
            """CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                chat_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                attachments TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL
            )""",
            "CREATE INDEX IF NOT EXISTS idx_chats_user ON chats(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_messages_chat ON messages(chat_id)",
            """CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                chat_id TEXT,
                message_content TEXT NOT NULL,
                reason TEXT,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
            )""",
            """CREATE TABLE IF NOT EXISTS chat_shares (
                token TEXT PRIMARY KEY,
                chat_id TEXT NOT NULL,
                owner_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                messages_snapshot TEXT NOT NULL DEFAULT '[]'
            )""",
            """CREATE TABLE IF NOT EXISTS user_api_keys (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                key_hash TEXT NOT NULL UNIQUE,
                key_prefix TEXT NOT NULL,
                name TEXT NOT NULL DEFAULT 'Default',
                created_at TEXT NOT NULL,
                last_used TEXT
            )""",
        ]
        for stmt in statements:
            conn.execute(stmt)

        # Safe migrations — skip if column already exists
        migrations = [
            "ALTER TABLE messages ADD COLUMN attachments TEXT NOT NULL DEFAULT '[]'",
            "ALTER TABLE users ADD COLUMN memory_notes TEXT NOT NULL DEFAULT ''",
            "ALTER TABLE reports ADD COLUMN status TEXT NOT NULL DEFAULT 'pending'",
            "ALTER TABLE chat_shares ADD COLUMN messages_snapshot TEXT NOT NULL DEFAULT '[]'",
        ]
        for stmt in migrations:
            try:
                conn.execute(stmt)
            except Exception:
                pass  # Column already exists — safe to skip

        try:
            conn.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username_ci "
                "ON users(LOWER(username))"
            )
        except Exception:
            pass


class TursoRowWrapper:
    def __init__(self, row, columns):
        self._row = row
        self._columns = columns
        
    def __getitem__(self, key):
        if isinstance(key, int):
            return self._row[key]
        if key in self._columns:
            idx = self._columns.index(key)
            return self._row[idx]
        raise KeyError(key)
        
    def keys(self):
        return self._columns

class TursoCursorWrapper:
    def __init__(self, rs):
        self.rs = rs
        
    def fetchone(self):
        if self.rs and self.rs.rows:
            return TursoRowWrapper(self.rs.rows[0], self.rs.columns)
        return None
        
    def fetchall(self):
        if self.rs and self.rs.rows:
            return [TursoRowWrapper(row, self.rs.columns) for row in self.rs.rows]
        return []

class TursoConnectionWrapper:
    def __init__(self, client):
        self.client = client
        self.row_factory = None
        
    def execute(self, sql, parameters=()):
        # Convert sqlite3 ? placeholders to positional args or let libsql_client handle them
        rs = self.client.execute(sql, parameters)
        return TursoCursorWrapper(rs)
                
    def commit(self):
        pass
        
    def rollback(self):
        pass

    def close(self):
        self.client.close()

@contextmanager
def get_db():
    if _USE_TURSO:
        import libsql_client
        client = libsql_client.create_client_sync(
            url=TURSO_DATABASE_URL,
            auth_token=TURSO_AUTH_TOKEN,
        )
        conn = TursoConnectionWrapper(client)
    else:
        conn = sqlite3.connect(str(DB_PATH), timeout=30, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def db_health() -> dict:
    try:
        with get_db() as conn:
            users = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
        return {"ok": True, "users": users, "path": str(DB_PATH)}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "path": str(DB_PATH)}


def create_user(username: str, email: str, password_hash: str) -> dict:
    user_id = str(uuid.uuid4())
    username = username.strip()
    email = email.strip().lower()
    if get_user_by_username(username):
        raise sqlite3.IntegrityError("username taken")
    if get_user_by_email(email):
        raise sqlite3.IntegrityError("email taken")
    with get_db() as conn:
        conn.execute(
            """INSERT INTO users
               (id, username, email, password_hash, created_at, memory_notes)
               VALUES (?,?,?,?,?,?)""",
            (user_id, username, email, password_hash, _now(), ""),
        )
    return {"id": user_id, "username": username, "email": email}


def get_user_by_email(email: str) -> sqlite3.Row | None:
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE email = ?", (email.lower(),)
        ).fetchone()


def get_user_by_username(username: str) -> sqlite3.Row | None:
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE LOWER(username) = LOWER(?)",
            (username.strip(),),
        ).fetchone()


def get_user_by_id(user_id: str) -> sqlite3.Row | None:
    with get_db() as conn:
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def create_session(user_id: str, token: str, expires_at: str) -> None:
    with get_db() as conn:
        conn.execute(
            "INSERT INTO sessions (token, user_id, expires_at) VALUES (?,?,?)",
            (token, user_id, expires_at),
        )


def get_session(token: str) -> sqlite3.Row | None:
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM sessions WHERE token = ?", (token,)
        ).fetchone()


def delete_session(token: str) -> None:
    with get_db() as conn:
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))


def create_chat(user_id: str, is_temp: bool = False, title: str = "New chat") -> dict:
    chat_id = str(uuid.uuid4())
    now = _now()
    with get_db() as conn:
        conn.execute(
            """INSERT INTO chats (id, user_id, title, is_temp, created_at, updated_at)
               VALUES (?,?,?,?,?,?)""",
            (chat_id, user_id, title, 1 if is_temp else 0, now, now),
        )
    return {
        "id": chat_id,
        "title": title,
        "is_temp": is_temp,
        "messages": [],
        "created_at": now,
        "updated_at": now,
    }


def list_chats(user_id: str) -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            """SELECT c.*, COUNT(m.id) as message_count
               FROM chats c
               LEFT JOIN messages m ON m.chat_id = c.id
               WHERE c.user_id = ?
               GROUP BY c.id
               ORDER BY c.updated_at DESC""",
            (user_id,),
        ).fetchall()
    return [
        {
            "id": r["id"],
            "title": r["title"],
            "is_temp": bool(r["is_temp"]),
            "updated_at": r["updated_at"],
            "message_count": r["message_count"],
        }
        for r in rows
    ]


def _msg_dict(row: sqlite3.Row) -> dict:
    attachments = []
    if "attachments" in row.keys() and row["attachments"]:
        try:
            attachments = json.loads(row["attachments"])
        except json.JSONDecodeError:
            attachments = []
    return {
        "role": row["role"],
        "content": row["content"],
        "attachments": attachments,
    }


def get_chat(chat_id: str, user_id: str) -> dict | None:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM chats WHERE id = ? AND user_id = ?",
            (chat_id, user_id),
        ).fetchone()
        if not row:
            return None
        msgs = conn.execute(
            "SELECT role, content, attachments FROM messages WHERE chat_id = ? ORDER BY created_at",
            (chat_id,),
        ).fetchall()
    return {
        "id": row["id"],
        "title": row["title"],
        "is_temp": bool(row["is_temp"]),
        "messages": [_msg_dict(m) for m in msgs],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def save_messages(chat_id: str, user_id: str, messages: list[dict], title: str | None = None) -> dict | None:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM chats WHERE id = ? AND user_id = ?",
            (chat_id, user_id),
        ).fetchone()
        if not row:
            return None
        conn.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
        for msg in messages:
            attachments = json.dumps(msg.get("attachments") or [])
            conn.execute(
                """INSERT INTO messages
                   (id, chat_id, role, content, attachments, created_at)
                   VALUES (?,?,?,?,?,?)""",
                (
                    str(uuid.uuid4()),
                    chat_id,
                    msg["role"],
                    msg["content"],
                    attachments,
                    _now(),
                ),
            )
        new_title = title or row["title"]
        if messages and row["title"] == "New chat":
            first = next((m["content"] for m in messages if m["role"] == "user"), None)
            if first:
                new_title = title_from_message(first)
        is_temp = row["is_temp"]
        if messages and is_temp:
            is_temp = 0
        now = _now()
        conn.execute(
            "UPDATE chats SET title = ?, is_temp = ?, updated_at = ? WHERE id = ?",
            (new_title, is_temp, now, chat_id),
        )
    sync_user_memory(user_id, messages)
    return get_chat(chat_id, user_id)


def rename_chat(chat_id: str, user_id: str, title: str) -> dict | None:
    clean = " ".join(title.split()).strip() or "New chat"
    with get_db() as conn:
        row = conn.execute(
            "SELECT id FROM chats WHERE id = ? AND user_id = ?",
            (chat_id, user_id),
        ).fetchone()
        if not row:
            return None
        conn.execute(
            "UPDATE chats SET title = ?, updated_at = ? WHERE id = ?",
            (clean[:80], _now(), chat_id),
        )
    return get_chat(chat_id, user_id)


def delete_chat(chat_id: str, user_id: str) -> bool:
    with get_db() as conn:
        row = conn.execute(
            "SELECT id FROM chats WHERE id = ? AND user_id = ?",
            (chat_id, user_id),
        ).fetchone()
        if not row:
            return False
        conn.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
        conn.execute("DELETE FROM chat_shares WHERE chat_id = ?", (chat_id,))
        conn.execute("DELETE FROM reports WHERE chat_id = ?", (chat_id,))
        conn.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
    return True


def delete_temp_chats(user_id: str) -> None:
    with get_db() as conn:
        temps = conn.execute(
            "SELECT id FROM chats WHERE user_id = ? AND is_temp = 1",
            (user_id,),
        ).fetchall()
        for t in temps:
            conn.execute("DELETE FROM messages WHERE chat_id = ?", (t["id"],))
            conn.execute("DELETE FROM chat_shares WHERE chat_id = ?", (t["id"],))
            conn.execute("DELETE FROM reports WHERE chat_id = ?", (t["id"],))
            conn.execute("DELETE FROM chats WHERE id = ?", (t["id"],))


def get_user_memory(user_id: str) -> str:
    with get_db() as conn:
        row = conn.execute(
            "SELECT memory_notes FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    return (row["memory_notes"] or "").strip() if row else ""


def append_user_memory(user_id: str, note: str) -> None:
    note = " ".join(note.split()).strip()
    if not note:
        return
    with get_db() as conn:
        row = conn.execute(
            "SELECT memory_notes FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        if not row:
            return
        existing = (row["memory_notes"] or "").strip()
        if note in existing:
            return
        combined = f"{existing}\n{note}".strip() if existing else note
        conn.execute(
            "UPDATE users SET memory_notes = ? WHERE id = ?",
            (combined[:4000], user_id),
        )


def sync_user_memory(user_id: str, messages: list[dict]) -> None:
    for msg in messages:
        if msg.get("role") != "user":
            continue
        text = (msg.get("content") or "").strip()
        if not text:
            continue
        lower = text.lower()
        if lower.startswith("my name is "):
            append_user_memory(user_id, f"User's name: {text[11:].strip()}")
        elif lower.startswith("call me "):
            append_user_memory(user_id, f"User prefers to be called: {text[8:].strip()}")
        elif "remember that " in lower:
            idx = lower.index("remember that ")
            append_user_memory(user_id, text[idx + 14 :].strip())
        elif lower.startswith("remember "):
            append_user_memory(user_id, text[9:].strip())
        elif lower.startswith("i am from "):
            append_user_memory(user_id, f"User is from: {text[10:].strip()}")
        elif lower.startswith("i live in "):
            append_user_memory(user_id, f"User lives in: {text[10:].strip()}")
        elif lower.startswith("i work as ") or lower.startswith("i work at "):
            append_user_memory(user_id, f"User work: {text[10:].strip()}")


def save_report(
    user_id: str, message_content: str, reason: str = "", chat_id: str | None = None
) -> None:
    with get_db() as conn:
        conn.execute(
            """INSERT INTO reports
               (id, user_id, chat_id, message_content, reason, created_at, status)
               VALUES (?,?,?,?,?,?,?)""",
            (
                str(uuid.uuid4()),
                user_id,
                chat_id,
                message_content[:8000],
                reason[:500],
                _now(),
                "pending",
            ),
        )


def list_reports(status: str | None = None) -> list[dict]:
    with get_db() as conn:
        if status:
            rows = conn.execute(
                """SELECT r.*, u.username, u.email
                   FROM reports r
                   JOIN users u ON u.id = r.user_id
                   WHERE r.status = ?
                   ORDER BY r.created_at DESC""",
                (status,),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT r.*, u.username, u.email
                   FROM reports r
                   JOIN users u ON u.id = r.user_id
                   ORDER BY r.created_at DESC"""
            ).fetchall()
    return [
        {
            "id": r["id"],
            "user_id": r["user_id"],
            "username": r["username"],
            "email": r["email"],
            "chat_id": r["chat_id"],
            "message_content": r["message_content"],
            "reason": r["reason"] or "",
            "status": r["status"] if "status" in r.keys() else "pending",
            "created_at": r["created_at"],
        }
        for r in rows
    ]


def fix_report(report_id: str) -> bool:
    with get_db() as conn:
        row = conn.execute("SELECT id FROM reports WHERE id = ?", (report_id,)).fetchone()
        if not row:
            return False
        conn.execute(
            "UPDATE reports SET status = ? WHERE id = ?",
            ("fixed", report_id),
        )
    return True


def edit_report_message(report_id: str, new_content: str) -> bool:
    with get_db() as conn:
        row = conn.execute("SELECT id FROM reports WHERE id = ?", (report_id,)).fetchone()
        if not row:
            return False
        conn.execute(
            "UPDATE reports SET message_content = ? WHERE id = ?",
            (new_content, report_id),
        )
    return True


def append_admin_reply(chat_id: str, content: str) -> None:
    with get_db() as conn:
        conn.execute(
            "INSERT INTO messages (id, chat_id, role, content, created_at, attachments) VALUES (?,?,?,?,?,?)",
            (str(uuid.uuid4()), chat_id, "assistant", content, _now(), "[]"),
        )


def get_admin_stats() -> dict:
    with get_db() as conn:
        users = conn.execute("SELECT COUNT(*) as c FROM users").fetchone()["c"]
        chats = conn.execute("SELECT COUNT(*) as c FROM chats").fetchone()["c"]
        messages = conn.execute("SELECT COUNT(*) as c FROM messages").fetchone()["c"]
        reports = conn.execute("SELECT COUNT(*) as c FROM reports").fetchone()["c"]
        pending = conn.execute(
            "SELECT COUNT(*) as c FROM reports WHERE status = 'pending'"
        ).fetchone()["c"]
    return {
        "users": users,
        "chats": chats,
        "messages": messages,
        "reports": reports,
        "pending_reports": pending,
    }


def create_chat_share(chat_id: str, user_id: str) -> str | None:
    with get_db() as conn:
        row = conn.execute(
            "SELECT id FROM chats WHERE id = ? AND user_id = ?",
            (chat_id, user_id),
        ).fetchone()
        if not row:
            return None
        token = secrets.token_urlsafe(16)
        
        msgs = conn.execute(
            "SELECT role, content, attachments FROM messages WHERE chat_id = ? ORDER BY created_at",
            (chat_id,),
        ).fetchall()
        msgs_list = [_msg_dict(m) for m in msgs]
        
        conn.execute(
            "INSERT INTO chat_shares (token, chat_id, owner_id, created_at, messages_snapshot) VALUES (?,?,?,?,?)",
            (token, chat_id, user_id, _now(), json.dumps(msgs_list)),
        )
    return token


def get_shared_chat(token: str) -> dict | None:
    with get_db() as conn:
        share = conn.execute(
            "SELECT * FROM chat_shares WHERE token = ?", (token,)
        ).fetchone()
        if not share:
            return None
        chat = conn.execute(
            "SELECT * FROM chats WHERE id = ?", (share["chat_id"],)
        ).fetchone()
        if not chat:
            return None
        owner = conn.execute(
            "SELECT username FROM users WHERE id = ?", (share["owner_id"],)
        ).fetchone()
        try:
            msgs = json.loads(share["messages_snapshot"])
        except Exception:
            msgs = []
    return {
        "token": token,
        "title": chat["title"],
        "shared_by": owner["username"] if owner else "Someone",
        "messages": msgs,
        "message_count": len(msgs),
    }


def search_chats(user_id: str, query: str) -> list[dict]:
    q = f"%{query.strip().lower()}%"
    if not query.strip():
        return list_chats(user_id)
    with get_db() as conn:
        rows = conn.execute(
            """SELECT DISTINCT c.id, c.title, c.is_temp, c.updated_at,
                      (SELECT COUNT(*) FROM messages m2 WHERE m2.chat_id = c.id) AS message_count
               FROM chats c
               LEFT JOIN messages m ON m.chat_id = c.id
               WHERE c.user_id = ?
                 AND (
                   LOWER(c.title) LIKE ?
                   OR LOWER(m.content) LIKE ?
                   OR LOWER(COALESCE(m.attachments, '')) LIKE ?
                 )
               ORDER BY c.updated_at DESC""",
            (user_id, q, q, q),
        ).fetchall()
    return [
        {
            "id": r["id"],
            "title": r["title"],
            "is_temp": bool(r["is_temp"]),
            "updated_at": r["updated_at"],
            "message_count": r["message_count"],
        }
        for r in rows
    ]


def continue_shared_chat(token: str, user_id: str) -> dict | None:
    shared = get_shared_chat(token)
    if not shared or not shared["messages"]:
        return None
    chat = create_chat(user_id, is_temp=False, title=f"Shared: {shared['title'][:50]}")
    return save_messages(chat["id"], user_id, shared["messages"])


def title_from_message(text: str, max_len: int = 40) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= max_len:
        return cleaned or "New chat"
    return cleaned[: max_len - 3] + "..."
