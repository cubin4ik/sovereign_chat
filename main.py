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
        self.id = int(DataHandling.get_from_database("data/app.csv", "users")) + 1

        DataHandling.save_to_database("users.csv", self.id, self.f_name, self.l_name, self.admin)
        DataHandling.save_to_database("app.csv", self.id)

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

        if database_path == "data/users.csv":
            data = f"{player_id},{f_name},{l_name},{admin}\n"

            with open(database_path, "a") as write_database:
                write_database.write(data)

        elif database_path == "data/app.csv":
            with open(database_path, "w") as write_database:
                for line in write_database:
                    if line.split(",")[0] == "users":
                        write_database.write(f"users,{player_id}")

    @staticmethod
    def get_from_database(database_path, value):
        """Getting data from database"""

        with open(database_path, "r") as read_database:
            info = read_database.read()
            for line in info:
                if line.split(",")[0] == value:
                    return line.split(",")[1]
                else:
                    print("no data found")


# my_player = User.from_str("Alejandro-Suarez-True")
# my_player_2 = User.from_str("Regina-Sultanova-False")
#
# p_dat = my_player.__dict__.items()
# for line in p_dat:
#     print(line)
