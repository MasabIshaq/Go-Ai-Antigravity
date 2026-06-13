content = open('app/database.py', encoding='utf-8').read()

addition = """

# ─── Server stop/start ────────────────────────────────────────────────────────

def get_server_stopped():
    with get_db() as conn:
        row = conn.execute(
            "SELECT value FROM server_settings WHERE key = 'server_stopped'"
        ).fetchone()
        return bool(row and row["value"] == "1")


def set_server_stopped(stopped):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO server_settings(key, value) VALUES('server_stopped', ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            ("1" if stopped else "0",),
        )


# ─── Password reset ───────────────────────────────────────────────────────────

def create_password_reset_token(user_id, email):
    import secrets
    with get_db() as conn:
        conn.execute(
            "UPDATE password_reset_tokens SET used=1 WHERE user_id=? AND used=0",
            (user_id,),
        )
    token = secrets.token_urlsafe(32)
    with get_db() as conn:
        conn.execute(
            "INSERT INTO password_reset_tokens(token, user_id, email, created_at) VALUES(?,?,?,?)",
            (token, user_id, email, _now()),
        )
    return token


def get_password_reset_token(token):
    from datetime import timedelta, datetime, timezone
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM password_reset_tokens WHERE token=? AND used=0",
            (token,),
        ).fetchone()
    if not row:
        return None
    created = datetime.fromisoformat(row["created_at"])
    if datetime.now(timezone.utc) - created > timedelta(minutes=15):
        return None
    return dict(row)


def use_password_reset_token(token, new_password_hash):
    data = get_password_reset_token(token)
    if not data:
        return False
    with get_db() as conn:
        conn.execute(
            "UPDATE users SET password_hash=? WHERE id=?",
            (new_password_hash, data["user_id"]),
        )
        conn.execute(
            "UPDATE password_reset_tokens SET used=1 WHERE token=?",
            (token,),
        )
    return True
"""

open('app/database.py', 'w', encoding='utf-8').write(content + addition)
print('Done')
