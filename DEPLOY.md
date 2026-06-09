# Deploy Go Ai (website + API together)

Netlify only hosts static files. Go Ai needs Python for login, chat, and AI.

Use one of these hosts — they run **both** the website and API like a full app:

## Best option: Railway (easiest, like Netlify)

1. Push project to GitHub
2. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub**
3. Select your repo
4. Add environment variables:
   - `ZAI_API_KEY` = your Z.AI key
   - `SITE_URL` = your Railway URL (e.g. `https://go-ai-production.up.railway.app`)
   - `DEFAULT_MODEL` = `glm-4.5-flash`
   - `ADMIN_EMAIL` = `admin@goai.com`
   - `ADMIN_PIN` = `0786`
5. Deploy — Railway uses `Procfile` / `railway.toml` automatically
6. Open your Railway URL — full app works

## Fly.io (free tier, global)

```bash
fly launch
fly secrets set ZAI_API_KEY=your-key SITE_URL=https://your-app.fly.dev
fly deploy
```

## Koyeb

1. [koyeb.com](https://www.koyeb.com) → Create App → GitHub
2. Build: `pip install -r requirements.txt`
3. Run: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add same env variables as Railway

---

## Your app is already an API

These endpoints work for the website and external apps:

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/signup` | Create account |
| POST | `/api/login` | Log in |
| GET | `/api/me` | Current user |
| GET | `/api/chats` | List chats |
| POST | `/api/chats` | New chat |
| POST | `/api/chat` | Stream AI reply (SSE) |
| POST | `/api/report` | Report a message |

### Example: call the chat API

```bash
curl -X POST "https://YOUR-APP-URL/api/chat" \
  -H "Content-Type: application/json" \
  -b "goai_session=YOUR_SESSION_COOKIE" \
  -d '{"messages":[{"role":"user","content":"Hello"}]}'
```

Admin chat requires `admin_pin` in the body:

```json
{
  "messages": [{"role": "user", "content": "Hello"}],
  "admin_pin": "0786"
}
```

### Use API from another website

After deploying on Railway/Fly/Koyeb, your API base URL is:

```
https://your-app-url/api/
```

CORS is enabled so other frontends can call it.

---

## Do NOT use Netlify alone

Netlify cannot run Python. If you use Netlify for the UI only, chat/login will not work unless you proxy `/api` to Railway — use Railway for everything instead (one URL, simpler).
