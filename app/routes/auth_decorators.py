import functools
import logging
from flask import flash, redirect, url_for, request
from ..utils.email_utils import send_admin_email
from flask_login import current_user

logger = logging.getLogger(__name__)

def requires_authentication(panel_name):
    """
    A decorator that checks if the user is authenticated before accessing a route.

    If the user is not authenticated:
        - A warning message is flashed.
        - The user is redirected to the login page.
        - The panel name is included in the flash message.
        - Errors are logged and an email notification is sent.

    Args:
        panel_name (str): The name of the panel that requires authentication.

    Returns:
        function: A wrapped function that enforces authentication.
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapped_view(*args, **kwargs):
            try:
                if not current_user.is_authenticated:
                    flash(f'Please log in to access the {panel_name} panel.', 'warning')
                    return redirect(url_for('main.login', next=request.url))
            except Exception as e:
                logger.error(f"Exception in decorator requires_authentication (panel: {panel_name}): {e}")
                send_admin_email(f'Exception in decorator requires_authentication ({panel_name})', str(e))
                flash('An error occurred while checking authentication. Please try again.', 'danger')
                return redirect(url_for('main.login'))

            return view_func(*args, **kwargs)

        return wrapped_view
    return decorator


def requires_control_access(panel_name):
    """
    A decorator that checks if the user has access to the specified control panel.

    If the user does not have access:
        - A warning is logged.
        - A flash message is displayed.
        - The user is redirected to the user panel.
        - Errors are logged and an email notification is sent if an exception occurs.

    Args:
        panel_name (str): The name of the panel that requires control panel access.

    Returns:
        function: A wrapped function that enforces access control.
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapped_view(*args, **kwargs):
            try:
                if not current_user.control_panel_access:
                    logger.warning(f'{current_user.login} tried to access the {panel_name} Panel without permission.')
                    flash(f'Error. User {current_user.login} is not allowed to access the {panel_name} Panel.', 'danger')
                    return redirect(url_for('main.user_panel_view'))
            except Exception as e:
                logger.error(f"Exception in decorator requires_control_access (panel: {panel_name}): {e}")
                send_admin_email(f'Exception in decorator requires_control_access ({panel_name})', str(e))
                flash('An unexpected error occurred while checking access permissions. Please try again.', 'danger')
                return redirect(url_for('main.user_panel_view'))

            return view_func(*args, **kwargs)

        return wrapped_view
    return decorator


def requires_admin_access():
    """
    A decorator that checks if the user has admin panel access.

    If the user does not have access:
        - A warning is logged.
        - A flash message is displayed.
        - The user is redirected to the user panel.
        - Errors are logged and an email notification is sent if an exception occurs.

    Returns:
        function: A wrapped function that enforces admin access control.
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapped_view(*args, **kwargs):
            try:
                if not current_user.admin_panel_access:
                    logger.warning(f'{current_user.login} tried to access the Admin Panel without permission.')
                    flash(f'Error. User {current_user.login} is not allowed to access the Admin Panel.', 'danger')
                    return redirect(url_for('main.user_panel_view'))
            except Exception as e:
                logger.error(f"Exception in decorator requires_admin_access: {e}")
                send_admin_email('Exception in decorator requires_admin_access', str(e))
                flash('An unexpected error occurred while checking admin access. Please try again.', 'danger')
                return redirect(url_for('main.user_panel_view'))

            return view_func(*args, **kwargs)

        return wrapped_view
    return decorator