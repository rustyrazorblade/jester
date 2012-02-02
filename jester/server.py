
from tornado.netutil import TCPServer
from tornado.ioloop import IOLoop
#from tornado.iostream import IOStream
import json

class JesterServer(TCPServer):
    def handle_stream(self, stream, address):
        Connection(stream, address)

class Connection(object):
    def __init__(self, stream, address):
        self.stream = stream
        self.address = address
        self.stream.read_until('\n', self.read_line)

    def read_line( self, data ):
        tmp = {'result':'ok'}
        tmp = json.dumps(tmp) + "\n"

        self.stream.write(tmp, self.finished_writing)

    def finished_writing(self):
        self.stream.read_until('\n', self.read_line)



server = JesterServer()
server.listen(8888)
IOLoop.instance().start()

