"""Server side based on socket connection"""

import socket


class Connection:
    """Handles all the connections using sockets"""

    IP = socket.gethostname()
    PORT = 8000
    BUFF_SIZE = 2 ** 7
    HEADER_SIZE = 10
    QUEUE = 5

    def __init__(self):
        """Creates an endpoint using TCP/IP"""

        # TODO: Find how to close all sockets correctly
        # Socket is closed when method self.request_server() is called

        self.host_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("CONNECTING TO SERVER")
        # self.host_socket.settimeout(3)
        self.host_socket.connect((Connection.IP, Connection.PORT))

    def receive_msg(self):
        """Receiving any long message"""

        new_msg = True
        req_full = ""
        msg_len = 0
        while True:
            msg_chunk = self.host_socket.recv(Connection.BUFF_SIZE).decode("utf-8")

            if not msg_chunk:
                break
            if new_msg:
                msg_len = int(msg_chunk[:Connection.HEADER_SIZE].strip())
                new_msg = False

            req_full += msg_chunk

            if len(req_full[Connection.HEADER_SIZE:]) == msg_len:
                return req_full[Connection.HEADER_SIZE:]

    def request_server(self, msg):
        """Returns response from server to request (with header)"""

        msg = f"{len(msg):<{Connection.HEADER_SIZE}}" + msg

        try:
            self.host_socket.send(msg.encode("utf-8"))
            resp = self.receive_msg()

            self.close_connection(self.host_socket)

            return resp

        except ConnectionResetError:
            print("Connection failed")

    def broadcast(self, msg):
        """Just sends any message to server"""

        msg = f"{len(msg):<{Connection.HEADER_SIZE}}" + msg

        try:
            self.host_socket.send(msg.encode("utf-8"))
            print("Message broadcasted: ", msg)
        except ConnectionResetError:
            print("Connection failed")

    @staticmethod
    def close_connection(sock):
        """Closes given sockets"""

        sock.shutdown(socket.SHUT_RDWR)  # TODO: Replace with "with" statement (on server side too)
        sock.close()
