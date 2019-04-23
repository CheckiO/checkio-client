

import sys
import os
import shutil
import subprocess

eoc_folder = None
cio_folder = None


def fill_file(name, content):
    filename = os.path.join(eoc_folder, name)
    dirname = os.path.dirname(filename)
    os.makedirs(dirname, exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as fh:
        fh.write(content)

def copy_file(from_name, to_name):
    with open(os.path.join(cio_folder, from_name), 'r', encoding='utf-8') as fh:
        fill_file(to_name, fh.read())

def to_eoc(args):
    # import ipdb
    # ipdb.set_trace()
    global cio_folder
    global eoc_folder
    cio_folder = args.cio
    eoc_folder = args.eoc
    git_repo = args.git_push

    fill_file('.gitignore', '''.idea
__pycache__
*.pyc
    ''')

    fill_file('schema', 'docker-referee-python3;git@github.com:CheckiO/mission-template.git')

    copy_file('editor/animation/init.js', 'animation/init.js')
    copy_file('editor/initial_code/js_node', 'initial/js_node')
    copy_file('editor/initial_code/python_3', 'initial/python_3')
    copy_file('info/task_description.html', 'info/description.html')
    copy_file('translations/ru/info/task_description.html', 'translations/ru/info/description.html')
    copy_file('verification/tests.py', 'verification/src/tests.py')

    with open(os.path.join(cio_folder, 'verification/referee.py'), 'r') as fh:
        referee_code = fh.read()
        referee_code = '\n'.join(filter(lambda a: not a.startswith('from'), referee_code.splitlines()))

        class CheckiOReferee:
            def __init__(self, *args, **kwargs):
                self.kwargs = kwargs
            @property
            def on_ready(self):
                return self
        class Covers:
            unwrap_args = '''

def cover(func, in_data):
    return func(*in_data)

    '''

            unwrap_kwargs = '''

def cover(func, in_data):
    return func(**in_data)

    '''

            js_unwrap_args = '''

function cover(func, in_data) {
    return func.apply(this, in_data)
}

    '''

        class Api:
            @classmethod
            def add_listener(cls, tt, ref):
                cls.kwargs = ref.kwargs

            
        globs = {
            'ON_CONNECT': None,
            'TESTS': None,
            'CheckiOReferee': CheckiOReferee,
            'cover_codes': Covers,
            'api': Api

        }

        exec(referee_code, globs)

    new_cover_code = ''
    try:
        py_cover_code = Api.kwargs['cover_code']['python-3']
    except KeyError:
        pass
    else:
        new_cover_code += "ENV_NAME.PYTHON: '''" + py_cover_code + "'''"

    try:
        js_cover_code = Api.kwargs['cover_code']['js-node']
    except KeyError:
        pass
    else:
        if new_cover_code:
            new_cover_code += ',\n            '
        new_cover_code += "ENV_NAME.JS_NODE: '''" + js_cover_code + "'''"

    new_referee_code = ('''from checkio_referee import RefereeRank, ENV_NAME



import settings_env
from tests import TESTS


class Referee(RefereeRank):
    TESTS = TESTS
    ENVIRONMENTS = settings_env.ENVIRONMENTS

    DEFAULT_FUNCTION_NAME = "{py_func_name}"
    FUNCTION_NAMES = {
        "python_3": "{py_func_name}",
        "js_node": "{js_func_name}"
    }
    ENV_COVERCODE = {
        {new_cover_code}
    }'''.replace('{py_func_name}', Api.kwargs['function_name']['python'])
        .replace('{js_func_name}', Api.kwargs['function_name']['js'])
        .replace('{new_cover_code}', new_cover_code))



    fill_file('verification/src/referee.py', new_referee_code)

    shutil.rmtree(os.path.join(eoc_folder, 'media'), ignore_errors=True)
    try:
        shutil.copytree(os.path.join(cio_folder, 'info/media'),
            os.path.join(eoc_folder, 'media'))
    except FileNotFoundError:
        pass

    if git_repo:
        os.chdir(eoc_folder)
        subprocess.run(['git', 'init'])
        subprocess.run(['git', 'add', '.'])
        subprocess.run(['git', 'commit', '-m', 'first commit'])
        subprocess.run(['git', 'remote', 'add', 'origin', git_repo])
        subprocess.run(['git', 'push', '-u', 'origin', 'master'])
