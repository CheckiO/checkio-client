import os
import re
import json

def gen_args(len_args):
    return ', '.join(map(chr,range(ord('a'), ord('a') + len_args)))

def gen_init_py(funcname, tests, args):
    first_input = tests['Basics'][0]['input']
    ret = '''def {funcname}({args}):
    # your code here
    return None


if __name__ == '__main__':
    print("Example:")
    print({funcname}({call}))

    # These "asserts" are used for self-checking and not for an auto-testing'''.format(
        funcname=funcname,
        args=gen_args(len(first_input)),
        call=json.dumps(first_input)[1:-1]
    ) + '\n'
    for test in tests['Basics']:
        ret += '    assert {funcname}({call}) == {out}\n'.format(
            funcname=funcname,
            call=json.dumps(test['input'])[1:-1],
            out=json.dumps(test['answer'])
        )
    ret += '    print("Coding complete? Click \'Check\' to earn cool rewards!")\n'
    return ret

def gen_init_js(funcname, tests, args):
    first_input = tests['Basics'][0]['input']
    ret = '''"use strict";

function {funcname}({args}) {{

    // your code here
    return undefined;
}}

var assert = require('assert');
if (!global.is_checking) {{
    console.log('Example:');
    console.log({funcname}({call}));

    // These "asserts" are used for self-checking and not for an auto-testing'''.format(
        funcname=funcname,
        args=gen_args(len(first_input)),
        call=json.dumps(first_input)[1:-1]
    ) + '\n'
    for test in tests['Basics']:
        ret += '    assert.{equal}({funcname}({call}), {out});\n'.format(
            funcname=funcname,
            call=json.dumps(test['input'])[1:-1],
            out=json.dumps(test['answer']),
            equal=('deepEqual' if isinstance(test['answer'],dict) or isinstance(test['answer'], list) else 'equal')
        )
    ret += '''
    console.log("Coding complete? Click 'Check' to earn cool rewards!");
}
    '''
    return ret


def main(args):
    folder = args.folder
    with open(os.path.join(folder, 'verification', 'tests.py')) as fh:
        globs = {}
        exec(fh.read(), globs)
        tests = globs['TESTS']
    with open(os.path.join(folder, 'editor', 'initial_code', 'python_3'), 'w') as fh:
        fh.write(gen_init_py(args.py_function, tests, args))
    with open(os.path.join(folder, 'editor', 'initial_code', 'js_node'), 'w') as fh:
        fh.write(gen_init_js(args.js_function, tests, args))

    referee_filename = os.path.join(folder, 'verification', 'referee.py')
    with open(referee_filename) as fh:
        referee = fh.read()
        referee = re.sub(
            r'\"python\"\:\s*\"[^\"]+\"',
            r'"python": "{}"'.format(args.py_function),
            referee, flags=re.MULTILINE)
        referee = re.sub(
            r'\"js\"\:\s*\"[^\"]+\"',
            r'"js": "{}"'.format(args.js_function),
            referee, flags=re.MULTILINE)

    with open(referee_filename, 'w') as fh:
        fh.write(referee)

    referee_filename = os.path.join(folder, 'editor', 'animation', 'init.js')
    with open(referee_filename) as fh:
        referee = fh.read()
        referee = re.sub(
            r"python\:\s*\'[^\']+\'",
            r"python: '{}'".format(args.py_function),
            referee, flags=re.MULTILINE)
        referee = re.sub(
            r"js\:\s*\'[^\']+\'",
            r"js: '{}'".format(args.js_function),
            referee, flags=re.MULTILINE)

    with open(referee_filename, 'w') as fh:
        fh.write(referee)

    description_filename = os.path.join(folder, 'info', 'task_description.html')
    with open(description_filename) as fh:
        desc = fh.read()

    py_tests = ''
    js_tests = ''
    for test in tests['Basics'][:2]:
        py_tests += '{funcname}({call}) == {out}\n'.format(
            funcname=args.py_function,
            call=json.dumps(test['input'])[1:-1],
            out=json.dumps(test['answer'])
        )
        js_tests += '{funcname}({call}) == {out}\n'.format(
            funcname=args.js_function,
            call=json.dumps(test['input'])[1:-1],
            out=json.dumps(test['answer'])
        )

    desc = re.sub(
        r'\<pre\sclass\=\"brush\:\sjavascript\"\>.*?\<\/pre\>',
        '<pre class="brush: javascript">' + js_tests + '</pre>',
        desc, flags=re.MULTILINE | re.DOTALL)
    desc = re.sub(
        r'\<pre\sclass\=\"brush\:\spython\"\>.*?\<\/pre\>',
        '<pre class="brush: python">' + py_tests + '</pre>',
        desc, flags=re.MULTILINE | re.DOTALL)

    with open(description_filename, 'w') as fh:
        fh.write(desc)
    print('Done.')
