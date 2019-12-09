import flask
import json
from flask import Blueprint, render_template, request
from flask_login import login_required
from .models import Task
from papp.checker import CodeValidator
from papp.models import TestData


tasks = Blueprint('tasks', __name__)


@tasks.route('/tasks/<task_id>', methods=["GET", "POST"])
@login_required
def task_by_id(task_id):
    task = Task.query.filter_by(task_id=task_id).first()
    if not task:
        return 404, f'task with id {task_id} is not found.'

    user_code = r"def main(l):\n\t..."

    if request.method == "POST":
        user_code = request.form.get('user-code')
        task = Task.query.filter_by(task_id=task_id).first()
        validator_builder = ValidatorBuilder().create_validator('python')

        test_data = (TestData.query.filter(TestData.task_id == task_id)
                     .with_entities(TestData.input_data,
                                    TestData.output_data)
                     .all()
                     )

        test_data = [(eval(input_data), eval(output_data)) for (input_data, output_data) in test_data]
        input_data, output_data = zip(*test_data)

        test_results = json.loads(
            validator.test_code(
                code=user_code,
                input_data=input_data,
                expected_output_data=output_data
            )
        )
        return render_template('code.html', task=task, test_results=test_results, editor_code=user_code)

    return render_template('code.html', task=task, editor_code=user_code)

