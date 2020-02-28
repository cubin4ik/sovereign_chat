"""USER DATABASE: social-database - best practises

login/register system with an availability to scale and grow or even changing the structure

by Alejandro Suarez
2020-February"""


class User:
    """Creating user instance"""

    def __init__(self, f_name: str, l_name: str, admin: bool):
        self.f_name = f_name.lower()
        self.l_name = l_name.lower()
        self.admin = admin
        self.id = 1  # TODO: change

        # DataHandling.save_to_database("users.csv", self.id, self.f_name, self.l_name, self.admin)
        # DataHandling.save_to_database("app.csv", self.id)

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
    def save_to_database(database_path, player_id, f_name, l_name, admin):

        if database_path == "data/users.txt":
            data = f"{player_id},{f_name},{l_name},{admin}\n"

            with open(database_path, "a") as write_database:
                write_database.write(data)

    @staticmethod
    def user_exists(database_path, f_name, l_name):
        """Getting data from database"""

        with open(database_path, "r") as read_database:
            info_lines = read_database.readlines()
            for line in info_lines:
                values = line.split(",")
                if f_name.lower() in values and l_name.lower() in values:
                    return True
            return False

