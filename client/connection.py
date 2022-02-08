"""Server side based on socket connection"""

import os
import socket


def get_ip():
    """Get IP/port from file first or set localhost"""

    if os.path.isfile('config.txt'):
        with open("config.txt", "r") as rf:
            full_address = rf.read().split('\n')
            if len(full_address) > 1:
                ip = full_address[0].strip()
                port = full_address[1].strip()
                if validate_addr(ip, port):
                    return ip, int(port)

    return socket.gethostname(), 8000


def validate_addr(ip, port):
    """Handles all the connections using sockets"""

    ip = ip.split('.')
    if len(ip) != 4:
        return False
    for bit in ip:
        if not bit.isdigit():
            return False
        if int(bit) < 0 or int(bit) > 255:
            return False

    if not port.isdigit():
        return False

    return True


class Connection:
    """Handles all the connections using sockets"""

    IP, PORT = get_ip()
    BUFF_SIZE = 2 ** 7
    BUFF_SIZE_IMG = 2 ** 22
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

    def request_server(self, msg, close=None):
        """Returns response from server to request (with header)"""

        msg = f"{len(msg):<{Connection.HEADER_SIZE}}" + msg

        try:
            self.host_socket.send(msg.encode("utf-8"))
            resp = self.receive_msg()

            if close == "KEEP_ALIVE":
                print("SOCKET IS ALIVE")
                return resp
            else:
                self.close_connection()
                print("REQUEST SOCKET CLOSED. RESPONSE: ", resp)
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

    def send_img(self, img):
        """Sends images to server"""

        msg = img

        try:
            self.host_socket.send(msg)
            resp = self.receive_msg()

            self.close_connection()

            return resp

        except ConnectionResetError:
            print("Connection failed")

    def receive_img(self):
        """Receiving any long image"""

        # TODO: get fixed length and loop
        img = self.host_socket.recv(Connection.BUFF_SIZE_IMG)
        return img

    def close_connection(self):
        """Closes given sockets"""

        self.host_socket.shutdown(socket.SHUT_RDWR)  # TODO: Replace with "with" statement (on server side too)
        self.host_socket.close()
