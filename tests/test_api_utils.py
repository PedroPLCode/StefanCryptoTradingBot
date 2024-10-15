import pytest
from unittest.mock import patch
from app.utils.api_utils import (
    fetch_data, 
    get_account_balance,
    fetch_current_price, 
    place_buy_order,
    place_sell_order
)

@pytest.fixture
def mock_client():
    with patch('app.utils.api_utils.client') as mock_client:
        yield mock_client

def test_fetch_data(mock_client):
    symbol = 'BTCUSDT'
    mock_client.get_historical_klines.return_value = [
        [1620000000000, '50000', '50500', '49000', '50000', '100', '1620003600000', '5000000', '100', '50', '2500000', '0']
    ]
    df = fetch_data(symbol)
    assert not df.empty
    assert df.shape[0] == 1
    assert df['close'].iloc[0] == 50000.0

def test_get_account_balance(mock_client):
    mock_client.futures_account.return_value = {
        'assets': [
            {'asset': 'USDC', 'balance': '1000'},
            {'asset': 'BTC', 'balance': '0.5'}
        ]
    }
    balance = get_account_balance()
    assert balance['USDC'] == 1000.0
    assert balance['BTC'] == 0.5

def test_fetch_current_price(mock_client):
    mock_client.get_symbol_ticker.return_value = {'price': '50000'}
    price = fetch_current_price('BTCUSDT')
    assert price == 50000.0

def test_place_order(mock_client):
    mock_client.futures_account.return_value = {
        'assets': [
            {'asset': 'USDC', 'balance': '1000'},
            {'asset': 'BTC', 'balance': '0'}
        ]
    }
    mock_client.get_symbol_ticker.return_value = {'price': '50000'}
    place_buy_order('BTCUSDT', 'buy')
    mock_client.order_market_buy.assert_called_once()
    
    mock_client.futures_account.return_value = {
        'assets': [
            {'asset': 'USDC', 'balance': '0'},
            {'asset': 'BTC', 'balance': '0.5'}
        ]
    }
    place_sell_order('BTCUSDT', 'sell')
    mock_client.order_market_sell.assert_called_once()

if __name__ == '__main__':
    pytest.main()