import socket


def main():
    pass


class Client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.seq_num = 0

    def send(self, data):
        self.socket.sendto(bytes(str(self.seq_num), 'utf-8'), ('localhost', 12345))
        self.seq_num += 1

    def receive(self):
        while True:
            data, addr = self.socket.recvfrom(1024)
            if data == b'ACK':
                break


if __name__ == '__main__':
    main()
