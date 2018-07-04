from checkio.signals import LISTENERS, WAITERS, ERR_WAITERS, PROCESS_LISTENERS
import echo

DEFAULT_RUNNER_PREFIX = 'req'
DEFAULT_FUNCTION = 'checkio'

WAITER_COUNTER = 0


def add_waiter(callback, errback=None):
    global WAITER_COUNTER
    WAITER_COUNTER += 1
    WAITERS[WAITER_COUNTER] = callback
    if errback is not None:
        ERR_WAITERS[WAITER_COUNTER] = errback

    return WAITER_COUNTER


def add_listener(signal, callback):
    LISTENERS[signal] = callback


def add_process_listener(prefix, signal, callback):
    if prefix not in PROCESS_LISTENERS:
        PROCESS_LISTENERS[prefix] = {}

    PROCESS_LISTENERS[prefix][signal] = callback
    echo.send_json({
        'do': 'set_process_informer',
        'prefix': prefix,
        'signal': signal
    })


def start_runner(code, runner, controller_type, callback,
                 prefix=DEFAULT_RUNNER_PREFIX, errback=None,
                 add_close_builtins=None, add_allowed_modules=None, remove_allowed_modules=None,
                 write_execute_data=False, cover_code=None, name='__check__'):
    wcode = add_waiter(callback, errback)
    echo.send_json({
        'do': 'start_runner',
        'waiter': wcode,
        'code': code,
        'runner': runner,
        'prefix': prefix,
        'type': controller_type,
        'name': name,
        'env_config': {
            'add_close_builtins': add_close_builtins,
            'add_allowed_modules': add_allowed_modules,
            'remove_allowed_modules': remove_allowed_modules,
            'cover_code': cover_code
        },
        'config': {
            'write_execute_data': write_execute_data
        }
    })
    return wcode

def sys_runner(code, callback,
                 prefix=DEFAULT_RUNNER_PREFIX, errback=None):
    wcode = add_waiter(callback, errback)
    echo.send_json({
        'do': 'sys_runner',
        'waiter': wcode,
        'code': code,
        'prefix': prefix
    })
    return wcode


def kill_runner(prefix):
    echo.send_json({
        'do': 'kill_runner',
        'prefix': prefix
    })


def execute_function(input_data, callback, func=DEFAULT_FUNCTION, prefix=DEFAULT_RUNNER_PREFIX, errback=None):
    wcode = add_waiter(callback, errback)
    echo.send_json({
        'do': 'execute_function',
        'waiter': wcode,
        'func': func,
        'prefix': prefix,
        'input': input_data
    })
    return wcode


def close():
    echo.send_json({
        'do': 'close'
    })


def success(score=0):
    echo.send_json({
        'do': 'success',
        'score': score
    })


def fail(num, description=''):
    echo.send_json({
        'do': 'fail',
        'num': num,
        'description': description
    })


def request_write(data):
    echo.send_json({
        'do': 'request_write',
        'data': data
    })


def request_write_start_in(name):
    request_write(["start_in", name])


def request_write_in(data, process):
    request_write(["in", data, process])


def request_write_ext(data):
    request_write(["ext", data])



