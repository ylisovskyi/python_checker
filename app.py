from flask import Flask
from flask import render_template

app = Flask(__name__)


@app.route('/')
def index_page():
    return render_template('index.html')


@app.route('/login')
def login_page():
    return render_template('login.html')


@app.route('/tasks')
def tasks_page():
    return render_template('tasks.html')


@app.route('/code')
def code_page():
    return render_template('code.html')


if __name__ == '__main__':
    app.run()
