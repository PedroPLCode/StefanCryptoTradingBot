from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ..forms import LoginForm, RegistrationForm
from ..models import User, Settings
from sqlalchemy import or_
from ..utils.app_utils import send_email, create_new_user, get_ip_address
from .. import db
from ..utils.logging import logger
import logging
from datetime import datetime as dt
from . import main
from .. import limiter

@main.route('/register', methods=['GET', 'POST'])
@limiter.limit("6/hour")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.user_panel_view'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user_ip = get_ip_address(request)
        user_exists = User.query.filter(or_(User.login == form.login.data, User.email == form.email.data)).first()
        if not user_exists:
            new_user = create_new_user(form)
            try:
                db.session.add(new_user)
                db.session.commit()
                logger.info(f'New account registered: {new_user.login} from {user_ip} ')
                flash('Account created successfully. Admin will contact you.', 'success')
                
                try:
                    send_email('piotrek.gaszczynski@gmail.com', 'New User', 'New user registered: ' + new_user.login)
                except Exception as e:
                    logger.error(f'Error sending registration email: {e}')
                    flash('Registration was successful, but there was an error notifying the admin.', 'warning')

            except Exception as e:
                db.session.rollback()
                logger.error(f'New account registration error: {e} from {user_ip}')
                flash('An error occurred while creating your account. Please try again.', 'danger')

                try:
                    send_email('piotrek.gaszczynski@gmail.com', 'Registration error', str(e))
                except Exception as email_error:
                    logger.error(f'Error sending registration error email: {email_error}')

        else:
            logger.info(f'{user_exists.login} {user_exists.email} trying to create new user from {user_ip}. User already exists.')
            flash('This login or email is already in use.', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field.capitalize()}: {error}', 'danger')

    return render_template('registration.html', form=form)


@main.route('/login', methods=['GET', 'POST'])
@limiter.limit("6/hour")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.user_panel_view'))

    form = LoginForm()
    if form.validate_on_submit():
        try:
            user_ip = get_ip_address(request)
            user = User.query.filter_by(login=form.login.data).first()
            if user:
                if not user.account_suspended:
                    if user.check_password(form.password.data):
                        login_user(user)
                        user.last_login = dt.utcnow()
                        db.session.commit()
                        next_page = request.args.get('next')
                        flash(f'Logged in successfully. Welcome back, {user.name}!', 'success')
                        return redirect(next_page or url_for('main.user_panel_view'))
                    else:
                        user.login_errors += 1
                        db.session.commit()
                        logger.warning(f'User {user.name} login error number {user.login_errors} from {user_ip}.')
                        flash(f'User {user.name} login error number {user.login_errors}.', 'danger')

                        if user.login_errors >= 4:
                            user.account_suspended = True
                            db.session.commit()
                            logger.warning(f'User {user.name} suspended from address {user_ip}')
                            flash(f'User {user.name} suspended. Admin will contact you.', 'danger')
                else:
                    logger.warning(f'User {user.name} suspended trying to log in from address {user_ip}')
                    flash(f'User {user.name} suspended. Admin will contact you.', 'danger')
            else:
                logger.warning(f'Bad login attempt from address {user_ip}. User not found')
                flash('Error: Login or Password Incorrect.', 'danger')
        except Exception as e:
            logger.error(f'Error during login process: {e} from {user_ip}')
            try:
                send_email('piotrek.gaszczynski@gmail.com', 'Login error', str(e))
            except Exception as email_error:
                logger.error(f'Error sending login error email: {email_error}')
            flash('An unexpected error occurred during login. Please try again later.', 'danger')

    return render_template('login.html', form=form)


@main.route('/logout')
@login_required
def logout():
    try:
        login = current_user.login
        logout_user()
        logger.info(f'User {login} logged out.')
        flash(f'User {login} logged out successfully.', 'success')
    except Exception as e:
        logger.error(f'Error during logout: {e}')
        send_email('piotrek.gaszczynski@gmail.com', 'Logout error', str(e))
        flash('An error occurred during logout. Please try again.', 'danger')

    return redirect(url_for('main.login'))