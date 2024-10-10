from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ..forms import LoginForm, RegistrationForm
from ..models import User, Settings
from .. import db, app
from ..utils.logging import logger
import logging
from datetime import datetime as dt
from ..utils.api_utils import fetch_data
from ..utils.app_utils import send_email, send_admin_email, show_account_balance, generate_trade_report
from . import main

@main.route('/start')
@login_required
def start_bot():
    if not current_user.control_panel_access:
        logger.warning(f'{current_user.login} tried to control Bot without permission.')
        flash(f'Error. User {current_user.login} is not allowed to control Bot.', 'danger')
        return redirect(url_for('main.user_panel_view'))
    
    try:
        settings = Settings.query.first()
        if not settings:
            settings = Settings()
            db.session.add(settings)
            db.session.commit()
            
        if settings.bot_running:
            flash('Bot is already running.', 'success')
        else:
            settings.bot_running = True
            db.session.commit()

            flash('Bot started.', 'success')
            send_admin_email('Bot started.', 'Bot started.')
        return redirect(url_for('main.control_panel_view'))
    
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error starting bot: {e}')
        send_admin_email('Error starting bot', str(e))
        flash('An error occurred while starting the bot. The admin has been notified.', 'danger')
        return redirect(url_for('main.control_panel_view'))


@main.route('/stop')
@login_required
def stop_bot():
    if not current_user.control_panel_access:
        logger.warning(f'{current_user.login} tried to control Bot without permission.')
        flash(f'Error. User {current_user.login} is not allowed to control Bot.', 'danger')
        return redirect(url_for('main.user_panel_view'))
    
    try:
        settings = Settings.query.first()
        if not settings:
            settings = Settings()
            db.session.add(settings)
            db.session.commit()
            
        if not settings.bot_running:
            flash('Bot is already stopped.', 'success')
        else:
            settings.bot_running = False
            db.session.commit()

            flash('Bot stopped.', 'success')
            send_admin_email('Bot stopped.', 'Bot stopped.')
        return redirect(url_for('main.control_panel_view'))
    
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error stopping bot: {e}')
        send_admin_email('Error stopping bot', str(e))
        flash('An error occurred while stopping the bot. The admin has been notified.', 'danger')
        return redirect(url_for('main.control_panel_view'))


@main.route('/refresh')
@login_required
def refresh():
    if not current_user.control_panel_access:
        logger.warning(f'{current_user.login} tried to control Bot without permission.')
        flash(f'Error. User {current_user.login} is not allowed to control Bot.', 'danger')
        return redirect(url_for('main.user_panel_view'))
    
    try:
        flash('Binance API refreshed.', 'success')
        return redirect(url_for('main.control_panel_view'))

    except Exception as e:
        logger.error(f'Error refreshing Binance API: {e}')
        send_admin_email('Error refreshing Binance API', str(e))
        flash('An error occurred while refreshing the Binance API. The admin has been notified.', 'danger')
        return redirect(url_for('main.control_panel_view'))



@main.route('/report')
@login_required
def report():
    if not current_user.email_raports_receiver:
        logger.warning(f'{current_user.login} tried to get email rapirt.')
        flash(f'Error. User {current_user.login} is not allowed receiving email raports.', 'danger')
        return redirect(url_for('main.user_panel_view'))
    
    email = current_user.email
    subject = 'Stefan Test Raport'
    report_body = generate_trade_report('7d')
    
    try:
        with current_app.app_context():
            send_email(email, subject, report_body)
            flash(f'Email to {email} sent successfully.', 'success')
    except Exception as e:
        logger.error(f'Error sending email to {email}: {e}')
        flash('An error occurred while sending the email. The admin has been notified.', 'danger')
        send_admin_email('Error sending email', str(e))
    
    return redirect(url_for('main.control_panel_view'))