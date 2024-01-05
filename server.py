import socket
import sys
import threading
import time


def main():
    listen_port = 8080
    send_port = 8081
    if len(sys.argv) >= 2:
        listen_port = int(sys.argv[1])
    if len(sys.argv) >= 3:
        send_port = int(sys.argv[2])
    application = Application(('localhost', listen_port), ('localhost', send_port))
    application.run()


class Application:
    def __init__(self, listen_address: tuple[str, int], send_address: tuple[str, int]):
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.listen_socket.bind(listen_address)
        self.listen_socket.settimeout(1)
        self.listen_seq_number = 0
        self.listen_data = []

        self.send_address = send_address
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.send_base_seq_number = 1
        self.send_current_seq_number = 1
        self.send_data = []

        self.lock = threading.Lock()

    def run(self):
        data_file = open('data.txt')
        self.send_data = [line.strip() for line in data_file.readlines()]

        listen_thread = threading.Thread(target=self._listen)
        send_thread = threading.Thread(target=self._send)
        listen_thread.start()
        send_thread.start()
        listen_thread.join()
        send_thread.join()

    def _listen(self):
        while True:
            try:
                try:
                    data, addr = self.listen_socket.recvfrom(1024)
                except socket.timeout:
                    break
                is_ack = bool(data[0])
                seq_number = int.from_bytes(data[1:5], 'big')

                if is_ack:
                    with self.lock:
                        if seq_number < self.send_base_seq_number:
                            print(f'Duplicate ck received: {seq_number}')
                            self.send_base_seq_number = seq_number + 1
                            self.send_current_seq_number = seq_number + 1
                        else:
                            print(f'Ack received: {seq_number}')
                            self.send_base_seq_number += 1
                else:
                    continue
            except Exception as e:
                print(e)

    def _send(self):
        while True:
            try:
                time.sleep(0.01)
                current_seq_number = self.send_current_seq_number
                if current_seq_number - 1 >= len(self.send_data):
                    time.sleep(1)
                    if self.send_current_seq_number - 1 >= len(self.send_data):
                        break
                    continue

                print(f'Sending data with seq number: {current_seq_number}')
                is_ack = int(False).to_bytes(1, 'big')
                seq_number = current_seq_number.to_bytes(4, 'big')
                data = is_ack + seq_number + self.send_data[current_seq_number - 1].encode()
                self.send_socket.sendto(data, self.send_address)

                threading.Timer(3, self._check_timeout, seq_number)

                with self.lock:
                    self.send_current_seq_number += 1
            except Exception as e:
                print(e)

    def _check_timeout(self, seq_number):
        if self.send_base_seq_number <= seq_number < self.send_current_seq_number:
            print(f'Timeout: {seq_number}')
            self.send_current_seq_number = seq_number


if __name__ == '__main__':
    main()
