"""
Email service for Go Ai.
Uses standard library smtplib (run in a thread executor so it never blocks
the async event loop).  aiosmtplib is NOT required.
"""

import asyncio
import logging
import smtplib
import ssl
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import GMAIL_USER, GMAIL_APP_PASSWORD, NOTIFICATION_EMAIL, APP_TITLE

logger = logging.getLogger(__name__)


def _send_email_sync(to_email: str, subject: str, html_content: str) -> bool:
    """Blocking SMTP send — called via run_in_executor so it won't block async."""
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        logger.warning("SMTP credentials not set (GMAIL_USER / GMAIL_APP_PASSWORD). Email skipped.")
        return False

    msg = MIMEMultipart("alternative")
    msg["From"] = f"{APP_TITLE} <{GMAIL_USER}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText("Please enable HTML to view this email.", "plain"))
    msg.attach(MIMEText(html_content, "html"))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, to_email, msg.as_string())
        logger.info("Email sent to %s", to_email)
        return True
    except smtplib.SMTPAuthenticationError:
        logger.error(
            "Gmail auth failed. Make sure GMAIL_USER=%s and GMAIL_APP_PASSWORD is a "
            "16-char App Password (not your regular password). "
            "Enable 2FA on the account and create an App Password at "
            "https://myaccount.google.com/apppasswords",
            GMAIL_USER,
        )
        return False
    except Exception as exc:
        logger.error("Failed to send email to %s: %s", to_email, exc)
        return False


