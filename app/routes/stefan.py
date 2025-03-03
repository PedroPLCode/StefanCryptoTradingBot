from flask import request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
import pandas as pd
from typing import Callable
from ..models import BotSettings, BacktestSettings
from datetime import datetime
from ..utils.logging import logger
from . import main
from .. import limiter
from ..utils.exception_handlers import exception_handler
from ..utils.reports_utils import generate_trade_report
from ..utils.user_utils import check_if_user_have_control_access
from ..utils.email_utils import (
    send_email,
    send_admin_email
)
from ..utils.bots_utils import (
    stop_all_bots,
    start_all_bots,
    start_single_bot,
    stop_single_bot,
    handle_emergency_sell_order
)


@main.route("/start/<int:bot_id>")
@exception_handler(default_return=lambda: redirect(url_for("main.control_panel_view")))
@login_required
def start_bot(bot_id: int) -> Callable:
    """
    Starts a specific bot based on the provided bot ID.
    Only accessible to users with control panel access.
    """
    check_if_user_have_control_access(current_user, "Control")

    bot_settings = BotSettings.query.filter_by(id=bot_id).first()

    if bot_settings:
        start_single_bot(bot_settings.id, current_user)
    else:
        flash(f"Settings for bot {bot_id} not found.", "danger")
        send_admin_email("Bot not started.", f"Settings for bot {bot_id} not found.")

    return redirect(url_for("main.control_panel_view"))


@main.route("/stop/<int:bot_id>")
@exception_handler(default_return=lambda: redirect(url_for("main.control_panel_view")))
@login_required
def stop_bot(bot_id: int) -> Callable:
    """
    Stops a specific bot based on the provided bot ID.
    If an active trade exists, executes a sell order before stopping.
    """
    check_if_user_have_control_access(current_user, "Control")

    bot_settings = BotSettings.query.filter_by(id=bot_id).first()

    if bot_settings.bot_current_trade.is_active:
        handle_emergency_sell_order(bot_settings)
        send_admin_email(
            f"Bot {bot_settings.id} stopped manually.",
            f"Bot {bot_id} has been stopped manually.\n\nCheck CurrentTrade in Flask Admin Panel.\nCurrentTrade needs to be deactivated and all params needs to be set on 0.",
        )

    if bot_settings:
        stop_single_bot(bot_settings.id, current_user)
    else:
        flash(f"Settings for bot {bot_id} not found.", "danger")
        send_admin_email("Bot not stopped.", f"Settings for bot {bot_id} not found.")

    return redirect(url_for("main.control_panel_view"))


@main.route("/startall")
@exception_handler(default_return=lambda: redirect(url_for("main.control_panel_view")))
@login_required
def start_all():
    """
    Starts all available bots.
    """
    check_if_user_have_control_access(current_user, "Control")

    start_all_bots(current_user)
    return redirect(url_for("main.control_panel_view"))


@main.route("/stopall")
@exception_handler(default_return=lambda: redirect(url_for("main.control_panel_view")))
@login_required
def stop_all():
    """
    Stops all active bots.
    """
    check_if_user_have_control_access(current_user, "Control")

    stop_all_bots(current_user)
    return redirect(url_for("main.control_panel_view"))


@main.route("/refresh")
@exception_handler(default_return=lambda: redirect(url_for("main.control_panel_view")))
@login_required
def refresh():
    """
    Refreshes the Binance API connection.
    """
    check_if_user_have_control_access(current_user, "Control")

    flash("Binance API refreshed.", "success")
    return redirect(url_for("main.control_panel_view"))


@main.route("/report")
@exception_handler(default_return=lambda: redirect(url_for("main.control_panel_view")))
@login_required
def report():
    """
    Sends a trade report email to the currently logged-in user if they have permission.
    Redirects to the user panel if the user is not allowed to receive reports.
    """
    if not current_user.email_raports_receiver:
        logger.warning(
            f"{current_user.login} tried to get email report without permission."
        )
        flash(
            f"Error. User {current_user.login} is not allowed receiving email reports.",
            "danger",
        )
        return redirect(url_for("main.user_panel_view"))

    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    email = current_user.email
    subject = f"{today} Stefan Trades Report"
    report_body = generate_trade_report("7d")

    with current_app.app_context():
        send_email(email, subject, report_body)
        flash(f"Email to {email} sent successfully.", "success")

    return redirect(url_for("main.control_panel_view"))


