"""Server side based on socket connection"""

import socket
import threading


class Connection:
    """Handles all the connections using sockets"""

    IP = "127.0.0.1"
    PORT = 1234
    BUFF_SIZE = 2
    HEADER_SIZE = 10
    QUEUE = 5

    def __init__(self, socket_type=None):
        """Creates an endpoint using TCP/IP"""

        # TODO: Find how to close all sockets correctly
        self.host_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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

                # TODO: Establishing messages headers below
                # remote_socket.send(f"{Connection.HEADER_SIZE}".encode("utf-8"))

                thread = threading.Thread(target=self.serv_client, args=[remote_socket])
                thread.start()
        else:
            raise ValueError("You need to specify connection type: \"server\" or \"client\"")

    def serv_client(self, client_socket):
        """A thread of serving one client"""

        req = self.receive(client_socket)
        if not req:
            print(f"connection failed: {client_socket}")
        else:
            print(f"received: {req}")
            req = f"{len(req):<{Connection.HEADER_SIZE}}" + req
            client_socket.send(req.encode("utf-8"))

    @staticmethod
    def receive(remote_socket):
        """Receiving any long message"""

        new_msg = True
        req_full = ""
        msg_len = 0
        while True:
            msg_chunk = remote_socket.recv(Connection.BUFF_SIZE).decode("utf-8")

            if not msg_chunk:
                break
            if new_msg:
                msg_len = int(msg_chunk[:Connection.HEADER_SIZE].strip())
                new_msg = False

            req_full += msg_chunk

            if len(req_full[Connection.HEADER_SIZE:]) == msg_len:
                return req_full[Connection.HEADER_SIZE:]

    def send_req(self, msg):
        """Returns response from server to request (with header)"""

        msg = f"{len(msg):<{Connection.HEADER_SIZE}}" + msg
        self.host_socket.send(msg.encode("utf-8"))

        resp = self.receive(self.host_socket)

        return resp

