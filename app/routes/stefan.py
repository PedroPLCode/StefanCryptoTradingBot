from flask import redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from ..models import BotSettings
from datetime import datetime
from ..utils.logging import logger
from . import main
from ..stefan.api_utils import place_sell_order
from ..utils.app_utils import (
    send_email, 
    send_admin_email,
    generate_trade_report,
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
        bot_settings = BotSettings.query.filter_by(id=bot_id).first()

        if bot_settings:
            start_single_bot(bot_settings.id, current_user)
        else:
            flash(f'Settings for bot {bot_id} not found.', 'danger')
            send_admin_email('Bot not started.', f'Settings for bot {bot_id} not found.')

        return redirect(url_for('main.control_panel_view'))

    except Exception as e:
        logger.error(f'Exception in start_bot bot {bot_id}: {str(e)}')
        flash(f'Error while starting bot {bot_id}.', 'danger')
        send_admin_email(f'Exception in start_bot bot {bot_id}', str(e))
        return redirect(url_for('main.control_panel_view'))


@main.route('/stop/<int:bot_id>')
@login_required
def stop_bot(bot_id):
    if not current_user.control_panel_access:
        logger.warning(f'{current_user.login} tried to control Bot without permission.')
        flash(f'Error. User {current_user.login} is not allowed to control the Bot.', 'danger')
        return redirect(url_for('main.user_panel_view'))
    
    try:
        bot_settings = BotSettings.query.filter_by(id=bot_id).first()
        
        if bot_settings.bot_current_trade.is_active:
            place_sell_order(bot_settings.id)
        
        if bot_settings:
            stop_single_bot(bot_settings.id, current_user)
        else:
            flash(f'Settings for bot {bot_id} not found.', 'danger')
            send_admin_email('Bot not stopped.', f'Settings for bot {bot_id} not found.')

        return redirect(url_for('main.control_panel_view'))

    except Exception as e:
        logger.error(f'Exception in stop_bot bot {bot_id}: {str(e)}')
        flash(f'An error occurred while stopping bot {bot_id}.', 'danger')
        send_admin_email(f'Exception in stop_bot bot {bot_id}', str(e))
        return redirect(url_for('main.control_panel_view'))
    

@main.route('/startall')
@login_required
def start_all():
    if not current_user.control_panel_access:
        logger.warning(f'{current_user.login} tried to control Bot without permission.')
        flash(f'Error. User {current_user.login} is not allowed to control the Bot.', 'danger')
        return redirect(url_for('main.user_panel_view'))
    
    try:
        start_all_bots(current_user)
        return redirect(url_for('main.control_panel_view'))

    except Exception as e:
        logger.error(f'Exception in start_all: {str(e)}')
        flash(f'An error occured while starting bots.', 'danger')
        send_admin_email(f'Exception in start_all', str(e))
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
        logger.error(f'Exception in stop_all: {str(e)}')
        flash(f'An error occurred while stopping bots.', 'danger')
        send_admin_email(f'Exception in stop_all.', str(e))
        return redirect(url_for('main.control_panel_view'))


@main.route('/refresh')
@login_required
def refresh():
    if not current_user.control_panel_access:
        logger.warning(f'{current_user.login} tried to Refresh control panel without permission.')
        flash(f'Error. User {current_user.login} is not allowed to control Bot.', 'danger')
        return redirect(url_for('main.user_panel_view'))
    
    try:
        flash('Binance API refreshed.', 'success')
        return redirect(url_for('main.control_panel_view'))

    except Exception as e:
        logger.error(f'Exception in refresh: {str(e)}')
        send_admin_email('Exception in refresh', str(e))
        flash('An error occurred while refreshing the Binance API. The admin has been notified.', 'danger')
        return redirect(url_for('main.control_panel_view'))


@main.route('/report')
@login_required
def report():
    if not current_user.email_raports_receiver:
        logger.warning(f'{current_user.login} tried to get email rapirt without permission.')
        flash(f'Error. User {current_user.login} is not allowed receiving email raports.', 'danger')
        return redirect(url_for('main.user_panel_view'))
    
    now = datetime.now()
    today = now.strftime('%Y-%m-%d')
    email = current_user.email
    subject = f'{today} Stefan Trades Report'
    report_body = generate_trade_report('7d')
    
    try:
        with current_app.app_context():
            send_email(email, subject, report_body)
            flash(f'Email to {email} sent successfully.', 'success')
    except Exception as e:
        logger.error(f'Exception in report email {email}: {str(e)}')
        flash('An error occurred while sending the email. The admin has been notified.', 'danger')
        send_admin_email(f'Exception in report email {email}', str(e))
    
    return redirect(url_for('main.control_panel_view'))