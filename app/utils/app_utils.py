#tests
from flask_mail import Message
from app.models import User
from flask import current_app
from werkzeug.security import generate_password_hash
from ..utils.logging import logger


def get_ip_address(request):
    if 'X-Forwarded-For' in request.headers:
        return request.headers['X-Forwarded-For'].split(',')[0]
    return request.remote_addr
                              
                                
def create_new_user(form):
    try:
        new_user = User(
            login=form.login.data,
            name=form.name.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
        )
        return new_user
    except Exception as e:
        logger.error(f'Error creating user: {e}')
        send_email('piotrek.gaszczynski@gmail.com', 'User Creation Error', str(e))
        raise
    
    
def send_email(email, subject, body):
    from app import mail
    try:
        with current_app.app_context():
            message = Message(subject=subject, recipients=[email])
            message.body = body
            mail.send(message)
            logger.info(f'Email "{subject}" sent to {email}.')
            return True
    except Exception as e:
        logger.error(f'Failed to send email "{subject}" to {email}: {str(e)}')
        return False 
    

def send_24h_report_email():
    send_email('piotrek.gaszczynski@gmail.com', '24hrs report', 'raport dobowy')
    

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