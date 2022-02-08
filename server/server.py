"""Server based on socket connections"""

import os
import controller
import socket
import threading
import logging


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

    return socket.gethostname(), 8001


def validate_addr(ip, port):
    """Validate IP/PORT"""

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

    active_users = {}  # users that are currently in chat

    def __init__(self, socket_type=None):
        """Creates an endpoint using TCP/IP"""

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.host_socket:

            # Checks an endpoint type: server or client
            if socket_type is None or socket_type == "client":
                self.host_socket.connect((Connection.IP, Connection.PORT))
            elif socket_type == "server":
                self.host_socket.bind((Connection.IP, Connection.PORT))
                self.host_socket.listen(Connection.QUEUE)
                logging.info(f"LISTENING ON: {self.IP}:{self.PORT}")

                while True:
                    remote_socket, address = self.host_socket.accept()
                    logging.info(f"connection: {address}")

                    serving_thread = threading.Thread(target=self.serv_client, args=[remote_socket])
                    serving_thread.start()
            else:
                raise ValueError("You need to specify connection type: \"server\" or \"client\"")

    def serv_client(self, client_socket):
        """A thread of serving one client"""

        handle_data = controller.DataHandling
        session = controller.Session

        with client_socket:
            req = self.receive(client_socket)
            logging.info("REQUEST TO: ", req)

            if not req:
                print(f"Connection closed by remote socket: {client_socket.getpeername()}")
            else:
                header, body = req.split("|")
                # TODO: all sending operations should consider try/except method in case client closes connection
                if header == "CHECK_KEY":
                    print(f"KEY RECEIVED: {body}")
                    resp = session.check_key(body)
                    client_socket.send(self.format_msg(str(resp)))
                elif header == "USEREXIST":
                    print(f"CHECKING USER: {body}")
                    resp = handle_data.user_exists(body)
                    print(f"RESULT: {resp}")
                    client_socket.send(self.format_msg(str(resp)))
                elif header == "CHECKPASS":
                    credentials = body.split(";")
                    resp = handle_data.check_pass(*credentials)
                    client_socket.send(self.format_msg(str(resp)))
                elif header == "STARTSESS":
                    user_name = body
                    resp = session(user_name)
                    key = resp.key[:-len(user_name)]
                    client_socket.send(self.format_msg(str(key)))
                    print(f"KEY SENT: {key}")
                elif header == "ADD_USERS":
                    user_data = body.split(";")
                    handle_data.save_to_database(*user_data)
                elif header == "UPDATE_ME":
                    user_name, f_name, l_name = body.split(";")
                    result = handle_data.update_database(user_name, f_name, l_name)  # TODO: Finish the response
                    client_socket.send(self.format_msg(str(result)))
                elif header == "AVATAR_ME":
                    user = body
                    reply = "SEND_IMG"
                    client_socket.send(self.format_msg(str(reply)))
                    img = self.receive_img(client_socket)
                    print("RECEIVED IMAGE: ", img)
                    result = handle_data.save_img(user, img)
                    client_socket.send(self.format_msg(str(result)))
                elif header == "GETAVATAR":
                    user = body
                    img = handle_data.get_avatar(user)
                    if img:
                        reply = "SENDING_IMG"
                        client_socket.send(self.format_msg(str(reply)))
                        client_socket.send(img)
                    else:
                        reply = "NOT_FOUND"
                        client_socket.send(self.format_msg(str(reply)))
                elif header == "GETLASTID":
                    resp = handle_data.get_last_id()
                    client_socket.send(self.format_msg(resp))
                    print(f"LAST ID: {resp}")
                elif header == "DELETEKEY":
                    key = body
                    session.terminate_session(key)
                elif header == "USERSLIST":
                    if Connection.active_users != {}:
                        users_list = ""
                        for user in Connection.active_users:
                            users_list += f"{user.capitalize()},"
                        client_socket.send(self.format_msg(users_list))
                        print(f"USER LIST: {users_list}")
                elif header == "STAY_ALIVE":
                    user_name = body
                    Connection.active_users[user_name] = client_socket

                    info_msg = f"SENDALLMSG|event|{user_name} joined\n"
                    self.broadcast(info_msg=info_msg)

                    try:
                        while True:
                            msg_in = self.receive(client_socket)  # TODO: add private messages
                            if not msg_in or msg_in[:Connection.HEADER_SIZE] == "STOPMYCHAT":
                                print(f"RECEIVED STOP KEY:", user_name)
                                break
                            else:
                                destination, msg = msg_in.split("|")

                                msg = f"{destination}|{user_name}|{msg}"

                                for user in Connection.active_users:
                                    print(f"BROADCASTING: {user} - {msg}")
                                    user_socket = Connection.active_users.get(user)
                                    user_socket.send(self.format_msg(msg))

                        closed_socket = Connection.active_users.pop(body)
                        print("USER LEFT: ", closed_socket)
                        info_msg = f"SENDALLMSG|event|{user_name} left\n"

                    except ConnectionRefusedError:
                        closed_socket = Connection.active_users.pop(body)
                        print("USER LEFT: ", closed_socket)
                        info_msg = f"SENDALLMSG|event|{user_name} left the chat\n"
                    except ConnectionResetError:
                        closed_socket = Connection.active_users.pop(body)
                        print("USER LEFT: ", closed_socket)
                        info_msg = f"SENDALLMSG|event|{user_name} left the chat\n"

                    print("ACTIVE USERS: ", Connection.active_users)

                    if Connection.active_users != {}:
                        print("SENDING QUIT MSG")
                        self.broadcast(info_msg=info_msg)
                elif header == "USER_DATA":
                    key = body
                    print(f"KEY RECEIVED: {key}")
                    user_data = handle_data.get_user_data(key)
                    print("SENDING USER DATA:", user_data)
                    client_socket.send(self.format_msg(str(user_data)))
                else:
                    print(f"NOT FOUND COMMAND: {header} ---> {body}")
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

    @staticmethod
    def receive_img(remote_socket):
        """Receiving any long image"""

        # TODO: get fixed length and loop
        img = remote_socket.recv(Connection.BUFF_SIZE_IMG)
        return img

    def send_req(self, msg):
        """Returns response from server to request (with header)"""
        # Not used on server side

        msg = f"{len(msg):<{Connection.HEADER_SIZE}}" + msg

        self.host_socket.send(msg.encode("utf-8"))
        resp = self.receive(self.host_socket)

        self.host_socket.shutdown(socket.SHUT_RDWR)
        self.host_socket.close()

        return resp

    @staticmethod
    def format_msg(msg):
        """Formats given message to internal protocol standard"""

        f_msg = f"{len(msg):<{Connection.HEADER_SIZE}}" + msg
        return f_msg.encode("utf-8")

    def broadcast(self, info_msg):
        """Sending message to all connected users"""

        for user in Connection.active_users:
            print(f"BROADCASTING: {user} - {info_msg}")
            user_socket = Connection.active_users.get(user)
            user_socket.send(self.format_msg(info_msg))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(message)s (%(asctime)s)')
    logging.info(f"LAUNCHING SERVER at address: {Connection.IP}:{Connection.PORT}")

    # starting server
    Connection('server')
