import pytest
from app import create_app, db
from app.models import Settings

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
        settings = Settings()
        db.session.add(settings)
        db.session.commit()
        return settings

def test_default_settings(test_settings):
    test_settings = Settings()
    db.session.add(test_settings)
    db.session.commit()
        
    assert test_settings.symbol == "BTCUSDT"
    assert test_settings.stop_loss_pct == 0.02
    assert test_settings.trailing_stop_pct == 0.01
    assert test_settings.take_profit_pct == 0.03
    assert test_settings.lookback_days == "30 days"
    assert test_settings.bot_running is False

def test_update_settings(test_settings):
    test_settings.symbol = "ETHUSDT"
    test_settings.stop_loss_pct = 0.05
    test_settings.bot_running = True
    db.session.commit()

    assert test_settings.symbol == "ETHUSDT"
    assert test_settings.stop_loss_pct == 0.05
    assert test_settings.bot_running is True

def test_delete_settings(test_settings):
    db.session.delete(test_settings)
    db.session.commit()

    assert Settings.query.filter_by(id=test_settings.id).first() is None