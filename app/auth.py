import re
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt

from app.database import (
    create_session,
    create_user,
    delete_session,
    get_session,
    get_user_by_email,
    get_user_by_id,
    get_user_by_username,
)

EMAIL_RE = re.compile(r"^[\w.+-]+@[\w.-]+\.\w+$")
USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,24}$")


def validate_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email.strip()))


def validate_username(username: str) -> bool:
    return bool(USERNAME_RE.match(username.strip()))


def validate_password(password: str) -> tuple[bool, str]:
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    return True, ""


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def signup(username: str, email: str, password: str) -> dict:
    username = username.strip()
    email = email.strip().lower()

    if not validate_username(username):
        raise ValueError("Username: 3–24 letters, numbers, underscore only")
    if not validate_email(email):
        raise ValueError("Invalid email address")
    ok, msg = validate_password(password)
    if not ok:
        raise ValueError(msg)
    if get_user_by_email(email):
        raise ValueError("Email already registered")
    if get_user_by_username(username):
        raise ValueError("Username already taken")

    user = create_user(username, email, hash_password(password))
    token, expires = _new_session(user["id"])
    return {"user": user, "token": token, "expires_at": expires}


def login(email: str, password: str) -> dict:
    identifier = email.strip()
    user = get_user_by_email(identifier.lower())
    if not user:
        user = get_user_by_username(identifier)
    if not user or not verify_password(password, user["password_hash"]):
        raise ValueError("Invalid email or password")
    token, expires = _new_session(user["id"])
    return {
        "user": {"id": user["id"], "username": user["username"], "email": user["email"]},
        "token": token,
        "expires_at": expires,
    }


def logout(token: str) -> None:
    if token:
        delete_session(token)


def user_from_token(token: str | None) -> dict | None:
    if not token:
        return None
    session = get_session(token)
    if not session:
        return None
    expires = datetime.fromisoformat(session["expires_at"])
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < datetime.now(timezone.utc):
        delete_session(token)
        return None
    user = get_user_by_id(session["user_id"])
    if not user:
        return None
    return {"id": user["id"], "username": user["username"], "email": user["email"]}


def _new_session(user_id: str) -> tuple[str, str]:
    token = secrets.token_urlsafe(32)
    expires = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    create_session(user_id, token, expires)
    return token, expires
