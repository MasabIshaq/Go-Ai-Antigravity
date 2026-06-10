with open('app/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add Request import
content = content.replace("from fastapi import BackgroundTasks,", "from fastapi import BackgroundTasks, Request,")

# Update _cookie_secure
old_cookie = '''def _cookie_secure() -> bool:
    return SITE_URL.startswith("https")'''
new_cookie = '''def _cookie_secure(request: Request = None) -> bool:
    if request:
        return request.url.scheme == "https" or request.headers.get("x-forwarded-proto") == "https"
    return SITE_URL.startswith("https")'''
content = content.replace(old_cookie, new_cookie)

# Update _set_session
old_set = '''def _set_session(response: Response, token: str) -> None:
    response.set_cookie(
        key="goai_session",
        value=token,
        httponly=True,
        max_age=30 * 24 * 3600,
        samesite="lax",
        secure=_cookie_secure(),
        path="/",
    )'''
new_set = '''def _set_session(response: Response, token: str, request: Request = None) -> None:
    response.set_cookie(
        key="goai_session",
        value=token,
        httponly=True,
        max_age=30 * 24 * 3600,
        samesite="lax",
        secure=_cookie_secure(request),
        path="/",
    )'''
content = content.replace(old_set, new_set)

# Update api_signup
old_signup = '''def api_signup(body: SignupBody, response: Response, background_tasks: BackgroundTasks):'''
new_signup = '''def api_signup(body: SignupBody, response: Response, background_tasks: BackgroundTasks, request: Request):'''
content = content.replace(old_signup, new_signup)

old_signup_call = '''    _set_session(response, result["token"])'''
new_signup_call = '''    _set_session(response, result["token"], request)'''
content = content.replace(old_signup_call, new_signup_call)

# Update api_login
old_login = '''def api_login(body: LoginBody, response: Response):'''
new_login = '''def api_login(body: LoginBody, response: Response, request: Request):'''
content = content.replace(old_login, new_login)

old_login_call = '''    _set_session(response, result["token"])'''
new_login_call = '''    _set_session(response, result["token"], request)'''
content = content.replace(old_login_call, new_login_call)

# Update admin verify
old_admin = '''def api_admin_verify(
    body: AdminPinBody,
    response: Response,
    user: dict = Depends(current_user),
):'''
new_admin = '''def api_admin_verify(
    body: AdminPinBody,
    response: Response,
    user: dict = Depends(current_user),
    request: Request = None,
):'''
content = content.replace(old_admin, new_admin)

old_admin_sec = '''secure=_cookie_secure(),'''
new_admin_sec = '''secure=_cookie_secure(request),'''
# careful, this appears in _set_session too, but we already replaced _set_session, so it only hits the one in api_admin_verify (and maybe others?)
# Let's count them or replace specific
content = content.replace("secure=_cookie_secure(),", "secure=_cookie_secure(request),")

with open('app/main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Cookie issue patched.")
