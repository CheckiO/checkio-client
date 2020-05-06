import os
import re
import json
import pprint

from checkio_client.settings import conf


def format_data(obj, to_js=False):
    data = pprint.pformat(obj, width=40)
    if to_js:
        return data.replace('True', 'true').replace('False', 'false').replace('None', 'Null')
    return data

def gen_args(len_args):
    return ', '.join(map(chr,range(ord('a'), ord('a') + len_args)))

def gen_init_py(funcname, tests, is_multiple=True):
    first_input = tests['Basics'][0]['input']
    ret = '''def {funcname}({args}):
    # your code here
    return None


if __name__ == '__main__':
    print("Example:")
    print({funcname}({call}))

    # These "asserts" are used for self-checking and not for an auto-testing'''.format(
        funcname=funcname,
        args=gen_args(is_multiple and len(first_input) or 1),
        call=is_multiple and format_data(first_input)[1:-1] or format_data(first_input)
    ) + '\n'
    for test in tests['Basics']:
        ret += '    assert {funcname}({call}) == {out}\n'.format(
            funcname=funcname,
            call=is_multiple and format_data(test['input'])[1:-1] or format_data(test['input']),
            out=format_data(test['answer'])
        )
    ret += '    print("Coding complete? Click \'Check\' to earn cool rewards!")\n'
    return ret

def gen_init_js(funcname, tests, is_multiple=True):
    first_input = tests['Basics'][0]['input']
    ret = '''import assert from "assert";

function {funcname}({args}) {{
    // your code here
    return undefined;
}}

console.log('Example:');
console.log({funcname}({call}));

// These "asserts" are used for self-checking'''.format(
        funcname=funcname,
        args=gen_args(is_multiple and len(first_input) or 1),
        call=is_multiple and format_data(first_input, to_js=True)[1:-1] or format_data(first_input, to_js=True)
    ) + '\n'
    for test in tests['Basics']:
        ret += 'assert.{equal}({funcname}({call}), {out});\n'.format(
            funcname=funcname,
            call=is_multiple and format_data(test['input'], to_js=True)[1:-1] or format_data(test['input'], to_js=True),
            out=format_data(test['answer'], to_js=True),
            equal=('deepEqual' if isinstance(test['answer'],dict) or isinstance(test['answer'], list) else 'equal')
        )
    ret += '''
console.log("Coding complete? Click 'Check' to earn cool rewards!");
    '''
    return ret

def gen_init_ts(funcname, tests, is_multiple=True):
    first_input = tests['Basics'][0]['input']
    ret = '''
export function {funcname}({args}) {{

    // your code here
    return undefined;
}}

import * as assert from 'assert';
console.log('Example:');
console.log({funcname}({call}));

// These "asserts" are used for self-checking'''.format(
        funcname=funcname,
        args=gen_args(is_multiple and len(first_input) or 1),
        call=is_multiple and format_data(first_input, to_js=True)[1:-1] or format_data(first_input, to_js=True)
    ) + '\n'
    for test in tests['Basics']:
        ret += 'assert.{equal}({funcname}({call}), {out});\n'.format(
            funcname=funcname,
            call=is_multiple and format_data(test['input'], to_js=True)[1:-1] or format_data(test['input'], to_js=True),
            out=format_data(test['answer'], to_js=True),
            equal=('deepEqual' if isinstance(test['answer'],dict) or isinstance(test['answer'], list) else 'equal')
        )
    ret += '''
console.log("Coding complete? Click 'Check' to earn cool rewards!");'''
    return ret


def gen_inits(f_init_py, name_py, f_init_js, name_js, tests, is_multiple=True):

    if name_py:
        with open(f_init_py, 'w') as fh:
            fh.write(gen_init_py(name_py, tests, is_multiple=is_multiple))

    if name_js:
        with open(f_init_js, 'w') as fh:
            domain_data = conf.default_domain_data
            if domain_data['game'] == 'cio':
                fh.write(gen_init_js(name_js, tests, is_multiple=is_multiple))
            else:
                fh.write(gen_init_ts(name_js, tests, is_multiple=is_multiple))

def get_tests(f_tests):
    with open(f_tests) as fh:
        globs = {}
        exec(fh.read(), globs)
        return globs['TESTS']



