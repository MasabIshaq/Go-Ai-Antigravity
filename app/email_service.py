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


async def send_password_reset_email(username: str, email: str, reset_code: str) -> None:
    """Send a password reset code to the user's email."""
    subject = f"Reset your {APP_TITLE} password"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; background: #f9f9f9; border-radius: 12px; overflow: hidden; border: 1px solid #e0e0e0;">
        <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); padding: 30px; text-align: center;">
            <h1 style="color: #ffffff; margin: 0; font-size: 24px;">Password Reset</h1>
            <p style="color: #a0a0c0; margin: 8px 0 0;">{APP_TITLE}</p>
        </div>
        <div style="padding: 30px; background: #ffffff;">
            <h2 style="color: #1a1a2e; margin-top: 0;">Reset Your Password</h2>
            <p style="color: #444; line-height: 1.6;">
                Hi <strong>{username}</strong>, we received a request to reset your password.
                Use the code below to set a new password. This code expires in <strong>15 minutes</strong>.
            </p>
            <div style="background: #f0f4ff; border-radius: 10px; padding: 24px; margin: 20px 0; text-align: center; border-left: 4px solid #10a37f;">
                <p style="margin: 0; color: #888; font-size: 13px; letter-spacing: 1px; text-transform: uppercase;">Your Reset Code</p>
                <p style="margin: 10px 0 0; font-size: 36px; font-weight: bold; letter-spacing: 8px; color: #1a1a2e; font-family: monospace;">{reset_code}</p>
            </div>
            <p style="color: #888; font-size: 13px;">If you did not request a password reset, you can safely ignore this email.</p>
        </div>
        <div style="padding: 20px; text-align: center; background: #f9f9f9; color: #999; font-size: 13px;">
            &copy; {APP_TITLE} by Go Projects &middot; This email was sent because a reset was requested.
        </div>
    </div>
    """
    await send_email(email, subject, html)


async def send_login_alert_email(username: str, email: str) -> None:
    """Send an alert when a user logs in."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    subject = f"Security Alert: New login to {APP_TITLE}"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; background: #f9f9f9; border-radius: 12px; overflow: hidden; border: 1px solid #e0e0e0;">
        <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); padding: 30px; text-align: center;">
            <h1 style="color: #ffffff; margin: 0; font-size: 24px;">Security Alert</h1>
            <p style="color: #a0a0c0; margin: 8px 0 0;">{APP_TITLE}</p>
        </div>
        <div style="padding: 30px; background: #ffffff;">
            <p style="color: #444; line-height: 1.6;">
                Hi <strong>{username}</strong>,<br><br>
                Your account was just accessed at <strong>{now}</strong>.<br><br>
                If this was you, you can safely ignore this email. If you did not log in, please reset your password immediately or contact support.
            </p>
        </div>
        <div style="padding: 20px; text-align: center; background: #f9f9f9; color: #999; font-size: 13px;">
            &copy; {APP_TITLE} by Go Projects
        </div>
    </div>
    """
    await send_email(email, subject, html)


async def send_otp_email(username: str, email: str, otp_code: str, context: str = "Sign Up") -> None:
    """Send an OTP code for 2FA or Signup."""
    subject = f"Your {APP_TITLE} Verification Code"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; background: #f9f9f9; border-radius: 12px; overflow: hidden; border: 1px solid #e0e0e0;">
        <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); padding: 30px; text-align: center;">
            <h1 style="color: #ffffff; margin: 0; font-size: 24px;">Verification Required</h1>
            <p style="color: #a0a0c0; margin: 8px 0 0;">{context}</p>
        </div>
        <div style="padding: 30px; background: #ffffff;">
            <h2 style="color: #1a1a2e; margin-top: 0;">Your Verification Code</h2>
            <p style="color: #444; line-height: 1.6;">
                Hi <strong>{username}</strong>,<br><br>
                Use the following 6-digit code to complete your {context.lower()}. This code expires in 15 minutes.
            </p>
            <div style="background: #f0f4ff; border-radius: 10px; padding: 24px; margin: 20px 0; text-align: center; border-left: 4px solid #4f46e5;">
                <p style="margin: 0; font-size: 36px; font-weight: bold; letter-spacing: 8px; color: #1a1a2e; font-family: monospace;">{otp_code}</p>
            </div>
            <p style="color: #888; font-size: 13px;">If you didn't request this code, please ignore this email.</p>
        </div>
        <div style="padding: 20px; text-align: center; background: #f9f9f9; color: #999; font-size: 13px;">
            &copy; {APP_TITLE} by Go Projects
        </div>
    </div>
    """
    await send_email(email, subject, html)
