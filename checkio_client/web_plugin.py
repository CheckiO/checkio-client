#!/usr/bin/env python



import sys
import json
import struct

from checkio_client.runner import apply_main_args
from checkio_client.settings import conf, Config
from checkio_client.utils.code import solutions_paths, code_for_sync,\
                                    get_end_desc_line, gen_filename,\
                                    init_code_file, gen_env_line


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
        domain_data = conf.default_domain_data;
        if not domain_data.get('key'):
            raise CheckiOClientConfigError('Domain is not configure. Please do $ checkio config')
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
                'content': content
            }
        else:
            filename = gen_filename(data['slug'], data['station']);
            init_code_file(filename, 
                gen_env_line(data['slug']) + '\n' + data['content'])

            return {
                'do': 'initContent',
                'filename': filename,
                'isNew': True
            }

    @staticmethod
    def syncLocalContent(data):
        conf.set_default_domain_by_inter(data['interpreter'])
        domain_data = conf.default_domain_data;

        with open(data['filename'], 'r', encoding='utf-8') as fh:
            content = code_for_sync(fh.read())

        return {
            'do': 'syncLocalContent',
            'content': content
        }

    @staticmethod
    def syncWebContent(data):
        conf.set_default_domain_by_inter(data['interpreter'])
        domain_data = conf.default_domain_data;
        delimiter = get_end_desc_line() + '\n'

        with open(data['filename'], 'r', encoding='utf-8') as fh:
            content = fh.read()
            if delimiter in content:
                description = content.split(delimiter)[0] + delimiter
            else:
                description = gen_env_line(data['slug']) + '\n';


        with open(data['filename'], 'w', encoding='utf-8') as fh:
            fh.write(description + data['content'])

        return {
            'do': 'syncWebContent'
        }


def send_message(data):
    message = json.dumps(data).encode('utf-8')
    sys.stdout.buffer.write(struct.pack('I', len(message)))
    # Write the message itself.
    sys.stdout.buffer.write(message)
    sys.stdout.flush()

def read_next_message():
    global conf
    text_length_bytes = sys.stdin.buffer.read(4)
    if len(text_length_bytes) == 0:
        sys.exit(0)

    text_length = struct.unpack('i', text_length_bytes)[0]
    text = sys.stdin.buffer.read(text_length).decode('utf-8')
    data = json.loads(text)

    conf = Config()
    if conf.exists():
        conf.open()

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
                'type': 'CheckiOClientError',
                'text': str(e)
            })
        else:
            send_message(ret)
