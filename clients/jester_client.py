
import socket
import json

class JesterClient(object):
    def __init__(self, host = 'localhost', port = 8844):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect( (host, port) )

    def send(self, msg):
        self.sock.send(msg + "\n")
        result = self.sock.recv(4096).strip()
        return json.loads(result)


