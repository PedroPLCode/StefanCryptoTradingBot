from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ..forms import LoginForm, RegistrationForm
from ..models import User, Settings, admin
import logging
from datetime import datetime as dt
from flask_cors import CORS
from flask_cors import cross_origin
from flask import current_app
from apscheduler.schedulers.background import BackgroundScheduler
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from ..utils.app_utils import send_email

main = Blueprint('main', __name__)

from . import session, panels, context_processors, error_handlers, stefan