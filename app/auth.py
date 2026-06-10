import re
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.config import SECRET_KEY
from app.database import (
    create_user,
    get_user_by_email,
    get_user_by_username,
)

EMAIL_RE = re.compile(r"^[\w.+-]+@[\w.-]+\.\w+$")
USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,24}$")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_DAYS = 30


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


def _create_jwt(user: dict) -> tuple[str, str]:
    """Create a signed JWT with user info embedded — no DB session needed."""
    expires = datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRE_DAYS)
    payload = {
        "sub": user["id"],
        "username": user["username"],
        "email": user["email"],
        "exp": expires,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token, expires.isoformat()


def user_from_token(token: str | None) -> dict | None:
    """Verify JWT and return user — works across ALL serverless instances."""
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return {
            "id": payload["sub"],
            "username": payload["username"],
            "email": payload["email"],
        }
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def signup(username: str, email: str, password: str) -> dict:
    username = username.strip()
    email = email.strip().lower()

    if not validate_username(username):
        raise ValueError("Username: 3\u201324 letters, numbers, underscore only")
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
    token, expires = _create_jwt(user)
    return {"user": user, "token": token, "expires_at": expires}


def login(email: str, password: str) -> dict:
    identifier = email.strip()
    user = get_user_by_email(identifier.lower())
    if not user:
        user = get_user_by_username(identifier)
    if not user or not verify_password(password, user["password_hash"]):
        raise ValueError("Invalid email or password")
    user_dict = {"id": user["id"], "username": user["username"], "email": user["email"]}
    token, expires = _create_jwt(user_dict)
    return {"user": user_dict, "token": token, "expires_at": expires}


def logout(token: str) -> None:
    # JWT is stateless — logout is handled by deleting the cookie client-side
    pass
