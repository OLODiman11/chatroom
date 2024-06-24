from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return redirect(url_for('room'))
    return render_template('index.html')


@app.route('/room')
def room():
    return render_template('room.html')


if __name__ == '__main__':
    app.run(debug=True)
