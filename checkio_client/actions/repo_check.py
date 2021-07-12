import asyncio
import json
import codecs
import os
import sys
import signal
import base64
import logging
import warnings

from checkio_client.settings import conf

REPO_FOLDER = None

USER_CODE = None
USER_RUNNER = None
CIO_WRITER = None
UCH_PROCESS = None
PROCESS_PID = None
PROCESS = None
TRANS_FOLDER = None


async def do_tester_get_files(data, writer):
    ret = {}
    for file_path in data['files'].split(','):
        folder_path = None

        if TRANS_FOLDER:
            folder_path = os.path.join(TRANS_FOLDER, file_path)
            if not os.path.exists(folder_path):
                folder_path = None

        if folder_path is None:
            folder_path = os.path.join(REPO_FOLDER, file_path)
            
        if not os.path.exists(folder_path):
            warnings.warn('File "' + folder_path + '" doesn\'t exist')
            continue
        try:
            fh = codecs.open(folder_path, "r", "utf-8")
            ret[file_path] = fh.read()
            fh.close()
        except IOError as e:
            warnings.warn('Error during oppening file "' + folder_path + '" :' + str(e))
            continue

    ret['question'] = data['question']
    ret['do'] = 'answer'
    await send_tester_data(writer, ret)


async def do_tester_get_tests(data, writer):
    ret = {}
    tests_path = os.path.join(REPO_FOLDER, 'verification/tests.py')
    with open(tests_path) as fh:
        test_code = fh.read()
        env_code = {}
        exec(test_code, env_code)
        ret['tests'] = env_code['TESTS']
        
    ret['question'] = data['question']
    ret['do'] = 'answer'
    await send_tester_data(writer, ret)


async def do_tester_get_file(data, writer):
    folder_path = None

    if TRANS_FOLDER:
        folder_path = os.path.join(TRANS_FOLDER, data['path'])
        if not os.path.exists(folder_path):
            folder_path = None

    if folder_path:
        try:
            fh = open(folder_path, "rb")
            fdata = fh.read()
            fh.close()
        except IOError as e:
            warnings.warn('Error during oppening file "' + folder_path + '" :' + str(e))
            await send_tester_data(writer, {
                'do': 'answer',
                'error': "Open error",
                'question': data['question'],
                'path': data['path']
            })
        else:
            await send_tester_data(writer, {
                'do': 'answer',
                'data': base64.standard_b64encode(fdata).decode('utf8'),
                'question': data['question'],
                'path': data['path']
            })
    else:
        folder_path = os.path.join(REPO_FOLDER, data['path'])
        if not os.path.exists(folder_path):
            warnings.warn('File "' + folder_path + '" doesn\'t exist')
            await send_tester_data(writer, {
                'do': 'answer',
                'error': "File doesn't exist",
                'question': data['question'],
                'path': data['path']
            })
        else:
            try:
                fh = open(folder_path, "rb")
                fdata = fh.read()
                fh.close()
            except IOError as e:
                warnings.warn('Error during oppening file "' + folder_path + '" :' + str(e))
                await send_tester_data(writer, {
                    'do': 'answer',
                    'error': "Open error",
                    'question': data['question'],
                    'path': data['path']
                })
            else:
                await send_tester_data(writer, {
                    'do': 'answer',
                    'data': base64.standard_b64encode(fdata).decode('utf8'),
                    'question': data['question'],
                    'path': data['path']
                })


async def send_tester_data(writer, data):
    writer.write(json.dumps(data).encode() + b'\0')

async def tcp_echo_client(message, loop):
    global CIO_WRITER
    conf_data = conf.default_domain_data
    reader, writer = await asyncio.open_connection(conf_data['server_host'], 
                                                   int(conf_data['server_port']),
                                                   loop=loop)
    CIO_WRITER = writer

    logging.debug('Send: %r' % message)
    writer.write(message.encode() + b'\0')
    logging.info('Open ' + conf_data['url_main'] + '/mission/tester/')

    while True:
        data = await reader.readuntil('\0'.encode())
        data = data.decode('utf8')[:-1]
        logging.debug('Received: %r' % data)
        data = json.loads(data)
        await globals()['do_tester_' + data['do']](data, writer)
    

    print('Close the socket')
    writer.close()

async def do_tester_start_process(data, writer):
    global loop
    global USER_CODE
    global USER_RUNNER
    global PROCESS
    USER_CODE = data['code']
    USER_RUNNER = data['runner']
    connection_id = data['connection_id']
    task_num = data['task_num']
    openline = ' '.join((sys.executable,
                        conf.uch_file,
                        str(connection_id),
                        str(task_num),
                        str(conf.local_uch_port)))
    envs = dict(os.environ)
    envs.update({
        'PYTHONIOENCODING': 'utf8',
        'PYTHONUNBUFFERED': '0',
        'FOLDER_USER': os.path.join(REPO_FOLDER, 'verification')
    })
    PROCESS = await asyncio.create_subprocess_shell(openline,
                               env=envs)

async def do_tester_kill_process(data, writer):
    PROCESS.kill()

async def do_tester_to_process(data, writer):
    UCH_PROCESS.sendData(data['data'])

async def do_tester_auth_error(data, writer):
    logging.error('Wrong key in config.ini file')
    logging.info('You can find a correct Api Key here: ' + conf.default_domain_data['url_main'] + '/profile/edit/')
    sys.exit()

#762 +

class EchoServerClientProtocol(asyncio.Protocol):

    def connection_made(self, transport):
        self.transport = transport

    def sendData(self, data):
        return self.transport.write(str.encode(json.dumps(data)) + b'\0')

    def data_received(self, lines):
        for line in lines.split(b'\0')[:-1]:
            data = line.decode('utf8')
            logging.debug('Data received: {!r}'.format(data))

            data = json.loads(data)

            method = getattr(self, 'do_' + data['do'], None)
            if method is not None:
                method(data)
            else:
                CIO_WRITER.write(b'{"do":"from_process", "data":' + line + b'}\0')

    def do_connect(self, data):
        global UCH_PROCESS
        global PROCESS_PID
        UCH_PROCESS = self
        PROCESS_PID = data['pid']
        self.sendData({
            'do': 'check',
            'code': USER_CODE,
            'runner': USER_RUNNER
        })


def main(args):
    global REPO_FOLDER
    global TRANS_FOLDER

    REPO_FOLDER = args.folder[0]
    if args.translation:
        TRANS_FOLDER = os.path.join(REPO_FOLDER, 'translations', args.translation)
    AUTH_KEY = conf.default_domain_data['key']
    message = '{"do": "connect", "key": "' + AUTH_KEY + '"}'
    if sys.platform == 'win32':
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait([
        tcp_echo_client(message, loop),
        loop.create_server(EchoServerClientProtocol, '127.0.0.1', int(conf.local_uch_port))
    ]))
    loop.close()