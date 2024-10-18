from flask import render_template, redirect, url_for, flash
from flask_login import current_user
from ..models import BotSettings
from ..utils.logging import logger
from . import main
from ..utils.api_utils import (
    fetch_system_status, 
    fetch_account_status, 
    fetch_server_time
)
from ..utils.app_utils import (
    show_account_balance, 
    send_admin_email
)

@main.route('/')
def user_panel_view():
    if current_user.is_authenticated:
        try:
            binance_status = fetch_system_status()
            account_status = fetch_account_status()
            server_time = fetch_server_time()
            return render_template(
                'user_panel.html',
                user=current_user, 
                account_status=account_status, 
                binance_status=binance_status, 
                server_time=server_time
            )
        except Exception as e:
            logger.error(f"Error in user_panel_view: {e}")
            send_admin_email('Error in user panel view', str(e))
            flash('An error occurred while fetching account data. Please try again later.', 'danger')
            return redirect(url_for('main.login'))
    else:
        flash('Please log in to access the app.', 'warning')
        return redirect(url_for('main.login'))

    
@main.route('/control')
def control_panel_view():
    if not current_user.is_authenticated:
        flash('Please log in to access the control panel.', 'warning')
        return redirect(url_for('main.login'))

    if not current_user.control_panel_access:
        logger.warning(f'{current_user.login} tried to access the Control Panel without permission.')
        flash(f'Error. User {current_user.login} is not allowed to access the Control Panel.', 'danger')
        return redirect(url_for('main.user_panel_view'))

    try:
        all_bots_settings = BotSettings.query.all()
        
        for bot_info in all_bots_settings:
            account_status = fetch_account_status(bot_info.id)
            cryptocoin_symbol = bot_info.symbol[:3]
            stablecoin_symbol = bot_info.symbol[-4:]
            balance = show_account_balance(
                account_status, 
                {cryptocoin_symbol, stablecoin_symbol})
            bot_info.balance = balance

        return render_template(
            'control_panel.html', 
            user=current_user, 
            all_bots_settings=all_bots_settings, 
            account_status=account_status, 
        )

    except Exception as e:
        logger.error(f'Error loading control panel: {e}')
        send_admin_email('Error loading control panel', str(e))
        flash('An error occurred while loading the control panel. The admin has been notified.', 'danger')
        return redirect(url_for('main.user_panel_view'))
    
    
@main.route('/trades')
def current_trades_view():
    if not current_user.is_authenticated:
        flash('Please log in to access the trades panel.', 'warning')
        return redirect(url_for('main.login'))

    if not current_user.control_panel_access:
        logger.warning(f'{current_user.login} tried to access the Trades Panel without permission.')
        flash(f'Error. User {current_user.login} is not allowed to access the Trades Panel.', 'danger')
        return redirect(url_for('main.user_panel_view'))

    try:
        all_bots = BotSettings.query.all()

        return render_template(
            'trades_history.html', 
            user=current_user, 
            all_bots=all_bots
        )

    except Exception as e:
        logger.error(f'Error loading trades panel: {e}')
        send_admin_email('Error loading trades panel', str(e))
        flash('An error occurred while loading the trades panel. The admin has been notified.', 'danger')
        return redirect(url_for('main.user_panel_view'))


@main.route('/admin')
def admin_panel_view():
    if not current_user.is_authenticated:
        flash('Please log in to access the admin panel.', 'warning')
        return redirect(url_for('main.login'))

    if not current_user.admin_panel_access:
        logger.warning(f'{current_user.login} tried to access the Admin Panel without permission.')
        flash(f'Error. User {current_user.login} is not allowed to access the Admin Panel.', 'danger')
        return redirect(url_for('main.user_panel_view'))

    try:
        return redirect(url_for('admin.index'))

    except Exception as e:
        logger.error(f'Error accessing admin panel: {e}')
        send_admin_email('Error accessing admin panel', str(e))
        flash('An error occurred while accessing the admin panel. The admin has been notified.', 'danger')
        return redirect(url_for('main.user_panel_view'))