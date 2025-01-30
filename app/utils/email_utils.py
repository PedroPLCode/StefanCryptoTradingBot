from flask import current_app
from flask_mail import Message
from datetime import datetime
from app.models import User
from ..utils.logging import logger
from ..utils.reports_utils import generate_trade_report

def send_email(email, subject, body):
    """
    Sends an email to a specified recipient.

    This function uses Flask-Mail to send an email with the given subject and body
    to the specified email address. If an exception occurs, it logs the error
    and notifies the admin via email.

    Args:
        email (str): The recipient's email address.
        subject (str): The subject of the email.
        body (str): The body content of the email.

    Returns:
        bool: True if the email was sent successfully, False otherwise.

    Raises:
        Logs any exceptions encountered and notifies the admin.
    """
    from app import mail
    
    try:
        
        with current_app.app_context():
            message = Message(subject=subject, recipients=[email])
            message.body = body
            mail.send(message)
            logger.info(f'Email "{subject}" to {email} sent succesfully.')
            return True
    except Exception as e:
        logger.error(f"Exception in send_email subject: {subject} email: {email}: {str(e)}")
        send_admin_email(f"Exception in send_email subject: {subject} email: {email}", str(e))
        return False


def send_admin_email(subject, body):
    """
    Sends an email notification to all users with admin panel access.

    This function retrieves all users who have `admin_panel_access=True`
    and sends them an email with the given subject and body. If an exception
    occurs, it logs the error.

    Args:
        subject (str): The subject of the email.
        body (str): The body content of the email.

    Raises:
        Logs any exceptions encountered.
    """
    try:
        
        with current_app.app_context():
            users = User.query.filter_by(admin_panel_access=True).all()
            for user in users:
                success = send_email(user.email, subject, body)
                if not success:
                    logger.error(f"Failed to send admin email to {user.email}. {subject} {body}")
                    
    except Exception as e:
        logger.error(f"Exception in send_admin_email: {str(e)}")
        

def send_trade_email(subject, body):
    """
    Sends trade-related notifications via email.

    This function retrieves all users who have `email_trades_receiver=True`
    and sends them an email with the given subject and body. If an exception
    occurs, it logs the error.

    Args:
        subject (str): The subject of the email.
        body (str): The body content of the email.

    Raises:
        Logs any exceptions encountered.
    """
    try:
        
        with current_app.app_context():
            users = User.query.filter_by(email_trades_receiver=True).all()
            for user in users:
                success = send_email(user.email, subject, body)
                if not success:
                    logger.error(f"Failed to send trade info email to {user.email}. {subject} {body}")
                    send_admin_email(f"Failed to send trade info email to {user.email}", str(e))
                    
    except Exception as e:
        logger.error(f"Exception in send_trade_email: {str(e)}")
        send_admin_email(f"Exception in send_trade_email", str(e))
        
        
def send_trade_report_via_email():
    """
    Sends a daily trade report via email to all users who have opted in.

    This function generates a 24-hour trade report and sends it via email
    to users who have `email_raports_receiver=True`. If an exception occurs,
    it logs the error and notifies the admin.

    Raises:
        Logs any exceptions encountered and notifies the admin.
    """
    try:
        
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        with current_app.app_context():
            users = User.query.filter_by(email_raports_receiver=True).all()
            report_body = generate_trade_report('24h')
            for user in users:
                success = send_email(user.email, f'{today} Daily Trades Report', report_body)
                if not success:
                    logger.error(f"Failed to send 24h report to {user.email}.")
                    
    except Exception as e:
        logger.error(f"Exception in send_trade_report_via_email email: {user.email}: {str(e)}")
        send_admin_email(f"Exception in send_trade_report_via_email email: {user.email}", str(e))