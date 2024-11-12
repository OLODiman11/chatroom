import pytest
from flask_socketio.test_client import SocketIOTestClient
from flask import Flask, session
from flask.testing import FlaskClient, FlaskCliRunner
from werkzeug.test import TestResponse
from chatroom import create_app, try_create_folder
import os


@pytest.fixture()
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db',
        'SECRET_KEY': 'test'
    })

    yield app


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture()
def runner(app: Flask) -> FlaskCliRunner:
    return app.test_cli_runner()


@pytest.fixture()
def joinned_client(client: FlaskClient) -> FlaskClient:
    client.post('/', data={
        'username': 'Test'
    }, follow_redirects=True)
    return client


@pytest.fixture()
def socketio_client(app: Flask, joinned_client: FlaskClient) -> SocketIOTestClient:
    from chatroom import socketio
    socketio_client = socketio.test_client(app, flask_test_client=joinned_client)
    socketio_client.connect()
    return socketio_client


def test_test(client: FlaskClient):
    response = client.get('/test')
    assert response.status_code == 200


def test_config():
    assert create_app().config['TESTING'] == False
    assert create_app({'TESTING': True}).config['TESTING'] == True


def test_auth(client: FlaskClient):
    with client:
        response = client.post('/', data={
            'username': 'Test'
        }, follow_redirects=True)
        assert_one_redirect(response, '/room')
        assert session['username'] == 'Test'


def test_logout(joinned_client: FlaskClient):
    response = joinned_client.get('/logout', follow_redirects=True)
    assert_one_redirect(response, '/')


def test_room_auth_redirect(client: FlaskClient):
    response = client.get('/room', follow_redirects=True)
    assert_one_redirect(response, '/')


def test_auth_room_redirect(joinned_client: FlaskClient):
    response = joinned_client.get('/', follow_redirects=True)
    assert_one_redirect(response, '/room')


def test_run_in_production_mode():
    os.environ.setdefault('FLASK_ENV', 'production')
    app1 = create_app({
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'
    })
    assert app1.instance_path == os.path.abspath('../data')


def test_on_send_message(socketio_client: SocketIOTestClient):
    socketio_client.emit('send_message', 'Some message')
    recieved = socketio_client.get_received()
    assert len(recieved) == 1
    assert recieved[0]['name'] == 'user_message'
    assert recieved[0]['args'][0] == 'Test'
    assert recieved[0]['args'][1] == 'Some message'


def test_try_create_folder():
    assert try_create_folder('test')
    os.rmdir('test')


def assert_one_redirect(response: TestResponse, to: str):
    assert response.status_code == 200
    assert len(response.history) == 1
    assert response.request.path == to
