from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ..forms import LoginForm, RegistrationForm
from ..models import User, Settings, Trades
from .. import db
import logging
from datetime import datetime as dt
from ..binance_api import fetch_data
from ..utils import send_email, show_account_balance
from . import main

@main.route('/start')
@login_required
def start_bot():
    return redirect(url_for('main.control_panel_view'))


@main.route('/stop')
@login_required
def stop_bot():
    return redirect(url_for('main.control_panel_view'))


@main.route('/refresh')
@login_required
def refresh():
    flash('Binance API refseshed.')
    return redirect(url_for('main.control_panel_view'))


@main.route('/report')
@login_required
def report():
    email = 'piotrek.gaszczynski@gmail.com'
    subject = 'Stefan Test'
    body = 'Stefan Body'
    send_email(email, subject, body)
    flash(f'Email to {email} send.')
    return redirect(url_for('main.control_panel_view'))