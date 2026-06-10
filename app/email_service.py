import asyncio
import logging
from email.message import EmailMessage

from datetime import datetime, timezone

import aiosmtplib

from app.config import GMAIL_USER, GMAIL_APP_PASSWORD, NOTIFICATION_EMAIL, APP_TITLE

logger = logging.getLogger(__name__)

async def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """Send email using aiosmtplib (non-blocking)."""
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        logger.warning("SMTP credentials not configured. Skipping email.")
        return False
        
    msg = EmailMessage()
    msg["From"] = f"{APP_TITLE} <{GMAIL_USER}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content("Please enable HTML to view this email.")
    msg.add_alternative(html_content, subtype="html")

    try:
        await aiosmtplib.send(
            msg,
            hostname="smtp.gmail.com",
            port=465,
            use_tls=True,
            username=GMAIL_USER,
            password=GMAIL_APP_PASSWORD,
        )
        logger.info(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


async def notify_admin_new_signup(username: str, email: str) -> None:
    """Send a signup notification to the notification email address."""
    if not NOTIFICATION_EMAIL:
        return

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    subject = f"🎉 New Sign-Up on {APP_TITLE}: @{username}"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; background: #f9f9f9; border-radius: 12px; overflow: hidden; border: 1px solid #e0e0e0;">
        <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); padding: 30px; text-align: center;">
            <h1 style="color: #ffffff; margin: 0; font-size: 24px;">🚀 {APP_TITLE}</h1>
            <p style="color: #a0a0c0; margin: 8px 0 0;">New User Signed Up!</p>
        </div>
        <div style="padding: 30px; background: #ffffff;">
            <h2 style="color: #1a1a2e; margin-top: 0;">New Account Created</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 10px; background: #f0f4ff; border-radius: 8px; font-weight: bold; color: #555; width: 130px;">👤 Username</td>
                    <td style="padding: 10px; color: #1a1a2e; font-size: 16px;"><strong>@{username}</strong></td>
                </tr>
                <tr>
                    <td style="padding: 10px; font-weight: bold; color: #555;">📧 Email</td>
                    <td style="padding: 10px; color: #1a1a2e;">{email}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; background: #f0f4ff; border-radius: 8px; font-weight: bold; color: #555;">🕒 Time</td>
                    <td style="padding: 10px; background: #f0f4ff; color: #1a1a2e;">{now}</td>
                </tr>
            </table>
        </div>
        <div style="padding: 20px; text-align: center; background: #f9f9f9; color: #999; font-size: 13px;">
            This is an automated notification from {APP_TITLE}
        </div>
    </div>
    """
    await send_email(NOTIFICATION_EMAIL, subject, html)


async def send_welcome_email(username: str, email: str) -> None:
    """Send a welcome confirmation email to the new user."""
    subject = f"Welcome to {APP_TITLE}, @{username}! 🎉"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; background: #f9f9f9; border-radius: 12px; overflow: hidden; border: 1px solid #e0e0e0;">
        <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); padding: 30px; text-align: center;">
            <h1 style="color: #ffffff; margin: 0; font-size: 28px;">Welcome to {APP_TITLE}! 🚀</h1>
            <p style="color: #a0a0c0; margin: 8px 0 0;">Your AI assistant is ready</p>
        </div>
        <div style="padding: 30px; background: #ffffff;">
            <h2 style="color: #1a1a2e;">Hey @{username}! 👋</h2>
            <p style="color: #444; line-height: 1.6;">
                Your account has been successfully created. You can now start chatting with <strong>{APP_TITLE}</strong> — your personal AI assistant built by <strong>Go Projects</strong>.
            </p>
            <div style="background: #f0f4ff; border-radius: 10px; padding: 20px; margin: 20px 0; border-left: 4px solid #4f46e5;">
                <p style="margin: 0; color: #1a1a2e; font-size: 15px;">💡 <strong>Tip:</strong> Ask me anything — I remember your conversations and learn your preferences over time.</p>
            </div>
            <p style="color: #444;">Start chatting now and experience the power of Go Ai!</p>
        </div>
        <div style="padding: 20px; text-align: center; background: #f9f9f9; color: #999; font-size: 13px;">
            © {APP_TITLE} by Go Projects · You're receiving this because you signed up.
        </div>
    </div>
    """
    await send_email(email, subject, html)
