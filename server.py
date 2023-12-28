import socket


def main():
    pass


class Server:
    def __init__(self, port: int):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('localhost', port))

    def listen(self):
        while True:
            data, addr = self.socket.recvfrom(1024)
            print('Received:', data)
            self.socket.sendto(b'ACK', addr)


if __name__ == '__main__':
    main()
