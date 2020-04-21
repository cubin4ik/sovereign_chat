"""USER DATABASE: social-database - best practises

login/register system with an availability to scale and grow or even changing the structure

by Alejandro Suarez
2020-February"""

# standard libraries
import os
from tkinter import messagebox
from tkinter import *

# local files
from client_v10.connection import Connection

file_paths = {
    "users": "data/users.txt",
    "key": "data/key.txt",
    "keys": "data/keys.txt"
}


class User:
    """Creating user instance"""

    def __init__(self, user_name, user_pass, admin: bool, f_name="none", l_name="none", user_id=None):
        self.user_name = user_name.lower()
        self.user_pass = user_pass
        self.f_name = f_name.lower()
        self.l_name = l_name.lower()
        self.admin = admin
        if user_id is None:
            self.id = 1 + DataHandling.get_last_id()
        else:
            self.id = user_id

    @classmethod
    def from_str(cls, name_str):
        """Creates an instance of a player using any string provided"""

        # TODO: get rid off errors
        if name_str.count("-") == 2:
            f_name, l_name, rights_lvl = name_str.split("-")
            return cls(f_name, l_name, rights_lvl)
        elif name_str.count("-") > 2:
            raise ValueError("Too many data given. Expected: first name, last name, admin")
        elif name_str.count("-") < 2:
            raise ValueError("Too little data given. Expected: first name, last name, admin")

    @classmethod
    def from_key(cls):
        """Creates user from database using just key"""

        with open(file_paths["key"], "r") as rf:
            key = rf.read()

        client = Connection()
        user_data = client.request_server(f"USER_DATA|{key}")
        data = user_data.split(",")
        print("USER DATA RECEIVED: ", data)

        return cls(user_name=data[2],
                   user_pass=None,
                   admin=data[1],
                   f_name=data[4],
                   l_name=data[5].rstrip(),
                   user_id=data[0])

    def update(self, f_name=None, l_name=None):
        """Updates user data"""

        DataHandling.update_database(self.user_name, f_name, l_name)


class Admin(User):
    """Admin account of a user"""

    pass


class DataHandling:
    """Data handling: saving & spitting"""

    @staticmethod
    def save_to_database(user_id, admin, user_name, user_pass, f_name, l_name):

        # data = f"{user_id},{admin},{user_name},{user_pass},{f_name},{l_name}\n"
        # list_data = [user_id, admin, user_name, user_pass, f_name, l_name]

        data = ";".join([str(user_id), str(admin), user_name, user_pass, f_name, l_name])

        client = Connection()
        client.request_server(f"ADD_USERS|{data}")  # Any message should start with method by 9 characters

    @staticmethod
    def update_database(user, f_name, l_name, avatar=None):
        """Updates database with given values"""

        try:
            client = Connection()
            status = client.request_server(f"UPDATE_ME|{user};{f_name};{l_name}")

            if status == "False":
                messagebox.showerror("SNet", "Could not update")
            else:
                messagebox.showinfo("SNet", "Profile updated")
        except ConnectionError:
            messagebox.showerror("SNet", "Server is not responding")
        except TimeoutError:
            messagebox.showerror("SNet", "Server dropped")

    @staticmethod
    def user_exists(user_name):
        """If user exists returns True"""

        try:
            client = Connection()
            status = client.request_server(f"USEREXIST|{user_name}")  # Any message should start with method by 9 characters

            if status == "False":
                return False
            else:
                return True
        except ConnectionError:
            messagebox.showerror("SNet", "Server is not responding")
        except TimeoutError:
            messagebox.showerror("SNet", "Server dropped")

    @staticmethod
    def get_last_id():
        """Spits the last registered user if"""

        try:
            client = Connection()
            last_id = client.request_server(f"GETLASTID|THROWAWAYSTRING")
            print(f"TYPE: {type(last_id)}, ID: {last_id}")
            return int(last_id)
        except ConnectionError:
            messagebox.showerror("SNet", "Server is not responding")
        except TimeoutError:
            messagebox.showerror("SNet", "Server dropped")

    @staticmethod
    def check_pass(user_name, user_pass):
        """Checks pair of name and password"""

        try:
            client = Connection()
            status = client.request_server(
                f"CHECKPASS|{user_name};{user_pass}")  # Any message should start with method by9 characters

            if status == "False":
                return False
            else:
                return True
        except ConnectionError:
            messagebox.showerror("SNet", "Server is not responding")
            return False
        except TimeoutError:
            messagebox.showerror("SNet", "Server dropped")
            return False


