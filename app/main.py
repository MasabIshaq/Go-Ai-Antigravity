import asyncio
import json
import mimetypes
import sqlite3
import uuid
from pathlib import Path

from fastapi import BackgroundTasks, Request, Cookie, Depends, FastAPI, File, Header, HTTPException, Query, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field

from app.admin_guard import is_sensitive_admin_query, last_user_message
from app.api_keys import create_api_key, list_api_keys, revoke_api_key, user_from_api_key
from app.auth import login, logout, signup, user_from_token
from app.email_service import notify_admin_new_signup, send_welcome_email
from app.config import (
    ADMIN_EMAIL,
    ADMIN_PIN,
    APP_TITLE,
    LOGO_PATH,
    ROOT,
    SITE_URL,
    SYSTEM_PROMPT,
    UPLOAD_DIR,
)
from app.database import (
    continue_shared_chat,
    create_chat,
    create_chat_share,
    delete_chat,
    db_health,
    delete_temp_chats,
    fix_report,
    get_admin_stats,
    get_chat,
    get_shared_chat,
    get_user_memory,
    init_db,
    list_chats,
    list_reports,
    rename_chat,
    save_messages,
    save_report,
    search_chats,
    sync_user_memory,
    edit_report_message,
    append_admin_reply,
)
from app.openrouter import ZAIError, stream_chat

STATIC_DIR = ROOT / "static"

app = FastAPI(title=APP_TITLE)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/css", StaticFiles(directory=STATIC_DIR / "css"), name="css")
app.mount("/js", StaticFiles(directory=STATIC_DIR / "js"), name="js")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


ALLOWED_UPLOAD_EXT = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".txt", ".md", ".py", ".js",
    ".json", ".pdf", ".csv", ".html", ".css",
}
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
TEXT_EXTRACT_EXT = {".txt", ".md", ".py", ".js", ".json", ".csv", ".html", ".css"}


@app.on_event("startup")
def startup():
    init_db()
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def current_user(goai_session: str | None = Cookie(default=None)) -> dict:
    user = user_from_token(goai_session)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


