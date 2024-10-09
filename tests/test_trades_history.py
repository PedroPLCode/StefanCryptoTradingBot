import pytest
from app import create_app, db
from app.models import TradesHistory

@pytest.fixture
def test_app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        yield app

@pytest.fixture
def test_client(test_app):
    return test_app.test_client()

@pytest.fixture
def test_settings(test_app):
    with test_app.app_context():
        trade = TradesHistory(type='buy', amount=0.5, price=30000.0)
        db.session.add(trade)
        db.session.commit()
        return trade

def test_trades_history_creation(test_app):
    with test_app.app_context():
        trade = TradesHistory(type='sell', amount=1.0, price=31000.0)
        db.session.add(trade)
        db.session.commit()
        
        assert trade.id is not None
        assert trade.type == 'sell'
        assert trade.amount == 1.0
        assert trade.price == 31000.0
        assert trade.timestamp is not None

def test_trades_history_default_values(test_app):
    with test_app.app_context():
        trade = TradesHistory()
        db.session.add(trade)
        db.session.commit()
        
        assert trade.type == 'undefined'
        assert trade.amount == 0
        assert trade.price == 0
        assert trade.timestamp is not None
