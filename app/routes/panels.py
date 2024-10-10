from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ..forms import LoginForm, RegistrationForm
from ..models import User, Settings, TradesHistory
from .. import db
from ..utils.logging import logger
import logging
from datetime import datetime as dt
from . import main
from ..utils.api_utils import fetch_data, fetch_ticker, fetch_system_status, fetch_account_status, fetch_server_time
from ..utils.app_utils import send_email, show_account_balance, send_admin_email

@main.route('/')
def user_panel_view():
    if current_user.is_authenticated:
        try:
            binance_status = fetch_system_status()
            account_status = fetch_account_status()
            server_time = fetch_server_time()
            return render_template('user_panel.html', user=current_user, account_status=account_status, binance_status=binance_status, server_time=server_time)
        except Exception as e:
            logger.error(f"Error in user_panel_view: {e}")
            send_admin_email('Error in user panel view', str(e))
            flash('An error occurred while fetching account data. Please try again later.', 'danger')
            return redirect(url_for('main.login'))
    else:
        flash('Please log in to access the app.', 'warning')
        return redirect(url_for('main.login'))

    
@main.route('/control')
def control_panel_view():
    if not current_user.is_authenticated:
        flash('Please log in to access the control panel.', 'warning')
        return redirect(url_for('main.login'))

    if not current_user.control_panel_access:
        logger.warning(f'{current_user.login} tried to access the Control Panel without permission.')
        flash(f'Error. User {current_user.login} is not allowed to access the Control Panel.', 'danger')
        return redirect(url_for('main.user_panel_view'))

    try:
        binance_ticker = fetch_ticker()
        account_status = fetch_account_status()
        account_balance = show_account_balance(account_status)
        current_trades = TradesHistory.query.all()

        return render_template('control_panel.html', user=current_user, account_status=account_status, account_balance=account_balance, data=binance_ticker, current_trades=current_trades)

    except Exception as e:
        logger.error(f'Error loading control panel: {e}')
        send_admin_email('Error loading control panel', str(e))
        flash('An error occurred while loading the control panel. The admin has been notified.', 'danger')
        return redirect(url_for('main.user_panel_view'))


@main.route('/admin')
def admin_panel_view():
    if not current_user.is_authenticated:
        flash('Please log in to access the admin panel.', 'warning')
        return redirect(url_for('main.login'))

    if not current_user.admin_panel_access:
        logger.warning(f'{current_user.login} tried to access the Admin Panel without permission.')
        flash(f'Error. User {current_user.login} is not allowed to access the Admin Panel.', 'danger')
        return redirect(url_for('main.user_panel_view'))

    try:
        return redirect(url_for('admin.index'))

    except Exception as e:
        logger.error(f'Error accessing admin panel: {e}')
        send_admin_email('Error accessing admin panel', str(e))
        flash('An error occurred while accessing the admin panel. The admin has been notified.', 'danger')
        return redirect(url_for('main.user_panel_view'))