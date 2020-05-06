#!/usr/bin/env python
import sys
import json
import struct
import time
import asyncio
#import logging

from checkio_client.runner import apply_main_args
from checkio_client.settings import conf, Config
from checkio_client.utils.code import solutions_paths, code_for_sync,\
                                    get_end_desc_line, gen_filename,\
                                    init_code_file, gen_env_line

# logger = logging.getLogger()

# # logging.basicConfig(
# #     level=logging.DEBUG,
# #     filename='~/.checkio/extension.log'
# #     )
# # logging.basicConfig(filename='~/.checkio/extension.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
# file_logger = logging.FileHandler('extension.log')
# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# file_logger.setLevel(logging.DEBUG)
# file_logger.setFormatter(formatter)
# logger.addHandler(file_logger)

# #logging.basicConfig(level=logging.DEBUG, handlers=[file_logger])
# logger.info('WOW')

class CheckiOClientError(Exception):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text

class CheckiOClientConfigError(CheckiOClientError):
    pass

if sys.platform == "win32":
    import os, msvcrt
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

class Actions:
    @staticmethod
    def initContent(data):
        conf.set_default_domain_by_inter(data['interpreter'])
        domain_data = conf.default_domain_data
        # if not domain_data.get('key'):
        #     raise CheckiOClientConfigError('Domain is not configure. Please do $ checkio config')
        if not domain_data.get('solutions'):
            raise CheckiOClientConfigError('Solutions are not synchronized yet. Please do $ checkio sync -h')

        paths = solutions_paths(domain_data['solutions'], domain_data['extension'])
        if data['slug'] in paths:

            filename = paths[data['slug']]

            with open(filename, 'r', encoding='utf-8') as fh:
                content = code_for_sync(fh.read())

            return {
                'do': 'initContent',
                'filename': filename,
                'content': content,
                'slug': data['slug']
            }
        else:
            filename = gen_filename(data['slug'], data['station'])
            init_code_file(filename, 
                gen_env_line(data['slug']) + '\n' + data['content'])

            return {
                'do': 'initContent',
                'filename': filename,
                'slug': data['slug'],
                'isNew': True
            }

    @staticmethod
    def syncLocalContent(data):
        conf.set_default_domain_by_inter(data['interpreter'])
        domain_data = conf.default_domain_data

        with open(data['filename'], 'r', encoding='utf-8') as fh:
            content = code_for_sync(fh.read())

        return {
            'do': 'syncLocalContent',
            'content': content
        }

    @staticmethod
    def syncWebContent(data):
        conf.set_default_domain_by_inter(data['interpreter'])
        domain_data = conf.default_domain_data
        delimiter = get_end_desc_line() + '\n'

        with open(data['filename'], 'r', encoding='utf-8') as fh:
            content = fh.read()
            if delimiter in content:
                description = content.split(delimiter)[0] + delimiter
            else:
                description = gen_env_line(data['slug']) + '\n'


        with open(data['filename'], 'w', encoding='utf-8') as fh:
            fh.write(description + data['content'])

        return {
            'do': 'syncWebContent'
        }

    @staticmethod
    def openEditor(data):
        from subprocess import Popen
        domain_data = conf.default_domain_data

        Popen([domain_data['editor'], data['filename']])

        return {
            'do': 'openEditor'
        }

    @staticmethod
    def listFolderStrategies(data):
        conf.set_default_domain_by_inter(data['interpreter'])
        domain_data = conf.default_domain_data
        folder = os.path.join(domain_data['solutions'], 'strategies')
        if not os.path.exists(folder):
            os.makedirs(folder)
            return {
                'do': 'listFolderStrategies',
                'files': []
            }

        files = []
        for filename in sorted(os.listdir(folder)):
            if not filename.endswith('.' + domain_data['extension']):
                continue

            abs_filename = os.path.join(folder, filename)

            # if not os.path.isfile(abs_filename):
            #     continue

            abs_filename = os.path.join(folder, filename)

            f_stats = os.stat(abs_filename)
            t_changed = time.time() - f_stats.st_mtime

            with open(abs_filename) as fh:
                content = fh.read()

            files.append({
                    'name': filename,
                    'filename': abs_filename,
                    'changed': int(t_changed),
                    'content': content,
                })

        return {
            'do': 'listFolderStrategies',
            'files': files
        }

    @staticmethod
    def saveStrategyFile(data):
        conf.set_default_domain_by_inter(data['interpreter'])
        domain_data = conf.default_domain_data
        folder = os.path.join(domain_data['solutions'], 'strategies')
        if not os.path.exists(folder):
            os.makedirs(folder)

        name = data['name']
        filename = os.path.join(folder, name)
        with open(filename, 'w') as fh:
            fh.write(data['content'])

        return {
            'do': 'saveStrategyFile',
            'name': name,
            'filename': filename,
        }

    @staticmethod
    def deleteStrategyFile(data):
        conf.set_default_domain_by_inter(data['interpreter'])
        domain_data = conf.default_domain_data
        folder = os.path.join(domain_data['solutions'], 'strategies')
        filename = os.path.join(folder, data['name'])
        if os.path.exists(filename):
            os.remove(filename)

        return {
            'do': 'deleteStrategyFile'
        }






def send_message(data):
    message = json.dumps(data).encode('utf-8')
    sys.stdout.buffer.write(struct.pack('I', len(message)))
    # Write the message itself.
    sys.stdout.buffer.write(message)
    sys.stdout.flush()

def read_next_message():
    text_length_bytes = sys.stdin.buffer.read(4)
    if len(text_length_bytes) == 0:
        sys.exit(0)

    text_length = struct.unpack('i', text_length_bytes)[0]
    text = sys.stdin.buffer.read(text_length).decode('utf-8')
    data = json.loads(text)

    conf.reload()

    return getattr(Actions, data['do'])(data)


#apply_main_args()
def main():
    while True:
        try:
            ret = read_next_message()
        except CheckiOClientError as e:
            send_message({
                'do': 'error',
                'type': e.__class__.__name__,
                'text': str(e)
            })
        except Exception as e:
            send_message({
                'do': 'error',
                'type': 'CheckiO CLient',
                'text': e.__class__.__name__ + ': ' +str(e)
            })
        else:
            send_message(ret)
