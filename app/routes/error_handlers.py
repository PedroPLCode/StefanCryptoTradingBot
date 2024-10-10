from flask import render_template, redirect, url_for, flash
from .. import app, limiter, login_manager

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