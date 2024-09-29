import random
from app import mail
from flask_mail import Message
from app.models import User
import os
from datetime import datetime, timedelta
import logging
from .binance_api import fetch_data, fetch_ticker, fetch_system_status, fetch_account_status


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
    

def show_account_balance(account_status):
    if not account_status:
        return False
    account_balance = []
    if 'balances' in account_status:
        for single in account_status['balances']:
            free_balance = float(single['free']) if isinstance(single['free'], str) else single['free']
            locked_balance = float(single['locked']) if isinstance(single['locked'], str) else single['locked']
            if single['asset'] == 'BTC' or single['asset'] == 'USDC':
                account_balance.append({
                    'asset': single['asset'],
                    'free': free_balance,
                    'locked': locked_balance,
                })
    return account_balance