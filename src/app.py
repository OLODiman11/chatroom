import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)
app.permanent_session_lifetime = datetime.timedelta(seconds=5)

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' in session:
        return redirect(url_for('room'))
    if request.method == 'POST':
        session.permanent = True
        session['username'] = request.form['username']
        socketio.emit('user_joined', session['username'])
        return redirect(url_for('room'))
    return render_template('index.html')


@app.route('/room')
def room():
    if 'username' not in session:
        return redirect(url_for('index'))
    return render_template('room.html', username=session['username'])


@socketio.on('message_sent')
def on_message_sent(message):
    emit('recieve_message', (session['username'], message), broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
