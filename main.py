"""USER DATABASE: social-database - best practises

login/register system with an availability to scale and grow or even changing the structure

by Alejandro Suarez
2020-February"""


class User:
    """Creating user instance"""

    def __init__(self, user_name, user_pass, admin: bool, f_name="none", l_name="none"):
        self.user_name = user_name.lower()
        self.user_pass = user_pass
        self.f_name = f_name.lower()
        self.l_name = l_name.lower()
        self.admin = admin
        self.id = 1 + int(DataHandling.get_last_id())

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


class Admin(User):
    """Admin account of a user"""

    pass


class DataHandling:
    """Data handling: saving & spitting"""

    @staticmethod
    def save_to_database(database_path, user_id, admin, user_name, user_pass, f_name, l_name):

        if database_path == "data/users.txt":
            data = f"{user_id},{admin},{user_name},{user_pass},{f_name},{l_name}\n"

            with open(database_path, "a") as write_database:
                write_database.write(data)

    @staticmethod
    def user_exists(database_path, user_name):
        """Getting data from database"""

        with open(database_path, "r") as read_database:

            while True:
                line = read_database.readline()
                if not line:
                    break

                values_list = line.split(",")
                if user_name.lower() in values_list:
                    return True
            return False

    @staticmethod
    def get_last_id():
        """Spits the last registered user if"""

        with open("data/users.txt", "r") as rf:
            if len(rf.read()) == 0:
                return 0
            rf.seek(0)
            return rf.readlines()[-1].split(",")[0]


class Session:
    """Handles operations on sessions and controls it"""

    def __init__(self, key=None):
        if key is None:
            import random
            import time

            # TODO: check how string formatting works!
            self.key = str(random.randint(1000, 9999)) + "_t_stamp:_" + ("{:#.%df}" % (10, )).format(time.time())
            # self.key = self.key[:30]
        else:
            self.key = key

        # TODO: Check if session exists

    @staticmethod
    def check_key(key):
        """Checks if user key is registered and logged in"""

        pass
        # resp = False  # Not logged in
        # if os.path.exists("data/key.txt"):
        #     with open("data/key.txt", "r") as rf:
        #         host_socket = Connection("client")
        #         resp = bool(host_socket.send_req(rf.read()))  # Either logged in or not (True or False)

        # return resp

