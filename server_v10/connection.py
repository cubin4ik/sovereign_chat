"""Server side based on socket connection"""

# standard libraries
import socket
import threading

# local libraries
from server_v10.controller import Session
from server_v10.controller import DataHandling


class Connection:
    """Handles all the connections using sockets"""

    IP = socket.gethostname()
    PORT = 8000
    BUFF_SIZE = 2 ** 7
    HEADER_SIZE = 10
    QUEUE = 5

    active_users = {}

    def __init__(self, socket_type=None):
        """Creates an endpoint using TCP/IP"""

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.host_socket:
            # self.host_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Checks an endpoint type (server or client)
            if socket_type is None or socket_type == "client":
                self.host_socket.connect((Connection.IP, Connection.PORT))  # TODO: Check if socket will be closed
            elif socket_type == "server":
                self.host_socket.bind((Connection.IP, Connection.PORT))
                self.host_socket.listen(Connection.QUEUE)
                print(f"LISTENING ON: {self.IP}:{self.PORT}")

                while True:
                    print("\nlistening..\n")
                    remote_socket, address = self.host_socket.accept()
                    print(f"connection: {address}")

                    # TODO: Add threads and joining list (KILL THREADS PROPERLY)
                    # with remote_socket:
                    serving_thread = threading.Thread(target=self.serv_client, args=[remote_socket])
                    serving_thread.start()
                    # TODO: Establishing messages headers below for protocol
                    # remote_socket.send(f"{Connection.HEADER_SIZE}".encode("utf-8"))
                    # thread = threading.Thread(target=self.serv_client, args=[remote_socket])
                    # thread.start()
            else:
                raise ValueError("You need to specify connection type: \"server\" or \"client\"")

    # TODO: Check if this method can be static
    def serv_client(self, client_socket):
        """A thread of serving one client"""

        with client_socket:
            req = self.receive(client_socket)
            print("REQUEST TO: ", req)

            if not req:
                print(f"Connection closed by remote socket: {client_socket.getpeername()}")
            else:
                header, body = req.split("|")

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
                elif header == "GETLASTID":
                    resp = DataHandling.get_last_id()
                    client_socket.send(self.format_msg(resp))
                    print(f"LAST ID: {resp}")
                elif header == "DELETEKEY":
                    key = body
                    Session.terminate_session(key)
                elif header == "STAY_ALIVE":
                    user_name = body
                    Connection.active_users[user_name] = client_socket

                    info_msg = f"SENDALLMSG|event|{user_name} has joined the chat\n"
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
                        info_msg = f"SENDALLMSG|event|{user_name} left the chat\n"

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
