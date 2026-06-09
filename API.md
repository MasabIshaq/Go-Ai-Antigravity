# Go Ai — API guide

Go Ai **is already an API**. The website and the API are the same Python app.

## 1. Run API locally (Windows)

Open PowerShell in the project folder:

```powershell
cd "c:\Users\Masab\OneDrive\Documents\Go Ai"
.\venv\Scripts\activate
python run.py
```

Open in browser:

- **App:** http://localhost:8000
- **API docs:** http://localhost:8000/docs
- **API base:** http://localhost:8000/api/

If you only open `index.html` or use **Netlify static**, the API will **not** work — you must run `python run.py` or deploy to Railway.

## 2. Environment (`.env`)

```
ZAI_API_KEY=your-key
SITE_URL=http://localhost:8000
DEFAULT_MODEL=glm-4.5-flash
ADMIN_EMAIL=admin@goai.com
ADMIN_PIN=0786
```

## 3. Main API endpoints

| Method | URL | Body |
|--------|-----|------|
| POST | `/api/signup` | `{"username","email","password"}` |
| POST | `/api/login` | `{"email","password"}` |
| GET | `/api/me` | (cookie session) |
| GET | `/api/chats` | (cookie session) |
| POST | `/api/chats` | (cookie session) |
| POST | `/api/chat` | `{"messages":[{"role":"user","content":"Hi"}]}` |
| POST | `/api/report` | `{"message_content","reason"}` |

Admin chat adds `"admin_pin": "0786"` to `/api/chat`.

## 4. Test chat API (after login)

1. Log in on http://localhost:8000
2. In browser DevTools → Application → Cookies, copy `goai_session`
3. Or use the interactive docs at http://localhost:8000/docs

Example with curl (replace cookie):

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -H "Cookie: goai_session=YOUR_TOKEN" \
  -d "{\"messages\":[{\"role\":\"user\",\"content\":\"Hello\"}]}"
```

## 5. Deploy API online (Railway — not Netlify)

Netlify = static files only. **Railway** runs Python + API + website together:

1. Push project to GitHub
2. https://railway.app → New Project → GitHub repo
3. Add variables: `ZAI_API_KEY`, `SITE_URL` (your Railway URL)
4. Deploy — Railway uses `Procfile` automatically

Your live API will be: `https://YOUR-APP.up.railway.app/api/`

See `DEPLOY.md` for full steps.
