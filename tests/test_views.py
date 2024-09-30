from flask import current_app
from flask import url_for
from bs4 import BeautifulSoup

def login(client, login, password):
    response = client.get(url_for('main.login'))
    soup = BeautifulSoup(response.data, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']

    return client.post(url_for('main.login'), data=dict(
        login=login,
        password=password,
        csrf_token=csrf_token
    ), follow_redirects=True)

def logout(client):
    return client.get(url_for('main.logout'), follow_redirects=True)

def test_user_panel_view_without_login(test_client):
    response = test_client.get(url_for('main.user_panel_view'), follow_redirects=True)
    assert response.status_code == 200
    assert b'Please log in to access app.' in response.data

def test_user_panel_view_with_login(test_client, mock_db):
    login(test_client, "testlogin", "TestPassword123#")
    response = test_client.get(url_for('main.user_panel_view'))
    assert response.status_code == 200
    assert b'testname' in response.data

def test_control_panel_view_without_login(test_client):
    response = test_client.get(url_for('main.control_panel_view'), follow_redirects=True)
    assert response.status_code == 200
    assert b'Please log in to access the control panel.' in response.data

def test_control_panel_view_with_login(test_client, mock_db):
    login(test_client, "testlogin", "TestPassword123#")
    response = test_client.get(url_for('main.control_panel_view'))
    assert response.status_code == 200
    assert b'Bot Control' in response.data

def test_control_panel_view_no_access(test_client, mock_db):
    mock_db.control_panel_access = False
    login(test_client, "testlogin", "TestPassword123#")
    response = test_client.get(url_for('main.control_panel_view'), follow_redirects=True)
    assert response.status_code == 200
    assert b'is not allowed to access the Control Panel.' in response.data

def test_admin_panel_view_without_login(test_client):
    response = test_client.get(url_for('main.admin_panel_view'), follow_redirects=True)
    assert response.status_code == 200
    assert b'Please log in to access the admin panel.' in response.data

def test_admin_panel_view_with_login(test_client, mock_db):
    login(test_client, "testlogin", "TestPassword123#")
    response = test_client.get(url_for('main.admin_panel_view'))
    assert response.status_code == 200
    assert b'Admin Panel' in response.data

def test_admin_panel_view_no_access(test_client, mock_db):
    mock_db.admin_panel_access = False
    login(test_client, "testlogin", "TestPassword123#")
    response = test_client.get(url_for('main.admin_panel_view'), follow_redirects=True)
    assert response.status_code == 200
    assert b'is not allowed to access the Admin Panel.' in response.data