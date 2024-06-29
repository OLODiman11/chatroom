import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chatroom.db'
socketio = SocketIO(app)
app.permanent_session_lifetime = datetime.timedelta(minutes=30)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String, nullable=False)
    text = db.Column(db.String)


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' in session:
        return redirect(url_for('room'))
    if request.method == 'POST':
        session.permanent = True
        session['username'] = request.form['username']
        add_message('System', f'{session["username"]} has joined the room.')
        socketio.emit('user_joined', session['username'])
        return redirect(url_for('room'))
    return render_template('index.html')


@app.route('/room')
def room():
    if 'username' not in session:
        return redirect(url_for('index'))
    messages = db.session.execute(db.select(Message)).scalars()
    return render_template('room.html', username=session['username'], messages=messages)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@socketio.on('message_sent')
def on_message_sent(message):
    add_message(session['username'], message)
    emit('recieve_message', (session['username'], message), broadcast=True)


@socketio.on('leave_room')
def on_leave_room():
    add_message('System', f'{session["username"]} has left the room.')
    emit('user_left', (session['username']), broadcast=True)


def add_message(sender, text):
    db.session.add(Message(sender=sender, text=text))
    db.session.commit()


if __name__ == '__main__':
    db.init_app(app)
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)
