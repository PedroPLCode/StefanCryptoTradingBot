from flask import redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from ..models import Settings, CurrentTrade
from ..utils.logging import logger
from . import main
from ..utils.api_utils import place_sell_order
from ..utils.app_utils import (
    send_email, 
    send_admin_email,
    generate_trade_report
)
from ..utils.stefan_utils import (
    stop_all_bots, 
    start_all_bots, 
    start_single_bot, 
    stop_single_bot
)

@main.route('/start/<int:bot_id>')
@login_required
def start_bot(bot_id):
    if not current_user.control_panel_access:
        logger.warning(f'{current_user.login} tried to control Bot without permission.')
        flash(f'Error. User {current_user.login} is not allowed to control the Bot.', 'danger')
        return redirect(url_for('main.user_panel_view'))

    try:
        settings = Settings.query.filter_by(id=bot_id).first()

        if settings:
            start_single_bot(settings, current_user)
        else:
            flash(f'Settings for bot {bot_id} not found.', 'danger')
            send_admin_email('Bot not started.', f'Settings for bot {bot_id} not found.')

        return redirect(url_for('main.control_panel_view'))

    except Exception as e:
        logger.error(f'Error while starting bot {bot_id}: {e}')
        flash(f'An error occurred while starting bot {bot_id}.', 'danger')
        return redirect(url_for('main.control_panel_view'))


@main.route('/stop/<int:bot_id>')
@login_required
def stop_bot(bot_id):
    if not current_user.control_panel_access:
        logger.warning(f'{current_user.login} tried to control Bot without permission.')
        flash(f'Error. User {current_user.login} is not allowed to control the Bot.', 'danger')
        return redirect(url_for('main.user_panel_view'))
    
    try:
        settings = Settings.query.filter_by(id=bot_id).first()
        current_trade = CurrentTrade.query.filter_by(id=bot_id).first()
        
        if current_trade.is_active:
            place_sell_order(settings.symbol, current_trade)
        
        if settings:
            stop_single_bot(settings, current_user)
        else:
            flash(f'Settings for bot {bot_id} not found.', 'danger')
            send_admin_email('Bot not stopped.', f'Settings for bot {bot_id} not found.')

        return redirect(url_for('main.control_panel_view'))

    except Exception as e:
        logger.error(f'Error while stopping bot {bot_id}: {e}')
        flash(f'An error occurred while stopping bot {bot_id}.', 'danger')
        return redirect(url_for('main.control_panel_view'))
    

@main.route('/startall')
@login_required
def start_all(current_user):
    if not current_user.control_panel_access:
        logger.warning(f'{current_user.login} tried to control Bot without permission.')
        flash(f'Error. User {current_user.login} is not allowed to control the Bot.', 'danger')
        return redirect(url_for('main.user_panel_view'))
    
    try:
        start_all_bots(current_user)
        return redirect(url_for('main.control_panel_view'))

    except Exception as e:
        logger.error(f'Error while stopping all bots: {e}')
        flash(f'An error occurred while stopping all bots.', 'danger')
        return redirect(url_for('main.control_panel_view'))
    
    
@main.route('/stopall')
@login_required
def stop_all():
    if not current_user.control_panel_access:
        logger.warning(f'{current_user.login} tried to control Bot without permission.')
        flash(f'Error. User {current_user.login} is not allowed to control the Bot.', 'danger')
        return redirect(url_for('main.user_panel_view'))
    
    try:
        stop_all_bots(current_user)
        return redirect(url_for('main.control_panel_view'))

    except Exception as e:
        logger.error(f'Error while stopping all bots: {e}')
        flash(f'An error occurred while stopping all bots.', 'danger')
        return redirect(url_for('main.control_panel_view'))


@main.route('/refresh')
@login_required
def refresh():
    if not current_user.control_panel_access:
        logger.warning(f'{current_user.login} tried to control Bot without permission.')
        flash(f'Error. User {current_user.login} is not allowed to control Bot.', 'danger')
        return redirect(url_for('main.user_panel_view'))
    
    try:
        flash('Binance API refreshed.', 'success')
        return redirect(url_for('main.control_panel_view'))

    except Exception as e:
        logger.error(f'Error refreshing Binance API: {e}')
        send_admin_email('Error refreshing Binance API', str(e))
        flash('An error occurred while refreshing the Binance API. The admin has been notified.', 'danger')
        return redirect(url_for('main.control_panel_view'))


@main.route('/report')
@login_required
def report():
    if not current_user.email_raports_receiver:
        logger.warning(f'{current_user.login} tried to get email rapirt.')
        flash(f'Error. User {current_user.login} is not allowed receiving email raports.', 'danger')
        return redirect(url_for('main.user_panel_view'))
    
    email = current_user.email
    subject = 'Stefan Test Raport'
    report_body = generate_trade_report('7d')
    
    try:
        with current_app.app_context():
            send_email(email, subject, report_body)
            flash(f'Email to {email} sent successfully.', 'success')
    except Exception as e:
        logger.error(f'Error sending email to {email}: {e}')
        flash('An error occurred while sending the email. The admin has been notified.', 'danger')
        send_admin_email('Error sending email', str(e))
    
    return redirect(url_for('main.control_panel_view'))