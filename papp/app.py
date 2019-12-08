from flask import render_template, request
from flask_login import login_required, current_user
from papp import create_app
from papp.models import Task, TaskList, TestData
from papp.checker import CodeValidator
import json


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


@app.route('/verifycode/<task_id>', methods=["POST"])
@login_required
def verify_code(task_id):
    user_code = request.form.get('user-code')
    validator = CodeValidator()

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

    print(test_results)

    return render_template('code.html', results=test_results)

@app.route('/code')
@login_required
def code_page():
    return render_template('code.html')


if __name__ == '__main__':
    # app.run(debug=True, ssl_context="adhoc")
    app.run(debug=True)