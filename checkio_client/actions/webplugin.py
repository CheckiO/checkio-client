import sys
import json
import struct

from checkio_client.settings import conf
from checkio_client.utils.code import solutions_paths


'''
--> {"event": "plugin:readFile", "fileName": "{PATH}"}
<-- {"event": "tools:readFile", "fileName": "{FULL_PATH}", "content": "{FILE_CONTENT}"}

--> {"event": "plugin:writeFile", "fileName": "{PATH}", "content": "{FILE_CONTENT}"}
<-- {"event": "tools:writeFile", "fileName": "{FULL_PATH}"}
'''

if sys.platform == "win32":
    import os, msvcrt
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

class Actions:
    @staticmethod
    def plugin__readFile(data):
        filename = data['filename']
        mission, domain = filename.split('.')
        domain_data = conf.domains[domain]
        paths = solutions_paths(domain_data['solutions'], domain_data['extension'])
        filename = paths[mission]

        send_message({
                "event": "tools:readFile",
                "content": open(filename, encoding='utf-8').read(),
                "fileName": filename
            })

    @staticmethod
    def plugin__writeFile(data):
        filename = data['filename']
        mission, domain = filename.split('.')
        domain_data = conf.domains[domain]
        paths = solutions_paths(domain_data['solutions'], domain_data['extension'])
        filename = paths[mission]

        text = data['content']
        with open(filename, 'w', encoding='utf-8') as fh:
            fh.write(text)
        send_message({
                "event": "tools:readFile",
                "fileName": "filename"
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
    getattr(Actions, data['do'].replace(':', '__'))(data)

def main(args):
    while True:
        read_next_message()
        