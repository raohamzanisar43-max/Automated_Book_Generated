import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from app.config import settings
import logging

logger = logging.getLogger(__name__)

def send_email(to_email: str, subject: str, body: str):
    try:
        msg = MIMEMultipart()
        msg['From'] = settings.from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(settings.smtp_host, settings.smtp_port)
        server.starttls()
        server.login(settings.smtp_username, settings.smtp_password)
        text = msg.as_string()
        server.sendmail(settings.from_email, to_email, text)
        server.quit()
        logger.info(f"Email sent successfully to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")

def send_teams_webhook(message: str):
    if not settings.teams_webhook_url:
        logger.warning("Teams webhook URL not configured.")
        return
        
    try:
        payload = {"text": message}
        response = requests.post(settings.teams_webhook_url, json=payload)
        response.raise_for_status()
        logger.info("Teams webhook sent successfully")
    except Exception as e:
        logger.error(f"Failed to send teams webhook: {e}")

def notify_review_required(book_title: str, item_type: str, item_id: str):
    subject = f"Review Required: {item_type.capitalize()} for book '{book_title}'"
    body = f"The {item_type} for '{book_title}' (ID {item_id}) has been generated and requires your review.\nPlease login to the platform to approve or add notes."
    
    # Normally we would fetch the editor's email from the DB or config
    editor_email = "editor@example.com" 
    
    send_email(editor_email, subject, body)
    send_teams_webhook(f"🚧 **Review Required** 🚧\n\n{item_type.capitalize()} for *{book_title}* is ready. [ID: {item_id}]")

def notify_workflow_paused(book_title: str, reason: str):
    send_teams_webhook(f"⚠️ **Workflow Paused** ⚠️\n\nBook: *{book_title}*\nReason: {reason}")

def notify_compilation_ready(book_title: str, file_url: str):
    subject = f"Book Compiled: {book_title}"
    body = f"The final draft for '{book_title}' has been successfully compiled.\nDownload it here: {file_url}"
    editor_email = "editor@example.com"
    send_email(editor_email, subject, body)
    send_teams_webhook(f"✅ **Book Compiled** ✅\n\n*{book_title}* is ready for download: {file_url}")
