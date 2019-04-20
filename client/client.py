# -*- coding: utf-8 -*-

from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ReconnectingClientFactory
from checks_data_collector import CheckCollector

HOST = "142.93.140.28"


class Client(Protocol):
    def sendData(self):
        self.transport.write(bytes(CheckCollector().get_collect_data(), encoding='utf8'))

    def connectionMade(self):
        self.sendData()

    def dataReceived(self, data):
        if int(data.split()[0]) == 200:
            reactor.stop()


class EchoClientFactory(ReconnectingClientFactory):
    def startedConnecting(self, connector):
        print('Started to connect.')

    def buildProtocol(self, addr):
        print('Connected.')
        print('Resetting reconnection delay')
        self.resetDelay()
        return Client()

    def clientConnectionLost(self, connector, reason):
        print('Lost connection.  Reason:', reason)
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed. Reason:', reason)
        ReconnectingClientFactory.clientConnectionFailed(self, connector,
                                                         reason)


def main():
    reactor.connectTCP('127.0.0.1', 8007, EchoClientFactory())
    reactor.run()


if __name__ == "__main__":
    main()