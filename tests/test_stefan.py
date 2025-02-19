import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.models import Settings
from app.stefan.trading_bot import run_single_bot_trading_logic


@pytest.fixture
def test_app():
    from app import app

    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    with app.app_context():
        yield app


@pytest.fixture
def mock_settings():
    with test_app.app_context():
        settings = Settings()
        settings.bot_running = True
        settings.symbol = "BTCUSDC"
        settings.trailing_stop_pct = 0.05
        settings.interval = "1m"
        settings.lookback_period = "1h"
        return settings


@pytest.fixture
def mock_trade():
    with test_app.app_context():
        trade = MagicMock()
        trade.trailing_stop_loss = 0.95
        trade.previous_price = 100
        return trade


@patch("test_app.stefan.stefan.current_app")
@patch("test_app.stefan.stefan.fetch_data")
@patch("test_app.stefan.stefan.calculate_indicators")
@patch("test_app.stefan.stefan.check_buy_signal")
@patch("test_app.stefan.stefan.place_buy_order")
@patch("test_app.stefan.stefan.place_sell_order")
@patch("test_app.stefan.stefan.load_current_trade", return_value=None)
@patch("test_app.stefan.stefan.save_trailing_stop_loss")
@patch("test_app.stefan.stefan.save_previous_price")
@patch("test_app.stefan.stefan.logger")
def test_run_trading_logic_buy(
    mock_logger,
    mock_save_previous_price,
    mock_save_trailing_stop_loss,
    mock_load_current_trade,
    mock_place_sell_order,
    mock_place_buy_order,
    mock_check_buy_signal,
    mock_calculate_indicators,
    mock_fetch_data,
    mock_current_app,
    mock_settings,
):

    mock_current_app.app_context.return_value.__enter__.return_value = None
    mock_settings.return_value = mock_settings
    mock_fetch_data.return_value = MagicMock()
    mock_fetch_data.return_value["close"].iloc[-1] = 105
    mock_check_buy_signal.return_value = True

    run_single_bot_trading_logic()

    mock_place_buy_order.assert_called_once_with("BTCUSDC")
    mock_save_trailing_stop_loss.assert_called_once_with(0.95)
    mock_save_previous_price.assert_called_once_with(105)


@patch("test_app.stefan.stefan.current_app")
@patch("test_app.stefan.stefan.fetch_data")
@patch("test_app.stefan.stefan.calculate_indicators")
@patch("test_app.stefan.stefan.check_buy_signal")
@patch("test_app.stefan.stefan.place_buy_order")
@patch("test_app.stefan.stefan.place_sell_order")
@patch("test_app.stefan.stefan.load_current_trade", return_value=mock_trade)
@patch("test_app.stefan.stefan.save_trailing_stop_loss")
@patch("test_app.stefan.stefan.save_previous_price")
@patch("test_app.stefan.stefan.logger")
def test_run_trading_logic_sell(
    mock_logger,
    mock_save_previous_price,
    mock_save_trailing_stop_loss,
    mock_load_current_trade,
    mock_place_buy_order,
    mock_place_sell_order,
    mock_check_buy_signal,
    mock_calculate_indicators,
    mock_fetch_data,
    mock_current_app,
    mock_settings,
    mock_trade,
):

    mock_current_app.app_context.return_value.__enter__.return_value = None
    mock_settings.return_value = mock_settings
    mock_fetch_data.return_value = MagicMock()
    mock_fetch_data.return_value["close"].iloc[-1] = 0.94
    mock_trade.trailing_stop_loss = 0.95
    mock_trade.previous_price = 100

    run_single_bot_trading_logic()

    mock_place_sell_order.assert_called_once_with("BTCUSDC")
    mock_save_previous_price.assert_called_once_with(0.94)


@patch("app.stefan.stefan.current_app")
@patch("app.stefan.stefan.logger")
@patch("app.stefan.stefan.send_admin_email", new_callable=AsyncMock)
def test_run_trading_logic_error_handling(
    mock_send_email, mock_logger, mock_current_app, test_app
):
    with test_app.app_context():
        mock_current_app.app_context.side_effect = Exception("Test error")

        run_single_bot_trading_logic()

        mock_logger.error.assert_called_once_with("Błąd w pętli handlowej: Test error")
        mock_send_email.assert_called_once_with("Błąd w pętli handlowej", "Test error")
