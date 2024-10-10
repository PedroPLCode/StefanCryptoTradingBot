from datetime import datetime, timedelta
from flask_mail import Message
from app.models import User, TradesHistory
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
        send_admin_email('User Creation Error', str(e))
        raise


def generate_trade_report(period):
    now = datetime.now()
    
    if period == '24h':
        last_period = now - timedelta(hours=24)
    elif period == '7d':
        last_period = now - timedelta(days=7)
    
    trades = TradesHistory.query.filter(TradesHistory.timestamp >= last_period).order_by(TradesHistory.timestamp.desc()).all()
    
    total_trades = len(trades)
    today = now.strftime('%Y-%m-%d')
    report_data = f"Raport okresowy Dnia: {today}\n\n"
    
    if total_trades == 0:
        report_data += f"Brak transakcji w ciągu ostatnich {period}.\n"
    else:
        report_data += f"Liczba transakcji w ciągu ostatnich {period}: {total_trades}\n\n"
        
        for trade in trades:
            report_data += (f"id: {trade.id}, {trade.type}, amount: {trade.amount} BTC, "
                            f"price: ${trade.price:.2f} USDC, timestamp: {trade.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")

    return report_data


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
    users = User.query.filter_by(email_raports_receiver=True).all()
    report_body = generate_trade_report('24h')
    for user in users:
        success = send_email(user.email, '24h report', report_body)
        if not success:
            logger.error(f"Failed to send 24h report to {user.email}.")
            
            
def send_admin_email(subject, body):
    users = User.query.filter_by(admin_panel_access=True).all()
    for user in users:
        success = send_email(user.email, subject, body)
        if not success:
            logger.error(f"Failed to send email to {user.email}. {subject} {body}")


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