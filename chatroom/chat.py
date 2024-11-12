from flask import Blueprint, redirect, render_template, session, url_for
from .models import Message
from . import db, socketio


bp = Blueprint('chat', __name__)


@bp.route('/room')
def room():
    if 'username' not in session:
        return redirect(url_for('auth.index'))
    messages = db.session.execute(db.select(Message)).scalars()
    messages = [{'sender': m.sender, 'text': m.text} for m in messages]
    return render_template('room.html', username=session['username'], messages=messages)


@socketio.on('send_message')
def on_send_message(text):
    send_user_message(session['username'], text)


def send_system_message(text):
    add_to_db(Message(sender='System', text=text))
    socketio.emit('system_message', text)


def send_user_message(sender, text):
    add_to_db(Message(sender=sender, text=text))
    socketio.emit('user_message', (sender, text))


def add_to_db(obj: object):
    db.session.add(obj)
    db.session.commit()
