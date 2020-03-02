"""Server side based on socket connection"""

import socket


class Connection:
    """Handles all the connections using sockets"""

    IP = socket.gethostname()
    PORT = 1234
    BUFF_SIZE = 2 ** 7

    def __init__(self, host_socket=None):
        if host_socket is None:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.host_socket:
                self.host_socket.bind((Connection.IP, Connection.PORT))
                self.host_socket.listen(5)
        else:
            self.host_socket = host_socket

    def conn(self):
        self.remote_socket, self.address = self.host_socket.accept()

    def send(self, msg):
        pass

    def recv(self, msg):
        pass


def get_connect(host_socket):
    """Establish the connection with one user"""

    remote_socket, address = host_socket.accept()
    print(f"connection: {address}")

    while True:
        msg_inc = remote_socket.recv(BUFF_SIZE)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((IP, PORT))
    server_socket.listen(5)

    get_connect(server_socket)
