import pytest
from flask import Flask
from app.utils.app_utils import show_account_balance, get_ip_address

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['MAIL_SUPPRESS_SEND'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'secret'
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_get_ip_address(client):
    with client:
        response = client.get('/')
        ip_address = get_ip_address(client.get('/').request)
        assert ip_address == '127.0.0.1'

def test_show_account_balance():
    account_status = {
        'balances': [
            {'asset': 'BTC', 'free': '0.5', 'locked': '0.1'},
            {'asset': 'USDC', 'free': '100.0', 'locked': '0.0'},
            {'asset': 'ETH', 'free': '2.0', 'locked': '0.0'},
        ]
    }
    
    balances = show_account_balance(account_status)
    assert len(balances) == 2
    assert balances[0]['asset'] == 'BTC'
    assert balances[1]['asset'] == 'USDC'
    assert balances[0]['free'] == 0.5
    assert balances[1]['free'] == 100.0