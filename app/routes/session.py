from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from ..forms import LoginForm, RegistrationForm
from ..models import User
from typing import Union, Optional
from sqlalchemy import or_
from .. import db
from ..utils.logging import logger
from ..utils.exception_handlers import exception_handler
from datetime import datetime as dt
from . import main
from .. import limiter
from ..utils.user_utils import create_new_user
from ..utils.email_utils import send_admin_email
from ..utils.app_utils import get_ip_address


@main.route("/register", methods=["GET", "POST"])
@limiter.limit("4 per hour")
@exception_handler(default_return=False)
def register():
    """
    Handles the user registration process. If the user is authenticated, they are redirected
    to their user panel. If the user submits the registration form, the function checks if
    the login or email already exists in the database, and if not, creates a new user account.
    It also sends an email to the admin notifying them of the registration or any errors during the process.

    If the registration is successful, a success message is flashed. In case of an error,
    an appropriate error message is flashed, and the admin is notified about the error.

    Returns:
        render_template: Renders the registration page with the form, or redirects
        if the user is already logged in.
    """
    if current_user.is_authenticated:
        return redirect(url_for("main.user_panel_view"))

    form = RegistrationForm()

    if form.validate_on_submit():
        user_ip = get_ip_address(request)

        user_exists = User.query.filter(
            or_(User.login == form.login.data, User.email == form.email.data)
        ).first()

        if user_exists:
            logger.warning(
                f"{user_exists.login} {user_exists.email} trying to create new user from {user_ip}. User already exists."
            )
            flash("This login or email is already in use.", "danger")
        else:
            is_first_user_in_db = User.query.count() == 0
            new_user = create_new_user(form)
            new_user.admin_panel_access = True if is_first_user_in_db else False

            try:
                db.session.add(new_user)
                db.session.commit()
                logger.info(f"New account registered: {new_user.login} from {user_ip}")
                flash(
                    "Account created successfully. Admin will contact you.", "success"
                )

                try:
                    send_admin_email(
                        "New User registered",
                        f"StefanCryptoTradingBot\nNew user has been registered in the database.\n\nlogin: {new_user.login}\nname: {new_user.name}\nemail: {new_user.email}\ncreation_date: {new_user.creation_date}",
                    )
                except Exception as e:
                    logger.error(f"Error sending registration email: {str(e)}")
                    flash(
                        "Registration was successful, but there was an error notifying the admin.",
                        "warning",
                    )

            except Exception as e:
                db.session.rollback()
                logger.error(f"New account registration error: {str(e)} from {user_ip}")
                flash(
                    "An error occurred while creating your account. Please try again.",
                    "danger",
                )

                try:
                    send_admin_email(
                        "StefanCryptoTradingBot\nRegistration error",
                        f"New User Registration error.\n{str(e)}",
                    )
                except Exception as email_error:
                    logger.error(
                        f"Error sending registration error email {str(email_error)}"
                    )

    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field.capitalize()}: {error}", "danger")

    return render_template("user/registration.html", form=form)


@main.route("/login", methods=["GET", "POST"])
@limiter.limit("4 per hour")
@exception_handler(default_return=False)
def login():
    """
    Handles the user login process. If the user is already authenticated, redirects them
    to their user panel. Otherwise, it processes the login form, checks the user's credentials,
    and logs them in if valid. It also handles login errors and account suspension due to
    multiple failed login attempts.

    Returns:
        render_template: Renders the login page with the form or redirects after a successful login.
    """
    if current_user.is_authenticated:
        return redirect(url_for("main.user_panel_view"))

    form = LoginForm()
    if form.validate_on_submit():
        try:
            user_ip = get_ip_address(request)
            user = User.query.filter_by(login=form.login.data).first()

            if not user:
                logger.error(f"Bad login attempt. User not found from {user_ip}")
                flash("Error: Login or Password Incorrect.", "danger")
                return render_template("user/login.html", form=form)

            if user.account_suspended:
                logger.error(
                    f"User {user.name} suspended trying to log in from {user_ip}"
                )
                flash(f"User {user.name} suspended. Admin will contact you.", "danger")
                return render_template("user/login.html", form=form)

            if not user.check_password(form.password.data):
                handle_failed_login(user, user_ip)
                return render_template("user/login.html", form=form)

            handle_successful_login(user)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.user_panel_view"))

        except Exception as e:
            logger.error(
                f"Error during login process. Error details: {str(e)} from {user_ip}"
            )
            flash(
                "An unexpected error occurred during login. Please try again later.",
                "danger",
            )
            return render_template("user/login.html", form=form)

    return render_template("user/login.html", form=form)


@exception_handler(default_return=False)
def handle_successful_login(user: User) -> Union[Optional[int], bool]:
    """
    Handles the actions required for a successful user login.

    This function logs in the user, updates their last login timestamp,
    commits the changes to the database, and displays a success message.

    Args:
        user (User): The user object representing the authenticated user.

    Returns:
        None
    """
    login_user(user)
    user.last_login = dt.now()
    db.session.commit()
    flash(f"Logged in successfully. Welcome back, {user.name}!", "success")
    return True


@exception_handler(default_return=False)
def handle_failed_login(user: User, user_ip: str) -> Union[Optional[int], bool]:
    """
    Handles a failed login attempt for a user.

    This function increments the user's login error count, logs a warning,
    and displays an error message. If the user exceeds the allowed number
    of failed attempts, their account is suspended.

    Args:
        user (User): The user object attempting to log in.
        user_ip (str): The IP address from which the login attempt was made.

    Returns:
        None
    """
    user.login_errors += 1
    db.session.commit()
    logger.warning(
        f"User {user.name} login error number {user.login_errors} from {user_ip}."
    )
    flash(f"User {user.name} login error number {user.login_errors}.", "danger")

    if user.login_errors >= 4:
        user.account_suspended = True
        db.session.commit()
        logger.warning(f"User {user.name} suspended from address {user_ip}")
        flash(f"User {user.name} suspended. Admin will contact you.", "danger")

    return True


@main.route("/logout")
@exception_handler()
@login_required
def logout():
    """
    Logs out the currently authenticated user, flashes a success message, and redirects to the login page.

    This function performs the following steps:
    - Attempts to log out the user using Flask-Login's `logout_user` function.
    - Flashes a success message with the user's login name.
    - If an error occurs, logs the exception and sends an email to the admin, then flashes an error message.

    Returns:
        Redirect: Redirects the user to the login page.
    """
    login = current_user.login
    logout_user()
    flash(f"User {login} logged out successfully.", "success")

    return redirect(url_for("main.login"))
