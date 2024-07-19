import os
import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

db = SQLAlchemy()
socketio = SocketIO()


def try_create_folder(path):
    try:
        os.makedirs(path)
        return True
    except OSError:
        return False


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_pyfile('config.py', silent=True)
    if config:
        app.config.from_mapping(config)

    try_create_folder(app.instance_path)

    @app.route('/test')
    def test():
        return 'Success!'

    db.init_app(app)
    socketio.init_app(app)

    with app.app_context():
        from . import models
        db.create_all()

        from . import auth
        app.register_blueprint(auth.bp)

        from . import chat
        app.register_blueprint(chat.bp)

    return app
