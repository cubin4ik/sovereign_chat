"""Server side based on socket connection"""

# standard libraries
import socket
import threading
import logging

# local files
# DELETE "server." as a reference (it is there to run both client and server from one project directory)
from server.controller import Session
from server.controller import DataHandling

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s (%(asctime)s)')


class Connection:
    """Handles all the connections using sockets"""

    with open("config.txt", "r") as rf:
        server_ip = rf.readline().strip()
        server_port = int(rf.readline().strip())

    IP = server_ip
    PORT = server_port
    BUFF_SIZE = 2 ** 7
    BUFF_SIZE_IMG = 2 ** 22
    HEADER_SIZE = 10
    QUEUE = 5

    active_users = {}

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
                    logging.info("\nlistening..\n")
                    remote_socket, address = self.host_socket.accept()
                    logging.info(f"connection: {address}")

                    serving_thread = threading.Thread(target=self.serv_client, args=[remote_socket])
                    serving_thread.start()
            else:
                raise ValueError("You need to specify connection type: \"server\" or \"client\"")

    def serv_client(self, client_socket):
        """A thread of serving one client"""

        with client_socket:
            req = self.receive(client_socket)
            print("REQUEST TO: ", req)

            if not req:
                print(f"Connection closed by remote socket: {client_socket.getpeername()}")
            else:
                header, body = req.split("|")
                # TODO: all sending operations should consider try/except method in case client closes connection
                if header == "CHECK_KEY":
                    print(f"KEY RECEIVED: {body}")
                    resp = Session.check_key(body)
                    client_socket.send(self.format_msg(str(resp)))
                elif header == "USEREXIST":
                    print(f"CHECKING USER: {body}")
                    resp = DataHandling.user_exists(body)
                    print(f"RESULT: {resp}")
                    client_socket.send(self.format_msg(str(resp)))
                elif header == "CHECKPASS":
                    credentials = body.split(";")
                    resp = DataHandling.check_pass(*credentials)
                    client_socket.send(self.format_msg(str(resp)))
                elif header == "STARTSESS":
                    user_name = body
                    resp = Session(user_name)
                    key = resp.key[:-len(user_name)]
                    client_socket.send(self.format_msg(str(key)))
                    print(f"KEY SENT: {key}")
                elif header == "ADD_USERS":
                    user_data = body.split(";")
                    DataHandling.save_to_database(*user_data)
                elif header == "UPDATE_ME":
                    user_name, f_name, l_name = body.split(";")
                    result = DataHandling.update_database(user_name, f_name, l_name)  # TODO: Finish the response
                    client_socket.send(self.format_msg(str(result)))
                elif header == "AVATAR_ME":
                    user = body
                    reply = "SEND_IMG"
                    client_socket.send(self.format_msg(str(reply)))
                    img = self.receive_img(client_socket)
                    print("RECEIVED IMAGE: ", img)
                    result = DataHandling.save_img(user, img)
                    client_socket.send(self.format_msg(str(result)))
                elif header == "GETAVATAR":
                    user = body
                    img = DataHandling.get_avatar(user)
                    if img:
                        reply = "SENDING_IMG"
                        client_socket.send(self.format_msg(str(reply)))
                        client_socket.send(img)
                    else:
                        reply = "NOT_FOUND"
                        client_socket.send(self.format_msg(str(reply)))
                elif header == "GETLASTID":
                    resp = DataHandling.get_last_id()
                    client_socket.send(self.format_msg(resp))
                    print(f"LAST ID: {resp}")
                elif header == "DELETEKEY":
                    key = body
                    Session.terminate_session(key)
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
                    user_data = DataHandling.get_user_data(key)
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
