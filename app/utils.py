import random
from app import mail
from flask_mail import Message
from app.models import User
import os
from datetime import datetime, timedelta
import logging

def send_email(email, subject, body):
    message = Message(subject=subject, recipients=[email])
    message.body = body
    try:
        mail.send(message)
        logging.info(f'Email "{subject}" sent to {email}.')
        return True
    except Exception as e:
        logging.error(f'Failed to send email "{subject}" to {email}: {str(e)}')
        return False 