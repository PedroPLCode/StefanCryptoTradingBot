from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ..forms import LoginForm, RegistrationForm
from ..models import User, Settings, Trades
from .. import db
import logging
from datetime import datetime as dt
from . import main

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            login=form.login.data,
            name=form.name.data,
            email=form.email.data,
            password_hash=hashed_password,
        )
        try:
            db.session.add(new_user)
            db.session.commit()
            logging.info(f'New account registered: {new_user.login}')
            flash('Account created successfully. Admin will contact you.', 'success')
            #email do admina
        except Exception as e:
            db.session.rollback() 
            logging.error(f'New account registration error: {e}')
            flash('An error occurred while creating your account. Please try again.', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field.capitalize()}: {error}', 'danger')
    return render_template('register.html', form=form)


@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.user_panel_view'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data).first()
        if user:
            if user.check_password(form.password.data):
                login_user(user)
                next_page = request.args.get('next')
                flash(f'Logged in successfully. Welcome back, {user.name}!', 'success')
                return redirect(next_page or url_for('main.user_panel_view'))
            else:
                user.login_errors += 1
                db.session.commit()
                logging.warning(f'User {user.name} login error number {user.login_errors}.')
                flash(f'User {user.name} login error number {user.login_errors}.', 'danger')

                if user.login_errors >= 4:
                    user.account_suspended = True
                    db.session.commit()
                    logging.warning(f'User {user.name} suspended.')
                    flash(f'User {user.name} suspended. Admin will contact you.', 'danger')
        else:
            logging.warning('Bad login attempt.')
            flash('Error: Login or Password Incorrect.', 'danger')

    return render_template('login.html', form=form)


@main.route('/logout')
@login_required
def logout():
    login = current_user.login
    logout_user()
    logging.info(f'User {login} logged out.')
    flash(f'User {login} logged out succesfully.', 'success')
    return redirect(url_for('main.login'))