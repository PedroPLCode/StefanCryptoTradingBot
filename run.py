from flask import Flask
from flask_mail import Message
from . import mail

def send_daily_report():
    with app.app_context():
        msg = Message('Daily Trade Report', sender='your-email', recipients=['user-email'])
        msg.body = "Your trade report for the last 24 hours."
        mail.send(msg)

# Add logic to trigger this function every 24 hours