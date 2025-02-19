from flask import redirect, url_for, flash
from werkzeug.security import generate_password_hash
from app.models import User
from ..utils.logging import logger
from ..utils.exception_handlers import exception_handler
from ..utils.email_utils import send_admin_email


@exception_handler()
def create_new_user(form):
    """
    Creates a new user based on the provided form data and hashes the password.

    Args:
        form (Form): The form containing the user's registration data.
            - login (str): The user's login name.
            - name (str): The user's full name.
            - email (str): The user's email address.
            - password (str): The user's password (will be hashed).

    Returns:
        User: The newly created User object.

    Raises:
        Exception: If there is an error during the user creation process, the exception is logged, and an email is sent to the admin.
    """
    new_user = User(
        login=form.login.data,
        name=form.name.data,
        email=form.email.data,
        password_hash=generate_password_hash(form.password.data),
    )
    return new_user


def check_if_user_is_authenticated(user, panel_name):
    """
    Checks if the user is authenticated.

    If the user is not authenticated, a warning message is flashed, and the user is redirected
    to the login page. The panel name is dynamically included in the flash message to specify
    which panel requires authentication.

    Args:
        user: The user object to check authentication status.
        panel_name (str): The name of the panel that the user is trying to access.

    Returns:
        Redirect: If the user is not authenticated, redirects to the login page.
    """
    try:
        if not user.is_authenticated:
            flash(f"Please log in to access the {panel_name} panel.", "warning")
            return redirect(url_for("main.login"))
    except Exception as e:
        logger.error(
            f"Exception in check_if_user_is_authenticated user {user.login}: {e}"
        )
        send_admin_email("Exception in check_if_user_is_authenticated", str(e))
        flash(
            "An error occurred while checking authentication. Please try again.",
            "danger",
        )
        return redirect(url_for("main.login"))


def check_if_user_have_control_access(user, panel_name):
    """
    Checks if the user has access to the specified control panel.

    If the user does not have control panel access, a warning is logged, a flash message
    is shown to the user indicating they are not allowed to access the panel,
    and the user is redirected to the user panel view.

    Args:
        user: The user object to check access permissions.
        panel_name (str): The name of the panel that the user is trying to access.

    Returns:
        Redirect: If the user does not have access, redirects to the user panel view.
    """
    try:
        if not user.control_panel_access:
            logger.warning(
                f"{user.login} tried to access the {panel_name} Panel without permission."
            )
            flash(
                f"Error. User {user.login} is not allowed to access the {panel_name} Panel.",
                "danger",
            )
            return redirect(url_for("main.user_panel_view"))
    except Exception as e:
        logger.error(
            f"Exception in check_if_user_have_control_access user {user.login}: {e}"
        )
        send_admin_email("Exception in check_if_user_have_control_access", str(e))
        flash(
            "An unexpected error occurred while checking access permissions. Please try again.",
            "danger",
        )
        return redirect(url_for("main.user_panel_view"))


def check_if_user_is_admin(user):
    """
    Checks if the user has admin panel access.

    If the user does not have admin panel access, a warning is logged, a flash message
    is shown to the user indicating they are not allowed to access the admin panel,
    and the user is redirected to the user panel view.

    Args:
        user: The user object to check admin access.

    Returns:
        Redirect: If the user is not an admin, redirects to the user panel view.
    """
    try:
        if not user.admin_panel_access:
            logger.warning(
                f"{user.login} tried to access the Admin Panel without permission."
            )
            flash(
                f"Error. User {user.login} is not allowed to access the Admin Panel.",
                "danger",
            )
            return redirect(url_for("main.user_panel_view"))
    except Exception as e:
        logger.error(f"Exception in check_if_user_is_admin user {user.login}: {e}")
        send_admin_email("Exception in check_if_user_is_admin", str(e))
        flash(
            "An unexpected error occurred while checking admin access. Please try again.",
            "danger",
        )
        return redirect(url_for("main.user_panel_view"))
