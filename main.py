"""USER DATABASE: social-database - best practises

login/register system with an availability to scale and grow or even changing the structure

by Alejandro Suarez
2020-February"""

import os
import random
import time

file_paths = {
    "users": "data/users.txt",
    "key": "data/key.txt",
    "keys": "data.keys.txt"
}


class User:
    """Creating user instance"""

    def __init__(self, user_name, user_pass, admin: bool, f_name="none", l_name="none"):
        self.user_name = user_name.lower()
        self.user_pass = user_pass
        self.f_name = f_name.lower()
        self.l_name = l_name.lower()
        self.admin = admin
        self.id = 1 + DataHandling.get_last_id()

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
    def save_to_database(user_id, admin, user_name, user_pass, f_name, l_name):

        data = f"{user_id},{admin},{user_name},{user_pass},{f_name},{l_name}\n"

        with open(file_paths["users"], "a") as write_database:
            write_database.write(data)

    @staticmethod
    def user_exists(user_name):
        """If user exists returns True"""

        with open(file_paths["users"], "r") as read_database:

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

        with open(file_paths["users"], "r") as rf:
            if len(rf.read()) == 0:
                return 0
            rf.seek(0)
            return int(rf.readlines()[-1].split(",")[0])

    @staticmethod
    def check_pass(user_name, user_pass):
        """Checks pair of name and password"""

        with open(file_paths["users"], "r") as rf:
            creds = rf.readline()

            while creds:
                creds_list = creds.strip().split(",")
                if user_name == creds_list[2] and user_pass == creds_list[3]:
                    print("SUCCESS")
                    return True

                creds = rf.readline()

        return False


class Session:
    """Handles operations on sessions and controls it"""

    def __init__(self, key=None):
        if key is None:

            # TODO: check how string formatting works!
            self.key = str(random.randint(0, 9999)).zfill(4) + "_t_stamp:_" + ("{:#.%df}" % (10, )).format(time.time())
            # self.key = self.key[:30]
        else:
            self.key = key

    @staticmethod
    def put_key(key):
        """Puts key to keys holder"""

        with open(file_paths["keys"], "a") as wf:
            wf.write(key + "\n")

    @staticmethod
    def check_key(key):
        """Checks if user key is registered and logged in"""

        if os.path.exists(file_paths["keys"]):
            with open(file_paths["keys"], "r") as rf:
                check_key = rf.readline().rstrip("\n")

                while check_key:
                    if check_key == key:
                        return True
                    check_key = rf.readline().rstrip("\n")

        return False