def gen_folders(
        name_py, name_js,
        f_tests=None,
        f_init_py=None,
        f_init_js=None,
        f_referee=None,
        f_animation=None,
        f_descriptions=None,
        desc_tests=2,
        is_multiple=True
        ):
    if f_tests is not None:
        tests = get_tests(f_tests)

    if f_init_py is not None and f_init_js is not None:
        gen_inits(f_init_py, name_py, f_init_js, name_js, tests, is_multiple)

    if f_referee is not None:
        referee_filename = f_referee
        with open(referee_filename) as fh:
            referee = fh.read()
            if name_py:
                referee = re.sub(
                    r'\"python\"\:\s*\"[^\"]+\"',
                    r'"python": "{}"'.format(name_py),
                    referee, flags=re.MULTILINE)
            if name_js:
                referee = re.sub(
                    r'\"js\"\:\s*\"[^\"]+\"',
                    r'"js": "{}"'.format(name_js),
                    referee, flags=re.MULTILINE)

        with open(referee_filename, 'w') as fh:
            fh.write(referee)

    if f_animation is not None:
        referee_filename = f_animation
        with open(referee_filename) as fh:
            referee = fh.read()
            if name_py:
                referee = re.sub(
                    r"python\:\s*\'[^\']+\'",
                    r"python: '{}'".format(name_py),
                    referee, flags=re.MULTILINE)
            if name_js:
                referee = re.sub(
                    r"js\:\s*\'[^\']+\'",
                    r"js: '{}'".format(name_js),
                    referee, flags=re.MULTILINE)

        with open(referee_filename, 'w') as fh:
            fh.write(referee)

    for description_filename in f_descriptions:
        with open(description_filename) as fh:
            desc = fh.read()

        py_tests = ''
        js_tests = ''
        for test in tests['Basics'][:desc_tests]:
            if name_py:
                py_tests += '{funcname}({call}) == {out}\n'.format(
                    funcname=name_py,
                    call=format_data(test['input'])[1:-1] if is_multiple else format_data(test['input']),
                    out=format_data(test['answer'])
                )
            if name_js:
                js_tests += '{funcname}({call}) == {out}\n'.format(
                    funcname=name_js,
                    call=format_data(test['input'], to_js=True)[1:-1] if is_multiple else format_data(test['input'], to_js=True),
                    out=format_data(test['answer'], to_js=True)
                )

        if name_js:
            desc = re.sub(
                r'\<pre\sclass\=\"brush\:\sjavascript\"\>.*?\<\/pre\>',
                '<pre class="brush: javascript">' + js_tests + '</pre>',
                desc, flags=re.MULTILINE | re.DOTALL)
        if name_py:
            desc = re.sub(
                r'\<pre\sclass\=\"brush\:\spython\"\>.*?\<\/pre\>',
                '<pre class="brush: python">' + py_tests + '</pre>',
                desc, flags=re.MULTILINE | re.DOTALL)

        with open(description_filename, 'w') as fh:
            fh.write(desc)




def main(args):
    folder = args.folder
    descriptions = [os.path.join(folder, 'info', 'task_description.html')]
    translations = os.path.join(folder, 'translations')
    if os.path.exists(translations):
        for dir_name in os.listdir(translations):
            tr_description = os.path.join(translations, dir_name, 'info', 'task_description.html')
            if not os.path.exists(tr_description):
                continue
            descriptions.append(tr_description)

    gen_folders(
            args.py_function, args.js_function,
            f_tests=os.path.join(folder, 'verification', 'tests.py'),
            f_init_py=os.path.join(folder, 'editor', 'initial_code', 'python_3'),
            f_init_js=os.path.join(folder, 'editor', 'initial_code', 'js_node'),
            f_referee=os.path.join(folder, 'verification', 'referee.py'),
            f_animation=os.path.join(folder, 'editor', 'animation', 'init.js'),
            f_descriptions=descriptions,
            desc_tests=args.desc_tests,
            is_multiple=not args.not_multy,
        )
    
    print('Done.')


def gen_cli_interface(folder, py_function, js_function):
    cli_interface_folder = os.path.join(folder, 'interfaces', 'checkio_cli', 'src')
    cli_interface_file = os.path.join(cli_interface_folder, 'interface.py')
    interface_content = '''
from handlers.simple_output import SimplePrintHandler
from server import TCPConsoleServer


class ServerController(TCPConsoleServer):
    cls_handler = SimplePrintHandler

    FUNCTION_NAMES = {{
        "python_3": "{py_function}",
        "js_node": "{js_function}"
    }}
    '''.format(py_function=py_function, js_function=js_function)

    os.makedirs(cli_interface_folder, exist_ok=True)
    with open(cli_interface_file, 'w') as fh:
        fh.write(interface_content)


def main_eoc(args):
    from checkio_client.eoc.folder import Folder
    from checkio_client.eoc.initial import init_home_file

    folder = args.mission
    #folder = Folder(mission).mission_folder()
    descriptions = [os.path.join(folder, 'info', 'description.html')]
    translations = os.path.join(folder, 'translations')
    if os.path.exists(translations):
        for dir_name in os.listdir(translations):
            tr_description = os.path.join(translations, dir_name, 'info', 'description.html')
            if not os.path.exists(tr_description):
                continue
            descriptions.append(tr_description)

    gen_folders(
            args.py_function, args.js_function,
            f_tests=os.path.join(folder, 'verification', 'src', 'tests.py'),
            f_init_py=os.path.join(folder, 'initial', 'python_3'),
            f_init_js=os.path.join(folder, 'initial', 'js_node'),
            f_animation=os.path.join(folder, 'animation', 'init.js'),
            f_descriptions=descriptions,
            desc_tests=args.desc_tests,
        )

    referee_filename = os.path.join(folder, 'verification', 'src', 'referee.py')
    with open(referee_filename) as fh:
        referee = fh.read()
        referee = re.sub(
            r'\"python_3\"\:\s*\"[^\"]+\"',
            r'"python_3": "{}"'.format(args.py_function),
            referee, flags=re.MULTILINE)
        referee = re.sub(
            r'\"js_node\"\:\s*\"[^\"]+\"',
            r'"js_node": "{}"'.format(args.js_function),
            referee, flags=re.MULTILINE)

    with open(referee_filename, 'w') as fh:
        fh.write(referee)

    gen_cli_interface(folder, args.py_function, args.js_function)

    
    print('Done.')
