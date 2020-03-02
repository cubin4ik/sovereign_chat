"""Server side based on socket connection"""

import socket
import threading


class Connection:
    """Handles all the connections using sockets"""

    IP = "127.0.0.1"
    PORT = 1234
    BUFF_SIZE = 2 ** 7
    HEADER_SIZE = 10
    QUEUE = 5

    def __init__(self, socket_type=None):
        """Creates an endpoint using TCP/IP"""

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.host_socket:

            # Checks an endpoint type (server or client)
            if socket_type is None or socket_type == "client":
                self.host_socket.connect((Connection.IP, Connection.PORT))
            elif socket_type == "server":
                self.host_socket.bind((Connection.IP, Connection.PORT))
                self.host_socket.listen(Connection.QUEUE)

                # TODO: Add thread joining list
                while True:
                    print("listening..")
                    remote_socket, address = self.host_socket.accept()
                    print(f"connection: {address}")

                    # Establishing messages headers
                    remote_socket.send(f"{Connection.HEADER_SIZE}".encode("utf-8"))

                    thread = threading.Thread(target=self.serv_client, args=[remote_socket])
                    thread.start()
            else:
                raise ValueError("You need to specify connection type: \"server\" or \"client\"")

    @staticmethod
    def serv_client(client_socket):
        """A thread of serving one client"""

        new_msg = ""
        req_full = ""
        while True:
            msg_chunk = client_socket.recv(Connection.BUFF_SIZE).decode("utf-8")

            if not msg_chunk:
                break

            if new_msg:
                msg_len = int(msg_chunk[:Connection.HEADER_SIZE].strip())
            req_full += msg_chunk

        client_socket.send(f"received: {req_full}".encode("utf-8"))

