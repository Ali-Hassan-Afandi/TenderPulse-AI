import smtplib
from email.message import EmailMessage
from src.config import secret

def configured():
    return all(secret(k) for k in ["SMTP_HOST","SMTP_PORT","SMTP_USER","SMTP_PASSWORD"])

def send_alert(recipient, subject, body):
    if not configured():
        return False, "SMTP secrets are not configured."
    msg=EmailMessage()
    msg["From"]=secret("SMTP_FROM", secret("SMTP_USER"))
    msg["To"]=recipient
    msg["Subject"]=subject
    msg.set_content(body)
    try:
        with smtplib.SMTP(secret("SMTP_HOST"), int(secret("SMTP_PORT",587)), timeout=20) as s:
            s.starttls(); s.login(secret("SMTP_USER"), secret("SMTP_PASSWORD")); s.send_message(msg)
        return True, "Email sent."
    except Exception as e:
        return False, f"Email failed: {e}"
