import socket
import json

from Exscript.protocols import Telnet


echo = None


def init(ip, port):
    global echo
    print("CONNECT", ip, port)
    echo = Telnet(connect_timeout=None)
    echo.connect(ip, port)


def send(data):
    data = str(data).encode("utf-8") + b"\0"
    echo.send(data)


def send_json(data):
    send(json.dumps(data))


def _receive_sock(trys=4):
    sock = echo.tn.get_socket()
    try:
        return sock.recv(100000000).decode("utf-8")
    except socket.error as e:
        if e.errno != 4:
            trys -= 1
            if not trys:
                raise
        return _receive_sock(trys=trys)


STREAM_DATA = ""


def receive():
    global STREAM_DATA
    no_data_counter = 100
    while True:
        new_data = _receive_sock()
        if not new_data:
            no_data_counter -= 1
            if not no_data_counter:
                raise ValueError("No data")
        STREAM_DATA += new_data
        if "\0" in STREAM_DATA:
            recv = STREAM_DATA[:STREAM_DATA.index("\0")]
            STREAM_DATA = STREAM_DATA[STREAM_DATA.index("\0") + 1:]
            return recv


def send_recv(send_data):
    send(send_data)
    data = ""
    echo.tn.get_socket()
    no_data_counter = 100
    while True:
        new_data = _receive_sock()
        if not new_data:
            no_data_counter -= 1
            if not no_data_counter:
                raise ValueError("No data")
        data += new_data
        if "\0" in new_data:
            recv = data.split("\0")[0]
            return recv


def send_recv_json(data):
    return json.loads(send_recv(json.dumps(data)))
