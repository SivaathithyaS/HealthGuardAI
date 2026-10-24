import os
import smtplib
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def _ensure_env_loaded():
    """Locate and load .env from project root or candidate directories."""
    candidates = [
        Path(__file__).resolve().parent.parent.parent.parent / ".env",
        Path(__file__).resolve().parent.parent.parent / ".env",
        Path.cwd() / ".env",
        Path.cwd().parent / ".env"
    ]
    for p in candidates:
        if p.is_file():
            try:
                from dotenv import load_dotenv
                load_dotenv(dotenv_path=p, override=False)
                break
            except ImportError:
                pass

_ensure_env_loaded()

class EmailService:
    def __init__(self):
        _ensure_env_loaded()

    @property
    def smtp_host(self) -> str:
        _ensure_env_loaded()
        return os.getenv("SMTP_HOST", "smtp.gmail.com").strip()

    @property
    def smtp_port(self) -> int:
        try:
            return int(os.getenv("SMTP_PORT", "587"))
        except (ValueError, TypeError):
            return 587

    @property
    def smtp_user(self) -> str:
        _ensure_env_loaded()
        return os.getenv("SMTP_USER", "").strip()

    @property
    def smtp_password(self) -> str:
        _ensure_env_loaded()
        return os.getenv("SMTP_PASSWORD", "").strip()

    @property
    def from_name(self) -> str:
        return os.getenv("SMTP_FROM_NAME", "HealthGuard AI Security").strip()

    def is_configured(self) -> bool:
        """Returns True if sender credentials have been provided in environment or .env file."""
        return bool(self.smtp_user and self.smtp_password)

    def send_otp_email(self, recipient_email: str, otp_code: str, user_name: str = "User") -> dict:
        """
        Sends a 6-digit verification OTP email to the recipient.
        Uses Gmail SMTP (TLS port 587) with Google App Password.
        Falls back gracefully if SMTP is unconfigured or encounters a network failure.
        """
        recipient_email = recipient_email.strip()
        display_name = user_name if user_name and user_name.strip() else "Valued Patient / Clinician"

        if not self.is_configured():
            return {
                "sent": False,
                "reason": "SMTP_USER or SMTP_PASSWORD not configured in .env",
                "demo_otp": otp_code
            }

        subject = f"Your HealthGuard AI Verification Code: {otp_code}"
        
        # Professional clinical HTML email template
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #F4F5F3; margin: 0; padding: 24px; color: #1B2420; }}
            .container {{ max-width: 540px; margin: 0 auto; background: #FFFFFF; border: 1px solid #E3E6E2; border-radius: 12px; overflow: hidden; }}
            .header {{ background: #0E3B38; color: #FFFFFF; padding: 24px 28px; text-align: left; }}
            .brand {{ font-size: 20px; font-weight: 700; letter-spacing: 0.5px; }}
            .subhead {{ font-size: 13px; color: #A7F3D0; margin-top: 4px; }}
            .content {{ padding: 28px; }}
            .greeting {{ font-size: 16px; font-weight: 600; margin-bottom: 12px; }}
            .text {{ font-size: 14px; line-height: 1.6; color: #4F5A54; margin-bottom: 24px; }}
            .otp-box {{ background: #EAF2EC; border: 1px solid #CFE3D5; border-radius: 8px; padding: 18px; text-align: center; margin-bottom: 24px; }}
            .otp-code {{ font-family: 'Courier New', Courier, monospace; font-size: 32px; font-weight: 800; letter-spacing: 6px; color: #0E6B64; }}
            .otp-expiry {{ font-size: 12px; color: #4F5A54; margin-top: 6px; }}
            .footer {{ background: #FAFAFA; border-top: 1px solid #EDEFEC; padding: 18px 28px; font-size: 12px; color: #8B948E; line-height: 1.5; }}
            .warning {{ color: #B5522E; font-size: 12px; margin-top: 16px; padding: 8px 12px; background: #FBF0EC; border-radius: 6px; border: 1px solid #E8C9BC; }}
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <div class="brand">HealthGuard AI</div>
              <div class="subhead">Clinical Decision Support & Personalized Health Platform</div>
            </div>
            <div class="content">
              <div class="greeting">Hello {display_name},</div>
              <div class="text">
                You have requested a secure verification code to access your HealthGuard AI personal account and longitudinal health history records.
              </div>
              <div class="otp-box">
                <div class="otp-code">{otp_code}</div>
                <div class="otp-expiry">This code will expire in 10 minutes.</div>
              </div>
              <div class="text">
                Enter this 6-digit code on the HealthGuard AI registration screen to verify your email address and activate your isolated health record repository.
              </div>
              <div class="warning">
                <strong>Security Notice:</strong> If you did not request this verification code, please disregard this email. Never share your verification code with anyone.
              </div>
            </div>
            <div class="footer">
              HealthGuard AI Autonomous Clinical System • Certified Data Isolation Protocol<br>
              This is an automated system notification; please do not reply directly to this email.
            </div>
          </div>
        </body>
        </html>
        """

        text_content = (
            f"Hello {display_name},\n\n"
            f"Your HealthGuard AI verification code is: {otp_code}\n\n"
            f"This code will expire in 10 minutes.\n\n"
            f"If you did not request this code, please ignore this email."
        )

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.smtp_user}>"
            msg["To"] = recipient_email

            part1 = MIMEText(text_content, "plain")
            part2 = MIMEText(html_content, "html")
            msg.attach(part1)
            msg.attach(part2)

            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=12) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                # Try with provided password, fallback to spaces-removed app password format
                try:
                    server.login(self.smtp_user, self.smtp_password)
                except smtplib.SMTPAuthenticationError:
                    clean_pwd = self.smtp_password.replace(" ", "").strip()
                    server.login(self.smtp_user, clean_pwd)

                server.sendmail(self.smtp_user, [recipient_email], msg.as_string())

            print(f"[EmailService] SUCCESS: Verification email sent to {recipient_email} (from {self.smtp_user})")
            return {
                "sent": True,
                "message": f"Real verification email dispatched successfully to {recipient_email}"
            }
        except Exception as e:
            print(f"[EmailService] ERROR sending to {recipient_email}: {str(e)}")
            # Fallback if connection fails (e.g. incorrect App Password or blocked port)
            return {
                "sent": False,
                "reason": f"SMTP dispatch error: {str(e)}",
                "demo_otp": otp_code
            }

email_service = EmailService()
