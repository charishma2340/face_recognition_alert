import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Load email credentials from .env file
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT'))

def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        print(f"Connecting to SMTP server: {SMTP_SERVER} on port: {SMTP_PORT}")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            print(f"Logging in as: {EMAIL_ADDRESS}")
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            text = msg.as_string()
            print(f"Sending email to: {to_email}")
            server.sendmail(EMAIL_ADDRESS, to_email, text)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Test the email functionality
to_email = "recipient@example.com"  # Replace with your test recipient email
subject = "Test Email"
body = "This is a test email."

send_email(to_email, subject, body)
