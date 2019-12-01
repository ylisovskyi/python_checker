import json
import sys
import traceback


def validate(source):
    valid = True
    try:
        # ast.parse(source)
        compile(source=source, filename='<unknown>', mode='exec', flags=1024)
    except:
        traceback.print_exc()
        valid = False
    return json.dumps({
        'valid': valid,
        'errors': [sys.exc_info()]
    })