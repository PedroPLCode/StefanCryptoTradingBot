from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ..forms import LoginForm, RegistrationForm
from ..models import User, Settings, Buy, Sell
from .. import db
import logging
from datetime import datetime as dt
from ..utils.api_utils import fetch_data
from ..utils.app_utils import send_email, show_account_balance
from . import main

@main.route('/start')
@login_required
def start_bot():
    try:
        settings = Settings.query.first()
        if not settings:
            settings = Settings()
            db.session.add(settings)
            db.session.commit()
        settings.bot_running = True
        db.session.commit()

        flash('Bot started.', 'success')
        send_email('piotrek.gaszczynski@gmail.com', 'Bot started.', 'Bot started.')
        return redirect(url_for('main.control_panel_view'))
    
    except Exception as e:
        db.session.rollback()  # Roll back in case of any DB error
        logging.error(f'Error starting bot: {e}')
        send_email('piotrek.gaszczynski@gmail.com', 'Error starting bot', str(e))
        flash('An error occurred while starting the bot. The admin has been notified.', 'danger')
        return redirect(url_for('main.control_panel_view'))


@main.route('/stop')
@login_required
def stop_bot():
    try:
        settings = Settings.query.first()
        if not settings:
            settings = Settings()
            db.session.add(settings)
            db.session.commit()
        settings.bot_running = False
        db.session.commit()

        flash('Bot stopped.', 'success')
        send_email('piotrek.gaszczynski@gmail.com', 'Bot stopped.', 'Bot stopped.')
        return redirect(url_for('main.control_panel_view'))
    
    except Exception as e:
        db.session.rollback()  # Roll back in case of any DB error
        logging.error(f'Error stopping bot: {e}')
        send_email('piotrek.gaszczynski@gmail.com', 'Error stopping bot', str(e))
        flash('An error occurred while stopping the bot. The admin has been notified.', 'danger')
        return redirect(url_for('main.control_panel_view'))


@main.route('/refresh')
@login_required
def refresh():
    try:
        flash('Binance API refreshed.', 'success')
        return redirect(url_for('main.control_panel_view'))

    except Exception as e:
        logging.error(f'Error refreshing Binance API: {e}')
        send_email('piotrek.gaszczynski@gmail.com', 'Error refreshing Binance API', str(e))
        flash('An error occurred while refreshing the Binance API. The admin has been notified.', 'danger')
        return redirect(url_for('main.control_panel_view'))



@main.route('/report')
@login_required
def report():
    email = 'piotrek.gaszczynski@gmail.com'
    subject = 'Stefan Test'
    body = 'Stefan Body'
    
    try:
        send_email(email, subject, body)
        flash(f'Email to {email} sent successfully.', 'success')
    except Exception as e:
        logging.error(f'Error sending email to {email}: {e}')
        flash('An error occurred while sending the email. The admin has been notified.', 'danger')
        send_email('piotrek.gaszczynski@gmail.com', 'Error sending email', str(e))
    
    return redirect(url_for('main.control_panel_view'))