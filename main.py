import socket
import threading
import time


def main():
    pass


class Application:
    def __init__(self, listen_port: int, send_port: int):
        self.listen_port = listen_port
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.listen_socket.bind(('localhost', listen_port))
        self.listen_seq_number = -1
        self.listen_data = []

        self.send_port = send_port
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.send_socket.bind(('localhost', send_port))
        self.send_seq_number = 0
        self.send_data = []

    def run(self):
        listen_thread = threading.Thread(target=self.listen)
        send_thread = threading.Thread(target=self.send_data)
        listen_thread.start()
        send_thread.start()

    def listen(self):
        while True:
            data, addr = self.listen_socket.recvfrom(1024)
            is_ack = bool(data[0])
            seq_number = int(data[1:4])

            if is_ack:
                pass
            else:
                if seq_number != self.listen_seq_number + 1:
                    # Send duplicate ACK
                    is_ack = bytes(True)
                    seq_number = self.listen_seq_number.to_bytes(4)
                    ack = is_ack + seq_number
                    self.listen_socket.send(ack)
                    continue

                # Read data
                data = data[4:].decode()
                self.listen_data.append(data)
                print(f'Data received: {data}')

                # Send new ACK
                is_ack = bytes(True)
                seq_number = seq_number.to_bytes(4)
                ack = is_ack + seq_number
                self.listen_socket.send(ack)

    def receive_ack(self):
        while True:
            data, addr = self.send_socket.recvfrom(1024)
            is_ack = bool(data[0])
            seq_number = int(data[1:4])
            if not is_ack:
                continue

            self.send_seq_number = seq_number + 1

    def read_input(self):
        while True:
            data = input()
            self.send_data.append(data)

    def send(self):
        while True:
            if len(self.send_data) <= self.send_seq_number:
                time.sleep(500)

            is_ack = bytes(False)
            seq_number = self.send_seq_number.to_bytes(4)
            data = is_ack + seq_number + self.send_data[self.send_seq_number].encode()
            self.send_socket.send(data)
            self.send_seq_number += 1


if __name__ == '__main__':
    main()