class Session:
    """Handles operations on sessions and controls it"""

    # TODO: Remove from clients side key generator
    def __init__(self, user_name, key=None):
        if key is None:
            client = Connection()
            self.key = client.request_server(f"STARTSESS|{user_name}")
            print(self.key)
            self.put_key()
        else:
            self.key = key

    def __repr__(self):
        return self.key

    @staticmethod
    def valid_session():
        """Checks if session exists, creates new if not"""

        if os.path.exists(file_paths["key"]):
            with open(file_paths["key"], "r") as rf:
                my_key = rf.read().rstrip("\n")
                try:
                    session_start = Session.check_key(my_key)
                except ConnectionError:
                    return 504
                except TimeoutError as ex:
                    messagebox.showerror("SNet", f"Server dropped:\n\n{ex}")
                    return 504
            if session_start:
                return True
            else:
                return False
        else:
            # messagebox.showerror("SNet", "Local key not found")
            return False

    @staticmethod
    def check_credentials(user_name, user_pass):
        """Checks if credentials are valid when login"""

        if user_name == "" or user_pass == "":
            messagebox.showerror("SNet", "You should enter both user name and password")
            return False

        if DataHandling.user_exists(user_name):
            print("USER IS REAL")
            if DataHandling.check_pass(user_name, user_pass):
                new_sess = Session(user_name)
                print(f"KEY CREATED: {new_sess.key}")
                return True
                # MainWindow(user_name=user_name)
            else:
                messagebox.showerror("SNet", "Incorrect password")
                return False
        else:
            messagebox.showerror("SNet", f"User doesn't exist")
            return False

    def put_key(self):
        """Puts key to keys holder"""

        with open(file_paths["key"], "w") as wf:
            wf.write(self.key)

    @staticmethod
    def new_user_reg(user_name, user_pass):
        """Check the existence. If not matches found - creates new user,
        puts data into database"""

        if user_name == "" or user_pass == "":
            messagebox.showerror("SNet", "You should enter both user name and password")
            return False

        if not DataHandling.user_exists(user_name):
            new_user = User(user_name, user_pass, False)

            DataHandling.save_to_database(new_user.id,
                                          new_user.admin,
                                          new_user.user_name,
                                          new_user.user_pass,
                                          new_user.f_name,
                                          new_user.l_name)
            return True
        else:
            messagebox.showerror("SNet", "User already exists")
            return False

    @staticmethod
    def check_key(key):
        """Checks if user key is registered and logged in"""

        try:
            client = Connection()
            status = client.request_server(f"CHECK_KEY|{key}")  # Any message should start with method by 9 characters
            if status == "False":
                return False
            else:
                return True
        except ConnectionError as ex:
            messagebox.showerror("SNet", f"Server is not responding:\n\n{ex}")
            return False
        except TimeoutError as ex:
            messagebox.showerror("SNet", f"Server dropped:\n\n{ex}")
            return False

    @staticmethod
    def terminate_session():
        """Terminates current session"""

        with open(file_paths["key"], "r") as rf:
            key = rf.read()

        try:
            client = Connection()
            client.request_server(f"DELETEKEY|{key}")  # Any message should start with method by 9 characters
            os.remove(file_paths["key"])
        except ConnectionError:
            messagebox.showerror("SNet", "Connection lost")
        except TimeoutError:
            messagebox.showerror("SNet", "Server dropped")

    @staticmethod
    def get_users_list():
        """Returns list of active users"""

        try:
            client = Connection()
            users_list = client.request_server(f"USERSLIST|DUMMY")
            return users_list
        except ConnectionError:
            messagebox.showerror("SNet", "Connection lost")
        except TimeoutError:
            messagebox.showerror("SNet", "Server dropped")


class Chat:
    """Sends and receives messages"""

    def __init__(self, chat_window, user_name):
        self.widget = chat_window
        self.client_socket = Connection()
        self.user_name = user_name.lower()
        try:
            self.client_socket.broadcast(f"STAY_ALIVE|{user_name}")
        except ConnectionError:
            messagebox.showerror("SNet", "Connection lost")
        except TimeoutError:
            messagebox.showerror("SNet", "Server dropped")

    def refresh(self):
        """Fetches all messages from server"""

        while True:
            try:
                msg_in = self.client_socket.receive_msg()
                if not msg_in:
                    # self.refresh_widget("EVENT", "Server stopped the connection")
                    # messagebox.showerror("SNet", "Server stopped the connection")
                    print("Server stopped the connection")
                    # Connection.close_connection(self.client_socket)  # TODO: Find if all sockets are closing correctly
                    break
                else:
                    header, user_name, msg = msg_in.split("|")
                    if header == "SENDALLMSG" or header == "STAY_ALIVE":
                        print(f"RECEIVED: {user_name}: {msg}")
                        self.refresh_widget(user_name, msg)
                    else:
                        print(f"Not for printing:{msg_in}", ":", header, ":", msg)
            except ConnectionError:
                messagebox.showerror("SNet", "Connection lost")
                break

    def stop_refresh(self):
        """Closes the connection"""

        self.client_socket.broadcast(f"STOPMYCHAT|DUMMY")

    def refresh_widget(self, user_name, entry_text):

        print(f"REFRESHING WIDGET:\n--{user_name}\n--{entry_text}\n")

        colors = {
            "event": "#ff6969",
            "me": "#4ed978",
            "OTHERS": "#e8b164"
        }

        if user_name.lower() == self.user_name.lower():
            user_name = "me"

        if entry_text != '':
            self.widget.config(state=NORMAL)
            if self.widget.index('end') is not None:

                line_num = float(self.widget.index('end')) - 1.0  # TODO: for reasons unknown it was in try/wxcept block

                self.widget.insert(END, f"{user_name}: {entry_text}")
                print("SHOW: ", f"{user_name}: {entry_text}")
                self.widget.tag_add(user_name, line_num, line_num + float("0." + str(len(user_name))))
                print(line_num)
                self.widget.tag_config(user_name, foreground=colors.get(user_name, "#e8b164"), font=("Arial", 12, "bold"))
                self.widget.config(state=DISABLED)
                self.widget.yview(END)

    def send_all(self, msg):

        try:
            print(type(self.client_socket))
            sent = self.client_socket.broadcast(f"SENDALLMSG|{msg}")
            print("Successfully sent:", sent)
            return True
            # if sent == "Received":
            #     return True
            # else:
            #     return False
        except ConnectionError:
            messagebox.showerror("SNet", "Connection lost")
        except TimeoutError:
            messagebox.showerror("SNet", "Server dropped")

    @staticmethod
    def filter_msg(entry_text):
        """Filter out all useless white lines at the end of a string, returns a new, beautifully filtered string"""

        filtered = ''
        for i in range(len(entry_text) - 1, -1, -1):
            if entry_text[i] != '\n':
                filtered = entry_text[0:i + 1]
                break
        for i in range(0, len(filtered), 1):
            if filtered[i] != "\n":
                return filtered[i:] + '\n'
        return ''
