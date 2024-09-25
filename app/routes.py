from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import LoginForm, RegistrationForm
from .models import User, Settings, TradeHistory
from . import db
import logging
from datetime import datetime as dt

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html')
    else:
        flash('Please log in to access app.', 'warning')
        return redirect(url_for('main.login'))

    
@main.route('/dashboard')
def dashboard_view():
    if current_user.is_authenticated:
        if current_user.accepted:
            return render_template('dashboard.html')
        else:
            logging.warning(f'{current_user.login} trying to login to Dashboard.')
            flash(f'Error. User {current_user.login} not accepted here.', 'danger')
            return redirect(url_for('main.login'))
    else:
        return redirect(url_for('main.index'))
    

    
@main.route('/admin')
def admin_view():
    if current_user.is_authenticated:
        if current_user.admin:
            return admin.index()
        else:
            logging.warning(f'{current_user.login} trying to login to Dashboard.')
            flash(f'Error. User {current_user.login} not accepted here.', 'danger')
            return redirect(url_for('main.login'))
    else:
        return redirect(url_for('main.index'))


@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:  # Check if already logged in
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        else:
            logging.warning(f'Error.')
            flash(f'Error.', 'danger')
    return render_template('login.html', form=form)


@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(login=form.login.data, name=form.name.data, email=form.email.data, password_hash=hashed_password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully. Please wait for admin confirmation', 'success')
        except Exception as e:
            db.session.rollback()  # Rollback in case of an error
            flash('An error occurred while creating your account. Please try again.', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field.capitalize()}: {error}', 'danger')
    return render_template('register.html', form=form)


@main.route('/logout')
@login_required
def logout():
    login = current_user.login
    logout_user()
    logging.info(f'User {login} logged out.')
    flash(f'User {login} logged out.', 'success')
    return redirect(url_for('main.login'))

@main.route('/start_bot')
@login_required
def start_bot():
    settings = Settings.query.first()
    settings.trading_enabled = True
    db.session.commit()
    return redirect(url_for('main.dashboard'))

@main.route('/stop_bot')
@login_required
def stop_bot():
    settings = Settings.query.first()
    settings.trading_enabled = False
    db.session.commit()
    return redirect(url_for('main.dashboard'))