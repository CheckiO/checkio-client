import sys
import os
import json
import echo

CONNECT_ID = sys.argv[1]
PREFIX = 'uch'
TASK_NUM = sys.argv[2]
SERVICE_PORT = int(sys.argv[3])

print(SERVICE_PORT)
echo.init('127.0.0.1', SERVICE_PORT)

sys.path.insert(0, os.getenv('FOLDER_USER'))

import referee
import checkio.signals as S

run_data = echo.send_recv_json(
    {'do': 'connect', 'id': CONNECT_ID, 'pid': os.getpid(), 'prefix': PREFIX})

S.LISTENERS[S.ON_CONNECT](run_data)


def do_waiter(data):
    S.WAITERS[data['id']](data)


def do_err_waiter(data):
    S.ERR_WAITERS[data['id']](data)


def do_process_info(data):
    try:
        callback = S.PROCESS_LISTENERS[data['prefix']][data['signal']]
    except KeyError:
        pass
    else:
        callback(data)


while True:
    raw_data = echo.receive()
    data = json.loads(raw_data)
    globals()['do_' + data['do']](data)
