from flask import Blueprint, render_template, redirect, url_for, flash
from .models import Settings, TradeHistory
from flask_login import login_required, login_user
from werkzeug.security import generate_password_hash
from .forms import LoginForm, RegistrationForm
from .models import User
from . import db

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def dashboard():
    trades = TradeHistory.query.all()
    return render_template('index.html', trades=trades)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.dashboard'))  # Zmienione na odpowiedni endpoint
    return render_template('login.html', form=form)

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)  # Hashowanie hasła
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Konto zostało utworzone! Możesz się zalogować.', 'success')
        return redirect(url_for('main.login'))  # Zmień na odpowiednią trasę logowania
    return render_template('register.html', form=form)

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