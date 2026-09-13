import os

# Add to app/database.py
DB_PATCH = """
def update_user_password(user_id: str, new_hash: str) -> None:
    with _get_conn() as conn:
        conn.execute("UPDATE users SET password_hash=?, otp_code=NULL, otp_expires_at=NULL WHERE id=?", (new_hash, user_id))
"""

with open("app/database.py", "r", encoding="utf-8") as f:
    db_code = f.read()
if "update_user_password" not in db_code:
    with open("app/database.py", "a", encoding="utf-8") as f:
        f.write(DB_PATCH)

# Add to app/main.py
MAIN_PATCH = """
class ForgotPasswordReq(BaseModel):
    email: str

class ResetPasswordReq(BaseModel):
    email: str
    code: str
    new_password: str

@app.post("/api/auth/forgot-password")
async def api_forgot_password(body: ForgotPasswordReq):
    from app.database import get_user_by_email, set_user_otp
    from app.email_service import send_password_reset_email
    import random
    from datetime import datetime, timedelta, timezone
    user = get_user_by_email(body.email.strip().lower())
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    otp = f"{random.randint(100000, 999999)}"
    expires = (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat()
    set_user_otp(user["id"], otp, expires)
    await send_password_reset_email(user["username"], user["email"], otp)
    return {"ok": True}

@app.post("/api/auth/reset-password")
async def api_reset_password(body: ResetPasswordReq):
    from app.database import get_user_by_email, verify_user_otp, update_user_password
    from app.auth import hash_password, validate_password
    user = get_user_by_email(body.email.strip().lower())
    if not user:
        raise HTTPException(status_code=404, detail="Invalid email or code")
    if not verify_user_otp(user["id"], body.code.strip()):
        raise HTTPException(status_code=400, detail="Invalid or expired reset code")
    ok, msg = validate_password(body.new_password)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    update_user_password(user["id"], hash_password(body.new_password))
    return {"ok": True}
"""

with open("app/main.py", "r", encoding="utf-8") as f:
    main_code = f.read()
if "/api/auth/forgot-password" not in main_code:
    with open("app/main.py", "a", encoding="utf-8") as f:
        f.write(MAIN_PATCH)

print("OTP Backend Patched successfully")
