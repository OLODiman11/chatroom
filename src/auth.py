from flask import Blueprint, redirect, render_template, request, session, url_for
from .chat import send_system_message

bp = Blueprint('auth', __name__)


@bp.route('/', methods=('GET', 'POST'))
def index():
    if 'username' in session:
        return redirect(url_for('chat.room'))
    if request.method == 'POST':
        session.permanent = True
        session['username'] = request.form['username']
        send_system_message(f'{session["username"]} has joined the room.')
        return redirect(url_for('chat.room'))
    return render_template('index.html')


@bp.route('/logout')
def logout():
    send_system_message(f'{session["username"]} has left the room.')
    session.clear()
    return redirect(url_for('auth.index'))
