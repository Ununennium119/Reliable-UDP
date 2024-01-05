import socket
import threading
import time


def main():
    application = Application(('localhost', 4444), ('localhost', 5555))
    application.run()


class Application:
    def __init__(self, listen_address: tuple[str, int], send_address: tuple[str, int]):
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.listen_socket.bind(listen_address)
        self.listen_seq_number = 0
        self.listen_data = []

        self.send_address = send_address
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.send_base_seq_number = 1
        self.send_current_seq_number = 1
        self.send_window_size = 1024
        self.send_data = []

        self.lock = threading.Lock()

    def run(self):
        data_file = open('data.txt')
        self.send_data = [line.strip() for line in data_file.readlines()]
        # read_input_thread = threading.Thread(target=self._read_input)
        listen_thread = threading.Thread(target=self._listen)
        send_thread = threading.Thread(target=self._send)
        # read_input_thread.start()
        listen_thread.start()
        send_thread.start()
        # read_input_thread.join()
        listen_thread.join()
        send_thread.join()

    def _listen(self):
        while True:
            try:
                data, addr = self.listen_socket.recvfrom(1024)
                is_ack = bool(data[0])
                seq_number = int.from_bytes(data[1:5], 'big')
                print(f'Something received: {data}')

                if is_ack:
                    print(f'Ack received: {seq_number}')
                    self.lock.acquire()
                    if seq_number != self.send_base_seq_number:
                        self.send_base_seq_number = seq_number + 1
                        self.send_current_seq_number = seq_number + 1
                    else:
                        self.send_base_seq_number += 1
                    self.lock.release()
                else:
                    if seq_number != self.listen_seq_number + 1:
                        # Send duplicate ACK
                        print(f'Sending duplicate ack: {self.listen_seq_number}')
                        is_ack = int(True).to_bytes(1, 'big')
                        seq_number = self.listen_seq_number.to_bytes(4, 'big')
                        ack = is_ack + seq_number
                        self.send_socket.sendto(ack, self.send_address)
                        continue

                    # Read data
                    data = data[5:].decode()
                    self.listen_data.append(data)
                    print(f'Data received: {data}, seq_number: {seq_number}')

                    # Send new ACK
                    is_ack = int(True).to_bytes(1, 'big')
                    seq_number = seq_number.to_bytes(4, 'big')
                    ack = is_ack + seq_number
                    self.send_socket.sendto(ack, addr)

                    self.listen_seq_number += 1
            except Exception as e:
                print(e)

    def _send(self):
        while True:
            self.lock.acquire()
            current_seq_number = self.send_current_seq_number
            self.lock.release()
            if len(self.send_data) <= current_seq_number - 1:
                time.sleep(100)
                continue

            print(f'Sending data with seq number: {current_seq_number}')
            is_ack = int(False).to_bytes(1, 'big')
            seq_number = self.send_current_seq_number.to_bytes(4, 'big')
            data = is_ack + seq_number + self.send_data[current_seq_number - 1].encode()
            self.send_socket.sendto(data, self.send_address)
            self.lock.acquire()
            self.send_current_seq_number += 1
            self.lock.release()

    # def _read_input(self):
    #     while True:
    #         data = input()
    #         self.send_data.append(data)


if __name__ == '__main__':
    main()
