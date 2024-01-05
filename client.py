import socket
import sys
import threading


def main():
    listen_port = 8082
    send_port = 8083
    data_count = 1000
    if len(sys.argv) >= 2:
        listen_port = int(sys.argv[1])
    if len(sys.argv) >= 3:
        send_port = int(sys.argv[2])
    if len(sys.argv) >= 4:
        data_count = int(sys.argv[3])
    application = Client(('localhost', listen_port), ('localhost', send_port), data_count)
    application.run()


class Client:
    def __init__(self, listen_address: tuple[str, int], send_address: tuple[str, int], data_count: int):
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.listen_socket.bind(listen_address)
        self.listen_seq_number = 0
        self.listen_data = []
        self.data_count = data_count

        self.send_address = send_address
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.send_base_seq_number = 1
        self.send_current_seq_number = 1
        self.send_data = []

    def run(self):
        listen_thread = threading.Thread(target=self._listen)
        listen_thread.start()
        listen_thread.join()

    def _listen(self):
        while True:
            data, addr = self.listen_socket.recvfrom(1024)
            is_ack = bool(data[0])
            seq_number = int.from_bytes(data[1:5], 'big')

            if is_ack:
                continue
            else:
                # Read data
                data = data[5:].decode()
                print(f'Data received: {data}, seq_number: {seq_number}')

                if seq_number != self.listen_seq_number + 1:
                    # Send duplicate ACK
                    print(f'Sending duplicate ack: {self.listen_seq_number}')
                    is_ack = int(True).to_bytes(1, 'big')
                    seq_number = self.listen_seq_number.to_bytes(4, 'big')
                    ack = is_ack + seq_number
                    self.send_socket.sendto(ack, self.send_address)
                    continue

                # Save data
                self.listen_data.append(data)

                # Send new ACK
                print(f'Sending ack: {seq_number}')
                is_ack = int(True).to_bytes(1, 'big')
                seq_number = seq_number.to_bytes(4, 'big')
                ack = is_ack + seq_number
                self.send_socket.sendto(ack, addr)

                self.listen_seq_number += 1

                if self.listen_seq_number == self.data_count:
                    output = open('output.txt', 'w')
                    output.write('\n'.join(self.listen_data))
                    break


if __name__ == '__main__':
    main()
