from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ..forms import LoginForm, RegistrationForm
from ..models import User, Settings, Trades
from .. import db
import logging
from datetime import datetime as dt
from . import main

@main.route('/')
def user_panel_view():
    if current_user.is_authenticated:
        return render_template('user_panel.html', user=current_user)
    else:
        flash('Please log in to access app.', 'warning')
        return redirect(url_for('main.login'))

    
@main.route('/control')
def control_panel_view():
    if current_user.is_authenticated:
        if current_user.control_panel_access:
            return render_template('control_panel.html')
        else:
            logging.warning(f'{current_user.login} trying to login to Dashboard.')
            flash(f'Error. User {current_user.login} not accepted here.', 'danger')
            return redirect(url_for('main.login'))
    else:
        return redirect(url_for('main.user_panel_view'))
    

@main.route('/admin')
def admin_panel_view():
    if current_user.is_authenticated:
        if current_user.admin_panel_access:
            from .. import admin
            return admin.index()
        else:
            logging.warning(f'{current_user.login} trying to login to Dashboard.')
            flash(f'Error. User {current_user.login} not accepted here.', 'danger')
            return redirect(url_for('main.login'))
    else:
        return redirect(url_for('main.user_panel_view'))