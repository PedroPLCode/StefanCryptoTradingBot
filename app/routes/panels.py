from flask import render_template, redirect, url_for, request
from flask_login import current_user
import json
import pandas as pd
from ..models import BotSettings, BacktestResult
from .. import db
from ..utils.exception_handlers import exception_handler
from ..routes.auth_decorators import (
    requires_authentication,
    requires_control_access,
    requires_admin_access,
)
from ..utils.logging import logger
from . import main
from ..stefan.api_utils import (
    fetch_system_status,
    fetch_account_status,
    fetch_server_time,
)
from ..utils.trades_utils import show_account_balance
from ..stefan.logic_utils import is_df_valid


@main.route("/")
@exception_handler(default_return=lambda: redirect(url_for("main.login")))
@requires_authentication("User")
def user_panel_view():
    """
    View for the user panel. This view is accessible only to authenticated users.

    If the user is authenticated, the system status, account status, and server time
    are fetched and displayed in the user panel. If an error occurs during fetching the data,
    an error message is flashed, and the user is redirected to the login page.

    Returns:
        Rendered user_panel.html template with user data, account status, and system status.
        If an error occurs, redirects to the login page.
    """
    binance_status = fetch_system_status()
    account_status = fetch_account_status()
    server_time = fetch_server_time()
    return render_template(
        "user_panel.html",
        user=current_user,
        account_status=account_status,
        binance_status=binance_status,
        server_time=server_time,
    )


@main.route("/control")
@exception_handler(default_return=lambda: redirect(url_for("main.user_panel_view")))
@requires_authentication("Control")
@requires_control_access("Control")
def control_panel_view():
    """
    View for the control panel. This view is accessible only to authenticated users with control panel access.

    If the user is not authenticated or doesn't have control panel access, they are redirected
    to the user panel or login page. The control panel fetches bot settings and account status
    for all bots, updating their balance.

    Returns:
        Rendered control_panel.html template with all bot settings.
        If an error occurs, redirects to the user panel.
    """
    all_bots_settings = BotSettings.query.all()

    for bot_info in all_bots_settings:
        account_status = fetch_account_status(bot_info.id)
        cryptocoin_symbol = bot_info.symbol[:3]
        stablecoin_symbol = bot_info.symbol[-4:]
        balance = show_account_balance(
            bot_info.symbol, account_status, {cryptocoin_symbol, stablecoin_symbol}
        )
        bot_info.balance = balance

    return render_template(
        "control_panel.html",
        user=current_user,
        all_bots_settings=all_bots_settings,
    )


@main.route("/analysis", methods=["GET", "POST"])
@exception_handler(default_return=lambda: redirect(url_for("main.user_panel_view")))
@requires_authentication("Technical Analysis")
@requires_control_access("Technical Analysis")
def analysis_panel_view():
    """
    View for the technical analysis panel. This view is accessible only to authenticated users
    with control panel access.

    Displays selected technical analysis indicators for all bots. Users can update the indicators
    via a POST request. If the bot's technical analysis data is empty, no plot is generated.

    Returns:
        Rendered technical_analysis.html template with all bot info and selected indicators.
        If an error occurs, redirects to the user panel.
    """
    from ..utils.plot_utils import plot_selected_ta_indicators

    all_bots_info = BotSettings.query.all()
    indicators = ["rsi", "macd"]

    for bot_info in all_bots_info:

        indicators = bot_info.selected_plot_indicators or ["rsi", "macd"]

        if request.method == "POST":
            bot_id = request.form.get("bot_id")
            if str(bot_id) == str(bot_info.id):
                indicators = request.form.getlist("indicators")
                bot_info.selected_plot_indicators = indicators
                db.session.commit()

        technical_analysis_data = bot_info.bot_technical_analysis
        df = technical_analysis_data.get_df()

        if not is_df_valid(df, bot_info):
            logger.warning(f"Bot {bot_info.symbol} returned an empty DataFrame.")
            bot_info.plot_url = None
            continue

        bot_info.plot_url = plot_selected_ta_indicators(
            df, indicators, bot_info, bot_info.lookback_period
        )

    return render_template(
        "technical_analysis.html",
        user=current_user,
        all_bots_info=all_bots_info,
        selected_indicators=indicators,
    )


@main.route("/backtest")
@exception_handler(default_return=lambda: redirect(url_for("main.user_panel_view")))
@requires_authentication("Backtest")
@requires_control_access("Backtest")
def backtest_panel_view():
    """
    View for the backtest panel. This view is accessible only to authenticated users
    with control panel access.

    Displays all backtest results, parsing and displaying the trade logs for each result.

    Returns:
        Rendered backtest_panel.html template with all backtest results.
        If an error occurs, redirects to the user panel.
    """
    all_backtest_results = BacktestResult.query.all()
    for result in all_backtest_results:
        result.trade_log = json.loads(result.trade_log)

    return render_template(
        "backtest_panel.html",
        user=current_user,
        all_backtest_results=all_backtest_results,
    )


@main.route("/trades")
@exception_handler(default_return=lambda: redirect(url_for("main.user_panel_view")))
@requires_authentication("Trades")
@requires_control_access("Trades")
def current_trades_view():
    """
    View for the trades panel. This view is accessible only to authenticated users
    with control panel access.

    Displays current trades for all bots. The view processes trade history, and if valid
    trades exist, a balance plot is generated for each bot.

    Returns:
        Rendered trades_history.html template with all bot data.
        If an error occurs, redirects to the user panel.
    """
    from ..utils.plot_utils import create_balance_plot

    all_bots = BotSettings.query.all()

    for bot in all_bots:
        valid_trades = [
            trade for trade in bot.bot_trades_history if trade.stablecoin_balance
        ]
        if valid_trades:
            bot.transaction_data = {
                "trade_id": [trade.trade_id for trade in valid_trades],
                "stablecoin_balance": [
                    trade.stablecoin_balance for trade in valid_trades
                ],
            }
            df = pd.DataFrame(bot.transaction_data)
            if not df.empty and df["stablecoin_balance"].sum() > 0:
                bot.plot_url = create_balance_plot(df)
            else:
                bot.plot_url = None
        else:
            bot.plot_url = None

    return render_template("trades_history.html", user=current_user, all_bots=all_bots)


@main.route("/admin")
@exception_handler(default_return=lambda: redirect(url_for("main.user_panel_view")))
@requires_authentication("Admin")
@requires_admin_access()
def admin_panel_view():
    """
    View for the admin panel. This view is accessible only to authenticated users
    with admin panel access.

    If the user is authenticated and has admin access, they are redirected to the admin
    panel index. If an error occurs, the user is redirected to the user panel.

    Returns:
        Redirects to the admin panel index or redirects to the user panel in case of error.
    """
    return redirect(url_for("admin.index"))
