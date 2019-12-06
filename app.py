from . import create_app
from flask import render_template
from flask_login import login_required, current_user


app = create_app()


@app.route('/')
@login_required
def index_page():
    return render_template('index.html')


@app.route('/login')
def login_page():
    return render_template('login.html')


@app.route('/tasks')
@login_required
def tasks_page():
    return render_template('tasks.html')


@app.route('/code')
@login_required
def code_page():
    return render_template('code.html')


if __name__ == '__main__':
    app.run()
