from flask import Flask, render_template, redirect, url_for, flash, request, __version__ as flask_version
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_mail import Mail
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask import current_app
from apscheduler.schedulers.background import BackgroundScheduler
from flask_limiter import Limiter
from flask_cors import CORS
from datetime import datetime as dt
import platform
import sys
import logging
from datetime import datetime
from .. import app, db, limiter, login_manager

@app.errorhandler(404)
def page_not_found(error_msg):
    flash(f'{error_msg}', 'warning')
    return redirect(url_for('main.login'))

@app.errorhandler(429)
@limiter.exempt
def too_many_requests(error_msg):
    return render_template('limiter.html', error_msg=error_msg)

@login_manager.unauthorized_handler
def unauthorized_callback():
    flash('Please log in to access this page.', 'warning')
    return redirect(url_for('main.login'))