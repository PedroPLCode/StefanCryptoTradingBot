from flask import render_template, redirect, url_for, flash
from .. import app, limiter, login_manager


@app.errorhandler(404)
def page_not_found(error_msg):
    """
    Handles 404 errors (Page Not Found). This function is triggered when the requested page does not exist.

    Args:
        error_msg (str): The error message associated with the 404 error.

    Returns:
        redirect: Redirects to the login page with a warning flash message.
    """
    flash(f"{error_msg}", "warning")
    return redirect(url_for("main.login"))


@app.errorhandler(429)
@limiter.exempt
def too_many_requests(error_msg):
    """
    Handles 429 errors (Too Many Requests). This function is triggered when a user exceeds the rate limit.

    Args:
        error_msg (str): The error message associated with the 429 error.

    Returns:
        render_template: Renders a custom error page (limiter.html) with the provided error message.
    """
    return render_template("limiter.html", error_msg=error_msg)


@login_manager.unauthorized_handler
def unauthorized_callback():
    """
    Handles unauthorized access attempts. This function is triggered when a user tries to access a protected page
    without being logged in.

    Returns:
        redirect: Redirects the user to the login page with a warning flash message.
    """
    flash("Please log in to access this page.", "warning")
    return redirect(url_for("main.login"))
