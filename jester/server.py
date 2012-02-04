
from tornado.netutil import TCPServer
from tornado.ioloop import IOLoop
#from tornado.iostream import IOStream
import json
from logging import info
from jester.parser import *

class JesterServer(TCPServer):
    def handle_stream(self, stream, address):
        info("incoming connection")
        Connection(stream, address)

class Connection(object):
    def __init__(self, stream, address):
        self.stream = stream
        self.address = address
        self.stream.read_until('\n', self.read_line)

    def read_line( self, data ):
        data = data.strip()
        info(  "received {0}".format(data) )
        tmp = {'result':'ok'}
        try:
            result = Parser.parse(data)
            tmp = result.evaluate()
            #info(result)
            #tmp = {'result':'ok'}
        except Exception as e:
            tmp = {'result':'fail'}
            tmp['message'] = e.message
            print e
        
        tmp = json.dumps(tmp) + "\n"
        self.stream.write(tmp, self.finished_writing)

    def finished_writing(self):
        self.stream.read_until('\n', self.read_line)


def run():
    RuleList.load_rules()
    server = JesterServer()
    server.listen(8888)
    IOLoop.instance().start()

