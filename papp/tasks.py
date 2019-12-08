import flask
from flask import Blueprint, render_template
from flask_login import login_required
from .models import Task


tasks = Blueprint('tasks', __name__)


@tasks.route('/tasks/<task_id>')
@login_required
def task_by_id(task_id):
    task = Task.query.filter_by(task_id=task_id).first()

    if not task:
        return 404, f'task with id {task_id} is not found.'

    return render_template('code.html', task=task)