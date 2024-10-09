import pytest
from unittest.mock import MagicMock
from app.models import Settings
from app import create_app
from app.stefan.stefan import run_trading_logic
from app.utils.stefan_utils import load_current_trade

@pytest.fixture
def test_app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        yield app
        
@pytest.fixture
def mock_db(mocker, test_app):
    with test_app.app_context():
        mock_settings = mocker.patch('app.models.Settings.query.first')
        mock_current_trade = mocker.patch('app.utils.stefan_utils.load_current_trade')
        mock_fetch_data = mocker.patch('app.utils.api_utils.fetch_data')
        mock_calculate_indicators = mocker.patch('app.utils.stefan_utils.calculate_indicators')
        mock_check_signals = mocker.patch('app.utils.stefan_utils.check_signals')
        mock_place_order = mocker.patch('app.utils.api_utils.place_order')
        mock_save_trailing_stop_loss = mocker.patch('app.utils.stefan_utils.save_trailing_stop_loss')
        mock_update_trailing_stop_loss = mocker.patch('app.utils.stefan_utils.update_trailing_stop_loss')
        mock_logger = mocker.patch('app.logger')

        return {
            'mock_settings': mock_settings,
            'mock_current_trade': mock_current_trade,
            'mock_fetch_data': mock_fetch_data,
            'mock_calculate_indicators': mock_calculate_indicators,
            'mock_check_signals': mock_check_signals,
            'mock_place_order': mock_place_order,
            'mock_save_trailing_stop_loss': mock_save_trailing_stop_loss,
            'mock_update_trailing_stop_loss': mock_update_trailing_stop_loss,
            'mock_logger': mock_logger
        }

def test_run_trading_logic_buy(mock_db):
    with test_app.app_context():
        mock_db['mock_settings'].return_value = Settings(bot_running=True, symbol='BTCUSDC', trailing_stop_pct=0.05, interval='1m', lookback_days=1)
        mock_db['mock_current_trade'].return_value = None  # Brak aktywnego handlu
        mock_db['mock_fetch_data'].return_value = MagicMock(close=[100, 101, 102])  # Przykładowe dane
        mock_db['mock_calculate_indicators'].return_value = None
        mock_db['mock_check_signals'].return_value = 'buy'  # Sygnał kupna

    run_trading_logic()

    # Sprawdzenie, czy odpowiednie funkcje zostały wywołane
    mock_db['mock_place_order'].assert_called_once_with('BTCUSDC', 'buy')
    mock_db['mock_save_trailing_stop_loss'].assert_called_once()  # Sprawdź, czy trailing stop loss został zapisany

def test_run_trading_logic_sell(mock_db):
    # Ustawienia mocka dla sprzedaży
    mock_db['mock_settings'].return_value = Settings(bot_running=True, symbol='BTCUSDC', trailing_stop_pct=0.05, interval='1m', lookback_days=1)
    mock_db['mock_current_trade'].return_value = MagicMock(trailing_stop_loss=95)  # Aktywny handel
    mock_db['mock_fetch_data'].return_value = MagicMock(close=[100, 101, 102])  # Przykładowe dane
    mock_db['mock_calculate_indicators'].return_value = None
    mock_db['mock_check_signals'].return_value = 'sell'  # Sygnał sprzedaży

    run_trading_logic()

    # Sprawdzenie, czy odpowiednie funkcje zostały wywołane
    mock_db['mock_place_order'].assert_called_once_with('BTCUSDC', 'sell')
    mock_db['mock_save_trailing_stop_loss'].assert_called_once_with(None)  # Trailing stop loss powinien być usunięty

def test_run_trading_logic_trailing_stop(mock_db):
    # Ustawienia mocka dla aktywnego handlu
    mock_db['mock_settings'].return_value = Settings(bot_running=True, symbol='BTCUSDC', trailing_stop_pct=0.05, interval='1m', lookback_days=1)
    mock_db['mock_current_trade'].return_value = MagicMock(trailing_stop_loss=95)  # Aktywny handel
    mock_db['mock_fetch_data'].return_value = MagicMock(close=[100, 90])  # Przykładowe dane
    mock_db['mock_calculate_indicators'].return_value = None
    mock_db['mock_check_signals'].return_value = None  # Brak sygnałów

    run_trading_logic()

    # Sprawdzenie, czy trailing stop loss został zaktualizowany
    mock_db['mock_update_trailing_stop_loss'].assert_called_once()
    mock_db['mock_save_trailing_stop_loss'].assert_called_once()

def test_run_trading_logic_exception_handling(mock_db):
    # Ustawienia mocka dla błędu
    mock_db['mock_settings'].return_value = Settings(bot_running=True, symbol='BTCUSDC', trailing_stop_pct=0.05, interval='1m', lookback_days=1)
    mock_db['mock_current_trade'].return_value = None
    mock_db['mock_fetch_data.side_effect'] = Exception("Fetch data error")  # Wywołanie wyjątku

    run_trading_logic()

    # Sprawdzenie, czy logger zarejestrował błąd
    mock_db['mock_logger'].error.assert_called_once_with('Błąd w pętli handlowej: Fetch data error')
