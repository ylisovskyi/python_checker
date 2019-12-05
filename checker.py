import ast
import json
import os
import subprocess


def wrap_to_json(func):

    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        if isinstance(res, tuple):
            res = dict(res)

        return json.dumps(res)

    return wrapper


class CodeValidator(object):

    def __init__(self, compile_mode='exec'):
        self.compile_mode = compile_mode

    @wrap_to_json
    def test_code(self, code, input_data, expected_output_data):
        results = []
        for input_sample, expected_output in zip(
                input_data, expected_output_data
        ):
            if isinstance(input_sample, str):
                input_sample = '"""{}"""'.format(input_sample)
            tmp_code = code + '\n\nprint(main({}))'.format(input_sample)
            validated = self.validate(tmp_code, type(expected_output))
            validated['input'] = input_sample
            validated['expected'] = expected_output
            if validated['valid']:
                actual_output = validated['result']
                validated['correct'] = (actual_output == expected_output)
            results.append(validated)

        return results

    def compile_code(self, code, expected_type=None):
        filename = 'file.py'
        result = None
        with open(filename, 'w') as f:
            f.write(code)

        sub = subprocess.Popen(
            ['python', filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        res_output, res_error = sub.communicate()
        res_output = res_output.decode('utf8')
        res_error = res_error.decode('utf8')
        if res_output:
            if expected_type == str:
                result = res_output.replace('\r', '').rstrip('\n')
            else:
                result = ast.literal_eval(res_output)
        os.remove('file.py')
        return result, res_error

    def validate(self, source, expected_type=None):
        out, err = self.compile_code(source, expected_type)
        return {
            'valid': False if err else True,
            'correct': False,
            'result': out,
            'input': None,
            'expected': None,
            'errors': [err]
        }


if __name__ == '__main__':
    validator = CodeValidator()
    code = """
def main(l):
    return l[::-1]s
"""
    test_results = json.loads(
        validator.test_code(
            code=code,
            input_data=[
                [1, 2, 3],
                'hello',
                'hi\nhi',
                [1, 2, 'hello']
            ],
            expected_output_data=[
                [3, 2, 1],
                'olleh',
                'ih\nih',
                ['hello', 3, 2]
            ]
        )
    )
    for res in test_results:
        print(res)
        for error in res['errors']:
            print(error)