async def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """Async wrapper — runs blocking SMTP in a thread so FastAPI stays responsive."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _send_email_sync, to_email, subject, html_content)


# ── Template helpers ─────────────────────────────────────────────────────────

def _header(title: str, subtitle: str = "") -> str:
    return f"""
    <div style="background:linear-gradient(135deg,#0f0f1a,#1a2740);padding:32px;text-align:center;border-radius:12px 12px 0 0;">
      <h1 style="color:#fff;margin:0;font-size:22px;font-family:Arial,sans-serif;">{title}</h1>
      {f'<p style="color:#8bb3d0;margin:6px 0 0;font-size:14px;">{subtitle}</p>' if subtitle else ''}
    </div>"""

def _footer() -> str:
    return f"""
    <div style="background:#f5f5f5;padding:16px;text-align:center;border-radius:0 0 12px 12px;color:#999;font-size:12px;font-family:Arial,sans-serif;">
      &copy; {APP_TITLE} by Go Projects &nbsp;|&nbsp; goprojects452@gmail.com
    </div>"""

def _wrap(inner: str) -> str:
    return (
        '<div style="font-family:Arial,sans-serif;max-width:580px;margin:auto;'
        'border:1px solid #e0e0e0;border-radius:12px;overflow:hidden;">'
        + inner + "</div>"
    )

def _otp_box(code: str) -> str:
    return f"""
    <div style="background:#f0f8f5;border-left:4px solid #10a37f;border-radius:8px;
                padding:24px;margin:24px 0;text-align:center;">
      <p style="margin:0 0 6px;color:#555;font-size:13px;letter-spacing:1px;text-transform:uppercase;">
        Verification Code
      </p>
      <p style="margin:0;font-size:38px;font-weight:bold;letter-spacing:10px;
                color:#0d0d0d;font-family:monospace;">{code}</p>
      <p style="margin:10px 0 0;color:#888;font-size:12px;">Expires in 15 minutes</p>
    </div>"""


# ── Public API ────────────────────────────────────────────────────────────────

async def send_otp_email(username: str, email: str, otp_code: str, context: str = "Sign Up") -> None:
    """OTP for signup verification or 2FA login."""
    subject = f"Your {APP_TITLE} verification code: {otp_code}"
    html = _wrap(
        _header("Verification Required", context)
        + f"""
        <div style="padding:28px;background:#fff;">
          <p style="color:#333;line-height:1.6;margin:0 0 8px;">
            Hi <strong>{username}</strong>,
          </p>
          <p style="color:#555;line-height:1.6;margin:0 0 4px;">
            Use this code to complete your <strong>{context.lower()}</strong>:
          </p>
          {_otp_box(otp_code)}
          <p style="color:#999;font-size:12px;margin:0;">
            If you didn't request this, you can safely ignore this email.
          </p>
        </div>"""
        + _footer()
    )
    await send_email(email, subject, html)


async def send_password_reset_email(username: str, email: str, reset_code: str) -> None:
    """Password reset code."""
    subject = f"Reset your {APP_TITLE} password"
    html = _wrap(
        _header("Password Reset", APP_TITLE)
        + f"""
        <div style="padding:28px;background:#fff;">
          <p style="color:#333;line-height:1.6;margin:0 0 8px;">
            Hi <strong>{username}</strong>,
          </p>
          <p style="color:#555;line-height:1.6;margin:0 0 4px;">
            Use the code below to set a new password.  This code expires in
            <strong>15 minutes</strong>.
          </p>
          {_otp_box(reset_code)}
          <p style="color:#999;font-size:12px;margin:0;">
            If you didn't request a password reset, you can ignore this email.
          </p>
        </div>"""
        + _footer()
    )
    await send_email(email, subject, html)


async def send_welcome_email(username: str, email: str) -> None:
    """Welcome email after successful account verification."""
    subject = f"Welcome to {APP_TITLE}! 🎉"
    html = _wrap(
        _header(f"Welcome to {APP_TITLE}! 🚀", "Your AI assistant is ready")
        + f"""
        <div style="padding:28px;background:#fff;">
          <h2 style="color:#0d0d0d;margin:0 0 12px;">Hey {username}! 👋</h2>
          <p style="color:#444;line-height:1.6;margin:0 0 16px;">
            Your account has been verified and is ready to use.
            Start chatting with <strong>{APP_TITLE}</strong> — your personal
            AI assistant built by <strong>Go Projects</strong>.
          </p>
          <div style="background:#f0f8f5;border-radius:8px;padding:16px;border-left:4px solid #10a37f;">
            <p style="margin:0;color:#0d0d0d;font-size:14px;">
              💡 <strong>Tip:</strong> Ask me anything — I remember your
              conversation history and learn your preferences.
            </p>
          </div>
        </div>"""
        + _footer()
    )
    await send_email(email, subject, html)


async def send_login_alert_email(username: str, email: str) -> None:
    """Security alert on new login (only when 2FA is off and login succeeds)."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    subject = f"New sign-in to your {APP_TITLE} account"
    html = _wrap(
        _header("New Sign-In Detected", APP_TITLE)
        + f"""
        <div style="padding:28px;background:#fff;">
          <p style="color:#333;line-height:1.6;margin:0 0 8px;">
            Hi <strong>{username}</strong>,
          </p>
          <p style="color:#555;line-height:1.6;margin:0;">
            Your account was accessed on <strong>{now}</strong>.
          </p>
          <p style="color:#555;line-height:1.6;margin:12px 0 0;">
            If this was you, no action is needed.  If you don't recognise
            this sign-in, reset your password immediately.
          </p>
        </div>"""
        + _footer()
    )
    await send_email(email, subject, html)


async def notify_admin_new_signup(username: str, email: str) -> None:
    """Notify admin (goprojects452@gmail.com) when a new user registers."""
    if not NOTIFICATION_EMAIL:
        return
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    subject = f"New sign-up on {APP_TITLE}: @{username}"
    html = _wrap(
        _header(f"New User — {APP_TITLE}", "Sign-up notification")
        + f"""
        <div style="padding:28px;background:#fff;">
          <table style="width:100%;border-collapse:collapse;font-size:14px;color:#333;">
            <tr>
              <td style="padding:10px;background:#f9f9f9;font-weight:bold;width:110px;">Username</td>
              <td style="padding:10px;">@{username}</td>
            </tr>
            <tr>
              <td style="padding:10px;font-weight:bold;">Email</td>
              <td style="padding:10px;">{email}</td>
            </tr>
            <tr>
              <td style="padding:10px;background:#f9f9f9;font-weight:bold;">Time</td>
              <td style="padding:10px;background:#f9f9f9;">{now}</td>
            </tr>
          </table>
        </div>"""
        + _footer()
    )
    await send_email(NOTIFICATION_EMAIL, subject, html)
