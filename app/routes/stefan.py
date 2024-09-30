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
    settings = Settings.query.first()
    if not settings:
        settings = Settings()
        db.session.add(settings)
        db.session.commit()
    settings.bot_running = True 
    db.session.commit()
    flash('Bot started.', 'success')
    return redirect(url_for('main.control_panel_view'))


@main.route('/stop')
@login_required
def stop_bot():
    settings = Settings.query.first()
    if not settings:
        settings = Settings()
        db.session.add(settings)
        db.session.commit()
    settings.bot_running = False
    db.session.commit()
    flash('Bot stopped.', 'success')
    return redirect(url_for('main.control_panel_view'))


@main.route('/refresh')
@login_required
def refresh():
    flash('Binance API refseshed.', 'success')
    return redirect(url_for('main.control_panel_view'))


@main.route('/report')
@login_required
def report():
    email = 'piotrek.gaszczynski@gmail.com'
    subject = 'Stefan Test'
    body = 'Stefan Body'
    send_email(email, subject, body)
    flash(f'Email to {email} send.', 'success')
    return redirect(url_for('main.control_panel_view'))