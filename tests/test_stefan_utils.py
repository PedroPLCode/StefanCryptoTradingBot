import pytest
from unittest.mock import patch, MagicMock
import talib
from datetime import datetime, timedelta
import pandas as pd
from app.utils.stefan_utils import (
    calculate_indicators,
    check_buy_signal,
    check_sell_signal,
    save_trade,
    delete_trade,
    load_current_trade,
    update_trailing_stop_loss,
    save_trailing_stop_loss,
    save_previous_price,
    save_trade_to_history,
    clear_old_trade_history
)

@pytest.fixture
def mock_db_session():
    with patch('app.utils.stefan_utils.db.session') as mock_session:
        yield mock_session

@pytest.fixture
def mock_current_trade():
    with patch('app.utils.stefan_utils.CurrentTrade') as MockCurrentTrade:
        yield MockCurrentTrade

@pytest.fixture
def mock_trades_history():
    with patch('app.utils.stefan_utils.TradesHistory') as MockTradesHistory:
        yield MockTradesHistory

@pytest.fixture
def mock_talib():
    with patch('app.utils.stefan_utils.talib') as MockTA:
        yield MockTA

def test_calculate_indicators(mock_talib):
    # Create a sample DataFrame
    df = pd.DataFrame({
        'close': [100, 105, 110, 115, 120],
        'high': [102, 107, 112, 117, 122],
        'low': [98, 103, 108, 113, 118],
        'volume': [10, 15, 20, 25, 30]
    })
    
    # Mock TA-Lib functions
    mock_talib.RSI.return_value = [30, 35, 40, 45, 50]
    mock_talib.MACD.return_value = ([0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0])
    mock_talib.BBANDS.return_value = ([0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0])
    mock_talib.ATR.return_value = [1, 1, 1, 1, 1]
    mock_talib.CCI.return_value = [0, 0, 0, 0, 0]
    mock_talib.STOCH.return_value = ([0, 0, 0, 0, 0], [0, 0, 0, 0, 0])

    calculate_indicators(df)

    assert 'rsi' in df.columns
    assert 'macd' in df.columns
    assert 'upper_band' in df.columns
    assert 'lower_band' in df.columns
    assert 'atr' in df.columns
    assert 'cci' in df.columns
    assert 'slowk' in df.columns
    assert 'slowd' in df.columns

def test_check_buy_signal(mock_talib):
    df = pd.DataFrame({
        'close': [100, 105, 110],
        'high': [102, 107, 112],
        'low': [98, 103, 108],
        'volume': [10, 15, 20]
    })

    mock_talib.MFI.return_value = [15, 10, 5]
    mock_talib.RSI.return_value = [20, 22, 24]
    mock_talib.MACD.return_value = ([0, 0, 0], [0, 0, 0], [0, 0, 0])
    mock_talib.CCI.return_value = [-150, -120, -110]

    assert check_buy_signal(df) is True

def test_check_sell_signal(mock_talib):
    df = pd.DataFrame({
        'close': [100, 105, 110],
        'high': [102, 107, 112],
        'low': [98, 103, 108],
        'volume': [10, 15, 20]
    })

    mock_talib.MFI.return_value = [90, 85, 82]
    mock_talib.RSI.return_value = [80, 75, 78]
    mock_talib.MACD.return_value = ([0, 0, 0], [0, 0, 0], [0, 0, 0])
    mock_talib.CCI.return_value = [150, 120, 110]

    assert check_sell_signal(df) is True

def test_save_trade(mock_db_session, mock_current_trade):
    mock_current_trade.return_value = MagicMock()
    
    save_trade('buy', 1, 100)

    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()

def test_delete_trade(mock_db_session):
    delete_trade()

    mock_db_session.query.return_value.delete.assert_called_once()
    mock_db_session.commit.assert_called_once()

def test_load_current_trade(mock_current_trade):
    mock_current_trade.query.first.return_value = MagicMock()

    current_trade = load_current_trade()
    
    assert current_trade is not None
    mock_current_trade.query.first.assert_called_once()

def test_update_trailing_stop_loss():
    trailing_stop_price = 90
    current_price = 100
    atr = 2

    result = update_trailing_stop_loss(current_price, trailing_stop_price, atr)
    
    assert result == 99  # since 100 * (1 - (0.5 * 2 / 100)) = 99

def test_save_trailing_stop_loss(mock_db_session, mock_current_trade):
    mock_current_trade.query.first.return_value = MagicMock()

    save_trailing_stop_loss(95)

    mock_current_trade.query.first.return_value.trailing_stop_loss = 95
    mock_db_session.commit.assert_called_once()

def test_save_previous_price(mock_db_session, mock_current_trade):
    mock_current_trade.query.first.return_value = MagicMock()

    save_previous_price(90)

    mock_current_trade.query.first.return_value.previous_price = 90
    mock_db_session.commit.assert_called_once()

def test_save_trade_to_history(mock_db_session, mock_trades_history):
    mock_trades_history.return_value = MagicMock()
    
    save_trade_to_history('sell', 1, 100)

    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()

def test_clear_old_trade_history(mock_db_session, mock_trades_history):
    mock_db_session.query.return_value.filter.return_value.delete = MagicMock()
    one_month_ago = datetime.now() - timedelta(days=30)

    clear_old_trade_history()

    mock_db_session.query.return_value.filter.assert_called_once()
    mock_db_session.commit.assert_called_once()
