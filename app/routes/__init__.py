from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ..forms import LoginForm, RegistrationForm
from ..models import User, Settings, Trades
import logging
from datetime import datetime as dt
from flask_cors import CORS
from flask_cors import cross_origin
from apscheduler.schedulers.background import BackgroundScheduler
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from ..utils.app_utils import send_email

main = Blueprint('main', __name__)
"""
def start_scheduler():
    logging.info('Starting scheduller.')
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=False, 
                      trigger="interval",
                      hours=24)
    scheduler.start()

start_scheduler()
"""

from . import session, panels, admin, stefan