def api_key_user(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing API key. Use: Authorization: Bearer goai_...")
    user = user_from_api_key(authorization.split(" ", 1)[1].strip())
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return user


class SignupBody(BaseModel):
    username: str = Field(..., min_length=3, max_length=24)
    email: EmailStr
    password: str = Field(..., min_length=6)


class LoginBody(BaseModel):
    email: str = Field(..., min_length=3, max_length=254)
    password: str


class ChatRequest(BaseModel):
    messages: list[dict] = Field(..., min_length=1)
    admin_pin: str | None = None


class ChatUpdate(BaseModel):
    title: str | None = None
    messages: list[dict] | None = None


class AdminPinBody(BaseModel):
    pin: str = Field(..., min_length=4, max_length=12)


class AdminAccessBody(BaseModel):
    pin: str = Field(..., min_length=4, max_length=12)


class ReportBody(BaseModel):
    message_content: str = Field(..., min_length=1)
    reason: str = ""
    chat_id: str | None = None


def _cookie_secure(request: Request = None) -> bool:
    if request:
        return request.url.scheme == "https" or request.headers.get("x-forwarded-proto") == "https"
    return SITE_URL.startswith("https")


def _set_session(response: Response, token: str, request: Request = None) -> None:
    response.set_cookie(
        key="goai_session",
        value=token,
        httponly=True,
        max_age=30 * 24 * 3600,
        samesite="lax",
        secure=_cookie_secure(request),
        path="/",
    )


def _is_admin_user(user: dict) -> bool:
    return user.get("email", "").lower() == ADMIN_EMAIL.lower()


def _verify_admin_pin(user: dict, pin: str) -> None:
    if not _is_admin_user(user):
        raise HTTPException(status_code=403, detail="Not an admin account")
    if pin.strip() != ADMIN_PIN:
        raise HTTPException(status_code=401, detail="Invalid S-Pin")


def _messages_for_api(messages: list[dict]) -> list[dict]:
    api_messages = []
    for msg in messages:
        content = msg.get("content") or ""
        attachments = msg.get("attachments") or []
        if attachments:
            parts = [content] if content else []
            for att in attachments:
                name = att.get("name") or "file"
                url = att.get("url") or ""
                preview = att.get("text_preview") or ""
                if preview:
                    parts.append(f"[Attachment {name}]:\n{preview[:4000]}")
                elif att.get("type", "").startswith("image/"):
                    parts.append(f"[User attached image: {name}]({url})")
                else:
                    parts.append(f"[User attached file: {name}]({url})")
            content = "\n\n".join(parts).strip()
        api_messages.append({"role": msg["role"], "content": content})
    return api_messages


def _build_system_prompt(user: dict) -> str:
    parts = [SYSTEM_PROMPT, f"\n\nThe logged-in user's username is {user['username']}."]
    memory = get_user_memory(user["id"])
    if memory:
        parts.append(f"\n\nKnown information about this user:\n{memory}")
    parts.append(
        "\n\nUse the conversation history to remember what you and the user said earlier."
    )
    return "".join(parts)


def _with_system(messages: list[dict], user: dict) -> list[dict]:
    if messages and messages[0].get("role") == "system":
        return messages
    return [{"role": "system", "content": _build_system_prompt(user)}, *messages]


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/c/{chat_id}")
def chat_page(chat_id: str):
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/share/{token}")
def share_page(token: str):
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/developers")
def developers_page():
    return FileResponse(STATIC_DIR / "developers.html")


@app.get("/manifest.json")
def manifest():
    return FileResponse(STATIC_DIR / "manifest.json", media_type="application/manifest+json")


@app.get("/sw.js")
def service_worker():
    return FileResponse(STATIC_DIR / "sw.js", media_type="application/javascript")


@app.get("/logo.png")
def logo():
    if LOGO_PATH.exists():
        return FileResponse(LOGO_PATH, media_type="image/png")
    raise HTTPException(status_code=404)


@app.get("/api/config")
def get_config():
    return {"app_title": APP_TITLE}


@app.get("/api/health")
async def api_health():
    return db_health()


@app.get("/api/me")
async def me(
    goai_session: str | None = Cookie(default=None),
    goai_admin: str | None = Cookie(default=None),
):
    user = user_from_token(goai_session)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {
        **user,
        "is_admin_account": _is_admin_user(user),
        "admin_unlocked": _is_admin_user(user) and goai_admin == "1",
    }


@app.post("/api/signup")
async def api_signup(body: SignupBody, response: Response, background_tasks: BackgroundTasks, request: Request):
    try:
        result = signup(body.username, str(body.email), body.password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail="Email or username already taken") from exc
    except sqlite3.Error as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {exc}") from exc
    _set_session(response, result["token"], request)
    # Queue emails via FastAPI BackgroundTasks (works correctly on Vercel)
    background_tasks.add_task(notify_admin_new_signup, result["user"]["username"], result["user"]["email"])
    background_tasks.add_task(send_welcome_email, result["user"]["username"], result["user"]["email"])
    return {"user": result["user"]}


@app.post("/api/login")
async def api_login(body: LoginBody, response: Response, request: Request):
    try:
        result = login(body.email.strip(), body.password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except sqlite3.Error as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {exc}") from exc
    _set_session(response, result["token"], request)
    return {"user": result["user"]}


@app.post("/api/logout")
async def api_logout(
    response: Response,
    user: dict = Depends(current_user),
    goai_session: str | None = Cookie(default=None),
):
    delete_temp_chats(user["id"])
    logout(goai_session or "")
    response.delete_cookie("goai_session", path="/")
    response.delete_cookie("goai_admin", path="/")
    return {"ok": True}


@app.get("/api/chats")
async def api_list_chats(
    user: dict = Depends(current_user),
    q: str | None = Query(default=None),
):
    all_chats = search_chats(user["id"], q) if q else list_chats(user["id"])
    return {
        "temp": [],
        "history": [c for c in all_chats if not c["is_temp"]],
    }


class ApiKeyCreate(BaseModel):
    name: str = Field(default="Default", max_length=40)


@app.get("/api/keys")
async def api_list_keys(user: dict = Depends(current_user)):
    return list_api_keys(user["id"])


@app.post("/api/keys")
async def api_create_key(body: ApiKeyCreate, user: dict = Depends(current_user)):
    return create_api_key(user["id"], body.name)


@app.delete("/api/keys/{key_id}")
async def api_revoke_key(key_id: str, user: dict = Depends(current_user)):
    if not revoke_api_key(key_id, user["id"]):
        raise HTTPException(status_code=404, detail="API key not found")
    return {"ok": True}


@app.get("/api/chats/{chat_id}")
async def api_get_chat(chat_id: str, user: dict = Depends(current_user)):
    chat = get_chat(chat_id, user["id"])
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


@app.post("/api/chats")
async def api_new_chat(temp: bool = False, user: dict = Depends(current_user)):
    if temp:
        delete_temp_chats(user["id"])
    return create_chat(user["id"], is_temp=temp)


@app.patch("/api/chats/{chat_id}")
async def api_update_chat(
    chat_id: str, body: ChatUpdate, user: dict = Depends(current_user)
):
    if body.messages is None and body.title is None:
        raise HTTPException(status_code=400, detail="Title or messages required")
    if body.messages is None and body.title is not None:
        chat = rename_chat(chat_id, user["id"], body.title)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        return chat
    chat = save_messages(chat_id, user["id"], body.messages, body.title)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


@app.delete("/api/chats/{chat_id}")
async def api_delete_chat(chat_id: str, user: dict = Depends(current_user)):
    if not delete_chat(chat_id, user["id"]):
        raise HTTPException(status_code=404, detail="Chat not found")
    return {"ok": True}


@app.post("/api/admin/verify")
async def api_admin_verify(
    body: AdminPinBody,
    response: Response,
    user: dict = Depends(current_user),
    request: Request = None,
):
    if not _is_admin_user(user):
        raise HTTPException(status_code=403, detail="Not an admin account")
    if body.pin.strip() != ADMIN_PIN:
        raise HTTPException(status_code=401, detail="Invalid S-Pin")
    response.set_cookie(
        key="goai_admin",
        value="1",
        httponly=True,
        max_age=8 * 3600,
        samesite="lax",
        secure=_cookie_secure(request),
        path="/",
    )
    return {"ok": True}


@app.post("/api/admin/stats")
async def api_admin_stats(body: AdminAccessBody, user: dict = Depends(current_user)):
    _verify_admin_pin(user, body.pin)
    return get_admin_stats()


@app.post("/api/admin/reports")
async def api_admin_reports(
    body: AdminAccessBody,
    user: dict = Depends(current_user),
    status: str | None = None,
):
    _verify_admin_pin(user, body.pin)
    return list_reports(status)


@app.patch("/api/admin/reports/{report_id}/fix")
async def api_fix_report(
    report_id: str, body: AdminAccessBody, user: dict = Depends(current_user)
):
    _verify_admin_pin(user, body.pin)
    if not fix_report(report_id):
        raise HTTPException(status_code=404, detail="Report not found")
    return {"ok": True}

class EditReportBody(BaseModel):
    pin: str
    message_content: str

@app.patch("/api/admin/reports/{report_id}/edit")
async def api_edit_report(
    report_id: str, body: EditReportBody, user: dict = Depends(current_user)
):
    _verify_admin_pin(user, body.pin)
    if not edit_report_message(report_id, body.message_content):
        raise HTTPException(status_code=404, detail="Report not found")
    return {"ok": True}

class AdminReplyBody(BaseModel):
    pin: str
    content: str

@app.post("/api/admin/chats/{chat_id}/reply")
async def api_admin_chat_reply(
    chat_id: str, body: AdminReplyBody, user: dict = Depends(current_user)
):
    _verify_admin_pin(user, body.pin)
    append_admin_reply(chat_id, body.content)
    return {"ok": True}


@app.post("/api/chats/{chat_id}/share")
async def api_share_chat(chat_id: str, user: dict = Depends(current_user)):
    token = create_chat_share(chat_id, user["id"])
    if not token:
        raise HTTPException(status_code=404, detail="Chat not found")
    base = SITE_URL.rstrip("/")
    return {"token": token, "url": f"{base}/share/{token}", "chat_url": f"{base}/c/{chat_id}"}


@app.get("/api/share/{token}")
async def api_get_share(token: str):
    shared = get_shared_chat(token)
    if not shared:
        raise HTTPException(status_code=404, detail="Share link not found")
    return shared


@app.post("/api/share/{token}/continue")
async def api_continue_share(token: str, user: dict = Depends(current_user)):
    chat = continue_shared_chat(token, user["id"])
    if not chat:
        raise HTTPException(status_code=404, detail="Share link not found or empty")
    return chat


@app.post("/api/upload")
async def api_upload(file: UploadFile = File(...), user: dict = Depends(current_user)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected")
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_UPLOAD_EXT:
        raise HTTPException(status_code=400, detail="File type not allowed")
    data = await file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail="File too large (max 5MB)")
    file_id = str(uuid.uuid4())
    dest = UPLOAD_DIR / f"{file_id}{ext}"
    dest.write_bytes(data)
    mime = file.content_type or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"
    text_preview = ""
    if ext in TEXT_EXTRACT_EXT:
        try:
            text_preview = data.decode("utf-8", errors="replace")[:8000]
        except Exception:
            text_preview = ""
    return {
        "id": file_id,
        "name": file.filename,
        "url": f"/api/files/{file_id}{ext}",
        "type": mime,
        "size": len(data),
        "text_preview": text_preview,
    }


@app.get("/api/files/{filename}")
async def api_get_file(filename: str):
    safe = Path(filename).name
    path = UPLOAD_DIR / safe
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    mime = mimetypes.guess_type(safe)[0] or "application/octet-stream"
    return FileResponse(path, media_type=mime)


@app.post("/api/report")
async def api_report(body: ReportBody, user: dict = Depends(current_user)):
    save_report(user["id"], body.message_content, body.reason, body.chat_id)
    return {"ok": True}


@app.get("/api/v1/chats")
async def v1_list_chats(user: dict = Depends(api_key_user)):
    all_chats = list_chats(user["id"])
    return {"chats": all_chats}


@app.post("/api/v1/chat")
async def v1_chat_stream(body: ChatRequest, user: dict = Depends(api_key_user)):
    await asyncio.to_thread(sync_user_memory, user["id"], body.messages)
    api_messages = await asyncio.to_thread(_with_system, _messages_for_api(body.messages), user)

    async def event_generator():
        try:
            async for token in stream_chat(api_messages):
                yield f"data: {json.dumps({'content': token})}\n\n"
        except ZAIError:
            yield f"data: {json.dumps({'error': 'AI request failed'})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/api/chat")
async def api_chat_stream(body: ChatRequest, user: dict = Depends(current_user)):
    user_text = last_user_message(body.messages)
    if _is_admin_user(user) and is_sensitive_admin_query(user_text):
        if not body.admin_pin or body.admin_pin.strip() != ADMIN_PIN:
            raise HTTPException(
                status_code=401,
                detail="S-Pin required for questions about Go Ai internals, API, or technical details.",
            )
    await asyncio.to_thread(sync_user_memory, user["id"], body.messages)
    api_messages = await asyncio.to_thread(_with_system, _messages_for_api(body.messages), user)

    async def event_generator():
        used_api = False
        try:
            async for token in stream_chat(api_messages):
                used_api = True
                yield f"data: {json.dumps({'content': token})}\n\n"
        except ZAIError as exc:
            if used_api:
                yield "data: [DONE]\n\n"
                return
            yield f"data: {json.dumps({'error': 'Could not get a response. Check your API key and try again.'})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
