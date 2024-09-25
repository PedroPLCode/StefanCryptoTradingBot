from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ..forms import LoginForm, RegistrationForm
from ..models import User, Settings, Trades
from .. import db
import logging
from datetime import datetime as dt
from . import main

@main.route('/start')
@login_required
def start_bot():
    settings = Settings.query.first()
    settings.trading_enabled = True
    db.session.commit()
    return redirect(url_for('main.dashboard'))


@main.route('/stop')
@login_required
def stop_bot():
    settings = Settings.query.first()
    settings.trading_enabled = False
    db.session.commit()
    return redirect(url_for('main.dashboard'))