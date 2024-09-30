from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ..forms import LoginForm, RegistrationForm
from ..models import User, Settings, Buy, Sell
from .. import db
import logging
from datetime import datetime as dt
from . import main
from ..utils.api_utils import fetch_data, fetch_ticker, fetch_system_status, fetch_account_status, fetch_server_time
from ..utils.app_utils import send_email, show_account_balance

@main.route('/')
def user_panel_view():
    if current_user.is_authenticated:
        binance_status = fetch_system_status()
        account_status = fetch_account_status()
        server_time = fetch_server_time()
        return render_template('user_panel.html', user=current_user, account_status=account_status, binance_status=binance_status, server_time=server_time)
    else:
        flash('Please log in to access app.', 'warning')
        return redirect(url_for('main.login'))

    
@main.route('/control')
def control_panel_view():
    if not current_user.is_authenticated:
        flash('Please log in to access the control panel.', 'warning')
        return redirect(url_for('main.login'))

    if not current_user.control_panel_access:
        logging.warning(f'{current_user.login} tried to access the Control Panel without permission.')
        flash(f'Error. User {current_user.login} is not allowed to access the Control Panel.', 'danger')
        return redirect(url_for('main.user_panel_view'))

    binance_ticker = fetch_ticker()
    account_status = fetch_account_status()
    account_balance = show_account_balance(account_status)

    return render_template('control_panel.html', user=current_user, account_status=account_status, account_balance=account_balance, data=binance_ticker)
    

@main.route('/admin')
def admin_panel_view():
    if not current_user.is_authenticated:
        flash('Please log in to access the admin panel.', 'warning')
        return redirect(url_for('main.login'))

    if not current_user.admin_panel_access:
        logging.warning(f'{current_user.login} tried to access the Admin Panel without permission.')
        flash(f'Error. User {current_user.login} is not allowed to access the Admin Panel.', 'danger')
        return redirect(url_for('main.user_panel_view'))

    return redirect(url_for('admin.index'))