@main.route("/load_data_for_backtest")
@exception_handler(default_return=lambda: redirect(url_for("main.backtest_panel_view")))
@login_required
def fetch_and_save_data_for_backtest():
    """
    Fetches historical trading data and saves it for backtesting.
    Redirects to the backtest panel view after execution.
    """
    from ..stefan.backtesting import fetch_and_save_data

    check_if_user_have_control_access(current_user, "Control")

    backtest_settings = BacktestSettings.query.first()
    bot_settings = BotSettings.query.filter(
        BotSettings.id == backtest_settings.bot_id
    ).first()
    if bot_settings:
        fetch_and_save_data(backtest_settings, bot_settings)
        flash(
            f"Data for backtest {bot_settings.symbol} fetched and saved in {backtest_settings.csv_file_path}.",
            "success",
        )
    else:
        flash(f"Bot {backtest_settings.bot_id} not found. Data not loaded", "danger")
    return redirect(url_for("main.backtest_panel_view"))


@main.route("/run_backtest")
@exception_handler(default_return=lambda: redirect(url_for("main.backtest_panel_view")))
@login_required
def run_backtest():
    """
    Runs a backtest using stored trading data and settings.
    Redirects to the backtest panel view after execution.
    """
    from ..stefan.backtesting import backtest_strategy
    from ..stefan.logic_utils import is_df_valid

    check_if_user_have_control_access(current_user, "Control")

    backtest_settings = BacktestSettings.query.first()
    bot_settings = BotSettings.query.filter(
        BotSettings.id == backtest_settings.bot_id
    ).first()
    if bot_settings:
        df = pd.read_csv(f"/backtesting/{backtest_settings.csv_file_path}")
        if is_df_valid(df, bot_settings.id):
            df["time"] = pd.to_datetime(df["close_time"])
            backtest_strategy(df, bot_settings, backtest_settings)
            flash("Backtest completed. Read log file", "success")
        else:
            flash("Backtest error. Dataframe empty or too short", "danger")
    else:
        flash(
            f"Bot {backtest_settings.bot_id} not found. Cannot run backtest", "danger"
        )
    return redirect(url_for("main.backtest_panel_view"))


@main.route("/get_df/", methods=["GET"])
@exception_handler(
    default_return=(lambda: (jsonify({"error": "Internal Server Error"}), 500))
)
@login_required
def get_df():
    """
    Retrieves and returns technical analysis data for all bots as a JSON response.
    """
    all_bots_info = BotSettings.query.all()
    if not all_bots_info:
        return jsonify({"error": "Bots not found"}), 404

    all_bots_df = [bot.bot_technical_analysis.df for bot in all_bots_info]
    return jsonify({"all_bots_df": all_bots_df}), 200


@main.route("/emergencystop", methods=["POST"])
@limiter.limit("2/hour")
@exception_handler()
def emergency_stop_all_bots():
    """
    Emergency stops all active bots.
    
    Usage:
        curl -X POST -d "passwd=estop_password" http://localhost/emergencystop
    """
    passwd = request.form.get("passwd")

    if not passwd:
        return jsonify({"error": "Missing password."}), 400

    logger.trade("Emergency stop attempt.")
    send_admin_email("Emergency stop attempt.", "An emergency stop attempt was made.")

    from .. import db
    from ..utils.estop_utils import (
        handle_no_bots,
        process_bot_emergency_stop,
        handle_bots_stopped,
    )

    all_bots_settings = BotSettings.query.all()

    if not all_bots_settings:
        return handle_no_bots()

    bots_stopped = []
    for bot_settings in all_bots_settings:
        result = process_bot_emergency_stop(bot_settings, passwd)
        if result:
            bots_stopped.append(result)

    if bots_stopped:
        db.session.commit()
        return handle_bots_stopped(bots_stopped)
    else:
        return jsonify({"error": "No bots stopped. All attempts failed."}), 403
