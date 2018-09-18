import subprocess
import json 
import struct

pipe = subprocess.Popen(['checkio', 'webplugin'],
        stdout=subprocess.PIPE, stdin=subprocess.PIPE,
        stderr=subprocess.PIPE)


def send_message(data):
    message = json.dumps(data).encode('utf-8')
    pipe.stdin.write(struct.pack('I', len(message)))
    pipe.stdin.write(message)
    pipe.stdin.flush()
    text_length_bytes = pipe.stdout.read(4)
    #print(text_length_bytes)

    text_length = struct.unpack('i', text_length_bytes)[0]
    print(pipe.stdout.read(text_length).decode('utf-8'))

#send_message({'do': 'mission_file', 'domain': 'py', 'mission': 'best-stock'})

#send_message({'do': 'read_file', 'filename': '/Users/oleksandrliabakh/www/checkio/mission-design/solutions_alfi/Elementary/best_stock.py'})
#send_message({'do': 'write_file', 'filename': '/Users/oleksandrliabakh/www/checkio/mission-design/solutions_alfi/test.py', 'text': 'WOW'})

send_message({"event": "plugin:test", "a": "1", "b": "2"})