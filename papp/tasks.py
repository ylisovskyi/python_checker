import flask
import json
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from .models import Task, Results
from . import db
from papp.checker import PythonValidatorFactory
from papp.models import TestData


tasks = Blueprint('tasks', __name__)


@tasks.route('/tasks/<task_id>', methods=["GET", "POST"])
@login_required
def task_by_id(task_id):
    task = Task.query.filter_by(task_id=task_id).first()
    if not task:
        return 404, f'task with id {task_id} is not found.'

    user_code = r"""def main(l):\r\n\t..."""
    test_data = (TestData.query.filter(TestData.task_id == task_id)
                 .with_entities(TestData.input_data,
                                TestData.output_data)
                 .all()
                 )

    test_data = [(eval(input_data), eval(output_data)) for
                 (input_data, output_data) in test_data]
    input_data, output_data = zip(*test_data)

    if request.method == "POST":
        user_code = request.form.get('user-code')
        validator_builder = PythonValidatorFactory().create_validator('python')

        test_results = json.loads(
            validator_builder.test_code(
                code=user_code,
                input_data=input_data,
                expected_output_data=output_data
            )
        )
        score = 0
        for test_result in test_results:
            if test_result['correct']:
                score += 1

        curr_user = current_user.username
        old_result = Results.query.filter_by(
            username=curr_user,
            task_id=task_id
        ).first()
        if old_result:
            if old_result.score < score:
                old_result.score = score
        else:
            result = Results(
                username=curr_user,
                task_id=task_id,
                score=score
            )
            db.session.add(result)
        db.session.commit()

        if score == 5:
            return redirect(url_for('tasks_page'))

        return render_template('code.html', task=task, test_results=test_results, editor_code=user_code.replace('\n', '\r\n'), test_data=None)

    return render_template('code.html', task=task, editor_code=user_code, test_data=zip(input_data, output_data), test_results=None)

