import pytest
from app.models import User


@pytest.fixture
def test_app():
    from app import app

    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    with app.app_context():
        yield app


@pytest.fixture
def test_client(test_app):
    return test_app.test_client()


@pytest.fixture
def create_admin_user(test_app):
    with test_app.app_context():
        admin_user = User.query.filter_by(login="test_admin_user").first()
        return admin_user


@pytest.fixture
def create_regular_user(test_app):
    with test_app.app_context():
        regular_user = User.query.filter_by(login="test_regular_user").first()
        return regular_user


def test_user_panel_view(test_client, create_regular_user, mocker):
    mocker.patch("flask_login.utils._get_user", return_value=create_regular_user)
    response = test_client.get("/", follow_redirects=True)
    print(response.data)
    assert response.status_code == 200
    assert b"<h5>User Info</h5>" in response.data


def test_user_panel_view_not_authenticated(test_client):
    response = test_client.get("/", follow_redirects=True)
    print(response.data)
    assert response.status_code == 200
    assert b"Please log in to access the app." in response.data


def test_control_panel_view(test_client, create_regular_user, mocker):
    mocker.patch("flask_login.utils._get_user", return_value=create_regular_user)
    response = test_client.get("/control", follow_redirects=True)
    assert response.status_code == 200
    assert b"<title>Trading Bot Control Panel</title>" in response.data


def test_control_panel_view_not_authenticated(test_client):
    response = test_client.get("/control", follow_redirects=True)
    assert response.status_code == 200
    assert b"Please log in to access the control panel." in response.data


def test_control_panel_view_no_access(test_client, create_admin_user, mocker):
    mocker.patch("flask_login.utils._get_user", return_value=create_admin_user)
    response = test_client.get("/control", follow_redirects=True)
    response = test_client.get("/control", follow_redirects=True)
    assert response.status_code == 200
    assert b"not allowed to access the Control Panel." in response.data


def test_admin_panel_view(test_client, create_admin_user, mocker):
    mocker.patch("flask_login.utils._get_user", return_value=create_admin_user)
    response = test_client.get("/admin/", follow_redirects=True)
    assert response.status_code == 200
    assert b"Admin Panel" in response.data


def test_admin_panel_view_not_authenticated(test_client):
    response = test_client.get("/admin/", follow_redirects=True)
    assert response.status_code == 200
    assert b"Please log in to access this page." in response.data


def test_admin_panel_view_no_access(test_client, create_regular_user, mocker):
    mocker.patch("flask_login.utils._get_user", return_value=create_regular_user)
    response = test_client.get("/admin/", follow_redirects=True)
    assert response.status_code == 200
    assert b"Please log in to access this page." in response.data


def test_start_bot(test_client, create_regular_user, mocker):
    mocker.patch("flask_login.utils._get_user", return_value=create_regular_user)
    response = test_client.get("/start", follow_redirects=True)
    assert response.status_code == 200
    assert b"Bot started." in response.data


def test_start_bot_without_permission(test_client, create_admin_user, mocker):
    mocker.patch("flask_login.utils._get_user", return_value=create_admin_user)
    response = test_client.get("/start", follow_redirects=True)
    assert response.status_code == 200
    assert (
        b"Error. User test_admin_user is not allowed to control Bot." in response.data
    )


def test_stop_bot(test_client, create_regular_user, mocker):
    mocker.patch("flask_login.utils._get_user", return_value=create_regular_user)
    response = test_client.get("/stop", follow_redirects=True)
    assert response.status_code == 200
    assert b"Bot stopped." in response.data


def test_stop_bot_without_permission(test_client, create_admin_user, mocker):
    mocker.patch("flask_login.utils._get_user", return_value=create_admin_user)
    response = test_client.get("/stop", follow_redirects=True)
    assert response.status_code == 200
    assert (
        b"Error. User test_admin_user is not allowed to control Bot." in response.data
    )


def test_refresh_bot(test_client, create_regular_user, mocker):
    mocker.patch("flask_login.utils._get_user", return_value=create_regular_user)
    response = test_client.get("/refresh", follow_redirects=True)
    assert response.status_code == 200
    assert b"Binance API refreshed." in response.data


def test_refresh_without_permission(test_client, create_admin_user, mocker):
    mocker.patch("flask_login.utils._get_user", return_value=create_admin_user)
    response = test_client.get("/refresh", follow_redirects=True)
    assert response.status_code == 200
    assert (
        b"Error. User test_admin_user is not allowed to control Bot." in response.data
    )


def test_report(test_client, create_regular_user, mocker):
    mocker.patch("flask_login.utils._get_user", return_value=create_regular_user)
    response = test_client.get("/report", follow_redirects=True)
    assert response.status_code == 200
    assert b"sent successfully." in response.data


def test_report_without_permission(test_client, create_admin_user, mocker):
    mocker.patch("flask_login.utils._get_user", return_value=create_admin_user)
    response = test_client.get("/report", follow_redirects=True)
    assert response.status_code == 200
    assert (
        b"Error. User test_admin_user is not allowed receiving email raports."
        in response.data
    )
