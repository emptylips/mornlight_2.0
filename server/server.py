import datetime
import json
import threading
from logger import logger
import hashlib

from aggregation_refactor import Aggregation
from twisted.internet import reactor
from twisted.internet.protocol import Factory, Protocol

NOW = datetime.datetime.now()


class FrontExc(Exception):
    pass


class Server(Protocol):
    def __init__(self):
        logger.info('Server start')

    def connectionMade(self):
        self._peer = self.transport.getPeer()
        self.host = self._peer.host
        self.session = hashlib.md5((str(NOW) + self.host).encode('utf-8')).hexdigest()
        logger.info('SERVER {} MADE CONNECTION AS {}'.format(self.host, self.session))
        print("200 connection from {} ok as session {}\r\n".format(self.host, self.session))

    def connectionLost(self, reason):
        logger.info('SERVER {} CLOSED CONNECTION BY {} {}'.format(self.host, reason, self.session))
        print('connection from {} lost'.format(self.host))

    def dataReceived(self, data):
        if data:
            logger.info('SERVER {} RECIEVED DATA FROM HOST {}'.format(self.host, self.session))
        try:
            t = threading.Thread(target=Aggregation, args=(self.host, json.loads(data), self.session))
            t.daemon = True
            t.start()
            logger.info("SERVER {} TRANSFERED DATA TO AGGREGATION {} {}".format(self.host, self.session, str(data)))
        except Exception as exc:
            logger.error('{} cannot transder data to Aggregation'.format(self.host), exc_info=True)
        self.transport.write(b"200 recieved ok")


class ServerFactory(Factory):
    protocol = Server

    def __init__(self, quote=None):
        self.quote = quote


reactor.listenTCP(8007, ServerFactory("quote"))
reactor.run()