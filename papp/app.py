import flask
from flask import render_template, request, redirect, url_for
from flask_login import login_required, current_user
from papp import create_app
from papp.models import Task, TaskList, TestData
from papp.checker import CodeValidator
import json
from . import db
from .models import Results


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
    difficulty = request.args.get('difficulty')

    if not difficulty:
        tasks = Task.query.all()
    else:
        tasks = (
            Task.query.join(TaskList)
            .filter(TaskList.difficulty == difficulty)
        )

    return render_template('tasks.html', tasks=tasks)


@app.route('/code')
@login_required
def code_page():
    return render_template('code.html')


@app.route('/stats')
@login_required
def stats_page():
    all_results = Results.query.filter_by(username=current_user.username).all()
    all_results_pretty = []
    fully_solved = 0
    score_sum = 0
    for result in all_results:
        if result.score == 5:
            fully_solved += 1
        score_sum += result.score
        all_results_pretty.append({
            'id': result.task_id,
            'score': result.score,
            'percents': (float(result) / 5.0) * 100,
            'fails': 5 - result.score
        })

    full_stats = {
        'solved': fully_solved,
        'average': (float(score_sum) / 5) * len(all_results) * 100,
        'fails': (len(all_results) * 5) - score_sum
    }
    return render_template('stats.html', results=all_results_pretty, full_stats=full_stats)


if __name__ == '__main__':
    # app.run(debug=True, ssl_context="adhoc")
    app.run(debug=True)