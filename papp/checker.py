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


CODE_VALIDATORS = {
    'python': PythonCodeValidator,
    'java': JavaCodeValidator
}


class ValidatorBuilder(object):
    
    @staticmethod
    def create_validator(language='python', *args, **kwargs):
        return CODE_VALIDATORS[language](*args, **kwargs)


class CodeValidator(object):
    
    interpreter = None
    file_extension = ''
    additional_args = []
    function_usage = ''

    def __init__(self, compile_mode='exec'):
        self.compile_mode = compile_mode
        
    def additional_compile():
        pass

    @wrap_to_json
    def test_code(self, code, input_data, expected_output_data):
        results = []
        for input_sample, expected_output in zip(
                input_data, expected_output_data
        ):
            if isinstance(input_sample, str):
                input_sample = '"""{}"""'.format(input_sample)
            tmp_code = code + self.function_usage.format(input_sample)
            validated = self.validate(tmp_code, type(expected_output))
            validated['input'] = input_sample
            validated['expected'] = expected_output
            if validated['valid']:
                actual_output = validated['result']
                validated['correct'] = (actual_output == expected_output)
            results.append(validated)

        return results

    def compile_code(self, code, expected_type=None):
        self.additional_compile()
        filename = 'file' + self.file_extension
        result = None
        with open(filename, 'w') as f:
            f.write(code)

        sub = subprocess.Popen(
            [self.interpreter, filename] + self.additional_args,
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
        os.remove(filename)
        return result, res_error

    def validate(self, source, expected_type=None):
        out, err = self.compile_code(source, expected_type)
        return {
            'valid': False if err else True,
            'correct': False,
            'result': out,
            'input': None,
            'expected': None,
            'error': err
        }
    
    
class PythonCodeValidator(object):
    
    interpreter = 'python'
    file_extension = '.py'
    additional_args = []
    function_usage = '\n\nprint(main({}))'
    
    
class JavaCodeValidator(object):
    
    interpreter = 'java'
    file_extension = ''
    additional_args = []
    function_usage = '\n\nSystem.out.println(main({}))'

    def additional_compile():
        filename = 'file.java'
        with open(filename, 'w') as f:
            f.write(code)

        sub = subprocess.Popen(
            ['javac', filename] + self.additional_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
