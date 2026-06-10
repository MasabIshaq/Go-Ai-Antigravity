import os
import sys
from pathlib import Path

from dotenv import load_dotenv

if getattr(sys, 'frozen', False):
    ROOT = Path(sys._MEIPASS)
else:
    ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

APP_TITLE = os.getenv("APP_TITLE", "Go Ai")
SECRET_KEY = os.getenv("SECRET_KEY", "go-ai-change-this-secret-in-production")
ZAI_API_KEY = os.getenv("ZAI_API_KEY", "")
ZAI_BASE_URL = os.getenv("ZAI_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "glm-4.5-flash")
SITE_URL = os.getenv("SITE_URL", "http://localhost:8000")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@goai.com")
NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL", "masabishaq452@gmail.com")
ADMIN_PIN = os.getenv("ADMIN_PIN", "0786")
GMAIL_USER = os.getenv("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
TURSO_DATABASE_URL = os.getenv("TURSO_DATABASE_URL", "")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN", "")
# On Vercel the project filesystem is read-only — use /tmp instead
# On HuggingFace Spaces, /app/data persists in the container
if getattr(sys, 'frozen', False):
    DATA_DIR = Path.home() / ".goai" / "data"
elif os.getenv("VERCEL"):
    DATA_DIR = Path("/tmp/goai_data")
else:
    DATA_DIR = ROOT / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
DB_PATH = DATA_DIR / "goai.db"
STATIC_DIR = ROOT / "static"
LOGO_PATH = ROOT / "logo.png"
if not LOGO_PATH.exists() and (STATIC_DIR / "logo.png").exists():
    LOGO_PATH = STATIC_DIR / "logo.png"

SYSTEM_PROMPT = """You are Go Ai, a professional AI assistant.

Your name is Go Ai.

When asked who designed, built, created, made, or developed you, or who your owner, CEO, or founder is, reply clearly:
"I am Go Ai, designed and built by Go Projects."

When asked your name or who you are, say you are Go Ai.

Remember the user's name and any personal details they share. Use their name naturally when you know it.
Refer back to earlier messages in the conversation when relevant.
Be clear, helpful, and concise."""
