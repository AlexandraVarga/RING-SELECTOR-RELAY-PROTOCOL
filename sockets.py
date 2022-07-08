import random
import socket
import threading

BUFFER_SIZE = 1024


# Class for RING COMMUNICATION
class CommNode(threading.Thread):
    def __init__(self, ip, port):
        threading.Thread.__init__(self)
        self.port = port
        self.IP = ip
        self.nextHopPort = None
        self.nextHopIP = None

    def setNextHop(self, nhIP, nhPort):
        self.nextHopIP = nhIP
        self.nextHopPort = nhPort

    def sendMsg(self, message):
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        send_socket.connect((self.nextHopIP, self.nextHopPort))
        send_socket.send(message.encode())

    def initcomm(self):
        self.sendMsg("1")

    def run(self):
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_socket.bind((self.IP, self.port))
        listen_socket.listen(1)

        while True:
            connection, address = listen_socket.accept()
            message = connection.recv(BUFFER_SIZE).decode()
            print(self.IP + " ---- " + str(message))
            if int(message) == 100:
                break
            else:
                self.sendMsg(str(int(message) + 1))


# Class for Node Selector
class UDPNode(threading.Thread):
    def __init__(self, ip, port, node):
        threading.Thread.__init__(self)
        self.port = port
        self.IP = ip
        self.node = node

    def run(self):
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        # Bind to address and ip
        UDPServerSocket.bind((self.IP, self.port))
        # Listen for incoming datagrams

        while (True):
            bytesAddressPair = UDPServerSocket.recvfrom(BUFFER_SIZE)
            message = bytesAddressPair[0].decode()
            address = bytesAddressPair[1]
            if self.node == 2 and int(message) % 3 == 0:
                UDPServerSocket.sendto(("ack from N2 for val:" + message).encode(), address)
            elif self.node == 3 and int(message) % 5 == 0:
                UDPServerSocket.sendto(("ack from N3 for val:" + message).encode(), address)


class NodeSelector:
    def __init__(self, ip, port, node):
        threading.Thread.__init__(self)
        self.port = port
        self.IP = ip
        self.n2HopPort = None
        self.n2HopIP = None
        self.n3HopPort = None
        self.n3HopIP = None
        self.startval = 1
        self.node = node

    def setNode2Hop(self, n2ip, n2port):
        self.n2HopIP = n2ip
        self.n2HopPort = n2port

    def setNode3Hop(self, n3ip, n3port):
        self.n3HopIP = n3ip
        self.n3HopPort = n3port

    def sendMsg(self, message):
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        if self.node == 1:
            randomhop = random.randint(0, 1)
            if randomhop == 0:
                send_socket.sendto(message.encode(), (self.n2HopIP, self.n2HopPort))
                print("From N1 to N2:" + message)
                if int(message) % 3 == 0:
                    try:
                        data, server = send_socket.recvfrom(1024)
                        print(data.decode())
                    except socket.timeout:
                        print('REQUEST TIMED OUT')
            else:
                send_socket.sendto(message.encode(), (self.n3HopIP, self.n3HopPort))
                print("From N1 to N3:" + message)
                if int(message) % 5 == 0:
                    try:
                        data, server = send_socket.recvfrom(1024)
                        print(data.decode())
                    except socket.timeout:
                        print('REQUEST TIMED OUT')

    def initcomm(self):
        while self.startval <= 100:
            self.sendMsg(str(self.startval))
            self.startval += 1


# Class for Relay COMMUNICATION

class RelayNode(threading.Thread):
    def __init__(self, ip, port,mode):
        threading.Thread.__init__(self)
        self.port = port
        self.IP = ip
        self.nextHopPort = None
        self.nextHopIP = None
        self.startVal = 1
        self.mode=mode

    def setNextHop(self, nhIP, nhPort):
        self.nextHopIP = nhIP
        self.nextHopPort = nhPort

    def sendMsg(self, message):
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        send_socket.connect((self.nextHopIP, self.nextHopPort))
        send_socket.send(message.encode())

    def initcomm(self):
        while self.startVal <= 100:
            randomhop = random.randint(1, 3)
            destination = ""
            payload = str(self.startVal)
            if randomhop == 1:
                destination = "127.0.0.1"
            elif randomhop == 2:
                destination = "127.0.0.2"
            else:
                destination = "127.0.0.3"
            print("\n"+payload + ":message init for :" + destination)
            self.sendMsg(destination + "," + payload)
            self.startVal += 1

    def run(self):
        if self.mode == 0:
            listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            listen_socket.bind((self.IP, self.port))
            listen_socket.listen(1)

            while True:
                connection, address = listen_socket.accept()
                message = connection.recv(BUFFER_SIZE).decode()
                destination, payload = message.split(",")
                if destination == self.IP:
                    print("\n"+payload + ":message received at " + self.IP)
                else:
                    print("\nmsg Fwd to next hop ")
                    self.sendMsg(message)


def main(mode):
    if mode == "RING":
        # node 1
        node1 = CommNode("127.0.0.1", 8086)
        node1.setNextHop("127.0.0.2", 8087)
        node1.start()
        # node2
        node2 = CommNode("127.0.0.2", 8087)
        node2.setNextHop("127.0.0.3", 8088)
        node2.start()
        # node3
        node3 = CommNode("127.0.0.3", 8088)
        node3.setNextHop("127.0.0.1", 8086)
        node3.start()

        node1.initcomm()
    elif mode == "NODE_SEL":
        # N1
        N1 = NodeSelector("127.0.0.1", 8086, 1)
        N1.setNode2Hop("127.0.0.2", 8087)
        N1.setNode3Hop("127.0.0.3", 8088)
        # N2
        N2 = UDPNode("127.0.0.2", 8087, 2)
        N2.start()
        # N3
        N3 = UDPNode("127.0.0.3", 8088, 3)
        N3.start()
        N1.initcomm()
    elif mode == "RELAY":
        # node 1
        sender = RelayNode("127.0.0.15", 8085,1)
        sender.setNextHop("127.0.0.1", 8086)
        sender.start()
        # node 1
        node1 = RelayNode("127.0.0.1", 8086,0)
        node1.setNextHop("127.0.0.2", 8087)
        node1.start()
        # node2
        node2 = RelayNode("127.0.0.2", 8087,0)
        node2.setNextHop("127.0.0.3", 8088)
        node2.start()
        # node3
        node3 = RelayNode("127.0.0.3", 8088,0)
        #  node3.setNextHop("127.0.0.1", 8086)
        node3.start()
        sender.initcomm()


if __name__ == "__main__":
    main("RING")
    #main("NODE_SEL")
    #main("RELAY")
