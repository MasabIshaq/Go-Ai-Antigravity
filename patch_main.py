import os

content = open('app/main.py', encoding='utf-8').read()

# Add imports
import_old = "from app.auth import login, logout, signup, user_from_token"
import_new = "from app.auth import login, logout, signup, user_from_token, validate_password, hash_password"
content = content.replace(import_old, import_new)

# Add Server State
server_state = """

class ServerStateBody(BaseModel):
    pin: str
    stopped: bool

@app.post("/api/admin/server-state")
async def api_admin_server_state(body: ServerStateBody, user: dict = Depends(current_user)):
    _verify_admin_pin(user, body.pin)
    set_server_stopped(body.stopped)
    return {"ok": True, "stopped": body.stopped}

"""

# Add Forgot Password
forgot_password = """

class ForgotPasswordBody(BaseModel):
    email: EmailStr

@app.post("/api/forgot-password")
async def api_forgot_password(body: ForgotPasswordBody, background_tasks: BackgroundTasks):
    user = get_user_by_email(body.email)
    if user:
        token = create_password_reset_token(user["id"], user["email"])
        background_tasks.add_task(send_password_reset_email, user["username"], user["email"], token)
    return {"ok": True}

class ResetPasswordBody(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)

@app.post("/api/reset-password")
async def api_reset_password(body: ResetPasswordBody):
    ok, msg = validate_password(body.new_password)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    if not use_password_reset_token(body.token, hash_password(body.new_password)):
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    return {"ok": True}

"""

if "def api_admin_server_state" not in content:
    content = content.replace("@app.post(\"/api/admin/stats\")", server_state + "\n@app.post(\"/api/admin/stats\")")

if "def api_forgot_password" not in content:
    content = content.replace("@app.post(\"/api/logout\")", forgot_password + "\n@app.post(\"/api/logout\")")

open('app/main.py', 'w', encoding='utf-8').write(content)
print('Done')
