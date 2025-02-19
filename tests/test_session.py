import pytest
from app import db
from app.models import User
from bs4 import BeautifulSoup


@pytest.fixture
def test_app():
    from app import app

    app.config["WTF_CSRF_ENABLED"] = True
    app.secret_key = "supersecretkey"
    app.testing = True
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    with app.app_context():
        yield app


@pytest.fixture
def test_client(test_app):
    return test_app.test_client()


@pytest.fixture
def test_session_user(test_app):
    with test_app.app_context():
        test_user = User.query.filter_by(login="test_regular_user").first()
        return test_user


def test_register(test_client):
    response = test_client.get("/register")
    soup = BeautifulSoup(response.data, "html.parser")
    csrf_token = soup.find("input", {"name": "csrf_token"})["value"]
    response = test_client.post(
        "/register",
        data={
            "login": "newuser_from_test",
            "email": "newuser@example.com",
            "name": "NewUserFromTest-DeleteIt",
            "password": "ValidPass123!",
            "confirm_password": "ValidPass123!",
            "csrf_token": csrf_token,
        },
        follow_redirects=True,
    )
    print(response.data)
    assert response.status_code == 200
    assert b"Account created successfully." in response.data
    assert User.query.filter_by(login="newuser").first() is not None


def test_login_and_logout(test_client, test_session_user):
    test_session_user.set_password("ValidPass123!")
    db.session.commit()
    response = test_client.get("/login")
    soup = BeautifulSoup(response.data, "html.parser")
    csrf_token = soup.find("input", {"name": "csrf_token"})["value"]
    response = test_client.post(
        "/login",
        data={
            "login": "test_regular_user",
            "password": "ValidPass123!",
            "csrf_token": csrf_token,
        },
        follow_redirects=True,
    )
    print(response.data)
    assert response.status_code == 200
    assert b"Logged in successfully." in response.data

    response = test_client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"logged out successfully." in response.data


def test_login_invalid(test_client):
    response = test_client.get("/login")
    soup = BeautifulSoup(response.data, "html.parser")
    csrf_token = soup.find("input", {"name": "csrf_token"})["value"]
    response = test_client.post(
        "/login",
        data={
            "login": "wronguser",
            "password": "wrongpassword",
            "csrf_token": csrf_token,
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Error: Login or Password Incorrect." in response.data
