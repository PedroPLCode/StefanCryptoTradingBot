from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from ..forms import LoginForm, RegistrationForm
from ..models import User
from sqlalchemy import or_
from .. import db
from ..utils.logging import logger
from datetime import datetime as dt
from . import main
from .. import limiter
from ..utils.app_utils import (
    send_admin_email,
    create_new_user, 
    get_ip_address
)

@main.route('/register', methods=['GET', 'POST'])
@limiter.limit("4/min")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.user_panel_view'))

    form = RegistrationForm()
    if form.validate_on_submit():
        
        user_ip = get_ip_address(request)
        
        user_exists = User.query.filter(or_(
            User.login == form.login.data, 
            User.email == form.email.data
        )).first()
        
        if not user_exists:            
            is_first_user = User.query.count() == 0
            new_user = create_new_user(form)
            new_user.admin_panel_access = True if is_first_user else False
                
            try:
                db.session.add(new_user)
                db.session.commit()
                logger.info(f'New account registered: {new_user.login} from {user_ip} ')
                flash('Account created successfully. Admin will contact you.', 'success')
                
                try:
                    send_admin_email('New User registered', f'New user has been registered in database.\n\nlogin: {new_user.login}\nname: {new_user.name}\nemail: {new_user.email}\ncreation_date: {new_user.creation_date}')
                except Exception as e:
                    logger.error(f'Error sending registration email: {str(e)}')
                    flash('Registration was successful, but there was an error notifying the admin.', 'warning')

            except Exception as e:
                db.session.rollback()
                logger.error(f'New account registration error: {str(e)} from {user_ip}')
                flash('An error occurred while creating your account. Please try again.', 'danger')

                try:
                    send_admin_email('Registration error', str(e))
                except Exception as email_error:
                    logger.error(f'Error sending registration error email {str(email_error)}')

        else:
            logger.warning(f'{user_exists.login} {user_exists.email} trying to create new user from {user_ip}. User already exists.')
            flash('This login or email is already in use.', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field.capitalize()}: {error}', 'danger')

    return render_template('registration.html', form=form)


@main.route('/login', methods=['GET', 'POST'])
@limiter.limit("4/min")
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
                        user.last_login = dt.now()
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
            logger.error(f'Error during login process from {user_ip} {str(e)}')
            try:
                send_admin_email('Login error', str(e))
            except Exception as email_error:
                logger.error(f'Error sending login error email {str(email_error)}')
            flash('An unexpected error occurred during login. Please try again later.', 'danger')

    return render_template('login.html', form=form)


@main.route('/logout')
@login_required
def logout():
    try:
        login = current_user.login
        logout_user()
        flash(f'User {login} logged out successfully.', 'success')
    except Exception as e:
        logger.error(f'Error during logout: {str(e)}')
        send_admin_email('Logout error', str(e))
        flash('An error occurred during logout. Please try again.', 'danger')

    return redirect(url_for('main.login'))