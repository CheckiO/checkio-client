import sys
import json
import struct

from checkio_client.settings import conf
from checkio_client.utils.code import solutions_paths

if sys.platform == "win32":
    import os, msvcrt
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

class Actions:
    @staticmethod
    def mission_file(data):
        domain = data['domain']
        domain_data = conf.domains[domain]
        mission = data['mission']
        if 'solutions' not in domain_data:
            return send_message({
                    'error': 'Solutions folder is not defined for domain {}'.format(domain)
                })


        paths = solutions_paths(domain_data['solutions'], domain_data['extension'])
        send_message({
            'filename': paths[mission]
        })

    @staticmethod
    def read_file(data):
        filename = data['filename']
        send_message({
                'data': open(filename, encoding='utf-8').read()
            })

    @staticmethod
    def write_file(data):
        filename = data['filename']
        text = data['text']
        with open(filename, 'w', encoding='utf-8') as fh:
            fh.write(text)
        send_message({
                'done': 'OK'
            })

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
    getattr(Actions, data['do'])(data)

def main(args):
    while True:
        read_next_message()
        