"""USER DATABASE: social-database - best practises

login/register system with an availability to scale and grow or even changing the structure

by Alejandro Suarez
2020-February"""

# standard libraries
import os
import random
import time
from PIL import Image, ImageDraw

file_paths = {
    "data": "data",
    "users": "data/users.txt",
    "keys": "data/keys.txt",
    "avatars": "img/avatars",
    "thumbnails": "img/avatars/thumb"
}

img_size = {
    "thumbnail": (30, 30)
}


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

        # TODO: Create a method that prepares and creates all directories and files upfront the server starts
        if not os.path.exists(file_paths["data"]):
            os.mkdir(file_paths["data"])
            open(file_paths["users"], "w").close()

        data = f"{user_id},{admin},{user_name},{user_pass},{f_name},{l_name}\n"

        with open(file_paths["users"], "a") as write_database:
            write_database.write(data)

    @staticmethod
    def update_database(user, f_name, l_name, avatar=None):
        """Updates database"""

        if f_name == "":
            f_name = "None"
        if l_name == "":
            l_name = "None"

        if not os.path.exists(file_paths["data"]):
            os.mkdir(file_paths["data"])
            open("data/users.txt", "w").close()
            open("data/users_tmp.txt", "w").close()

        if os.path.exists("data/users_tmp.txt"):
            os.remove("data/users_tmp.txt")

        # TODO: Test on multiple simultaneous connection to file
        with open("data/users.txt", "r") as rf:
            with open("data/users_tmp.txt", "a") as wf:

                while True:
                    line = rf.readline().strip()
                    if not line:
                        break
                    line_updated = line
                    user_data = line.split(",")
                    if user.lower() == user_data[2]:
                        user_data[4] = f_name
                        user_data[5] = l_name
                        line_updated = ",".join(user_data)
                        print("DATA TO UPDATE: ", line_updated)
                    wf.write(line_updated + "\n")

        with open("data/users_tmp.txt", "r") as rf:
            with open("data/users.txt", "w") as wf:

                while True:
                    line = rf.readline()
                    if not line:
                        break
                    wf.write(line)

        os.remove("data/users_tmp.txt")

    @staticmethod
    def save_img(user, img):
        """Saves given image to database folder img/avatars"""

        if not os.path.exists(file_paths["avatars"]):
            os.makedirs(file_paths["avatars"])

        file_name = user + ".png"
        avatar_path = os.path.join(file_paths["avatars"], file_name)

        with open(avatar_path, "wb") as wf:
            wf.write(img)

        if not os.path.exists(file_paths["thumbnails"]):
            os.makedirs(file_paths["thumbnails"])

        thumb_path = os.path.join(file_paths["thumbnails"], file_name)
        pil_img = Image.open(avatar_path)
        pil_img.thumbnail(img_size["thumbnail"])
        pil_img_round_corner = ImageProcessor.add_corners(pil_img, 15)
        pil_img_round_corner.save(thumb_path)

        return True

    @staticmethod
    def get_avatar(user):
        """Returns avatar picture from database"""

        file_name = user + ".png"
        avatar_path = os.path.join(file_paths["thumbnails"], file_name)

        if os.path.exists(avatar_path):
            with open(avatar_path, "rb") as rf:
                print("AVATAR FOUND FOR: ", user)
                img = rf.read()
                return img
        else:
            print("AVATAR NOT FOUND: ", user)
            return False

    @staticmethod
    def user_exists(user_name):
        """If user exists returns True"""

        if not os.path.exists(file_paths["data"]):
            os.mkdir(file_paths["data"])
            open(file_paths["users"], "w").close()

        with open(file_paths["users"], "r") as read_database:

            while True:
                line = read_database.readline()
                if not line:
                    break

                values_list = line.split(",")
                if user_name.lower() == values_list[2]:
                    return True
            return False

    @staticmethod
    def get_last_id():
        """Spits the last registered user if"""

        if not os.path.exists(file_paths["data"]):
            os.mkdir(file_paths["data"])
            open(file_paths["users"], "w").close()

        with open(file_paths["users"], "r") as rf:
            if len(rf.read()) == 0:
                return str(0)
            rf.seek(0)
            return rf.readlines()[-1].split(",")[0]

    @staticmethod
    def check_pass(user_name, user_pass):
        """Checks pair of name and password"""

        if not os.path.exists(file_paths["data"]):
            os.mkdir(file_paths["data"])
            open(file_paths["users"], "w").close()

        with open(file_paths["users"], "r") as rf:
            creds = rf.readline()

            while creds:
                creds_list = creds.strip().split(",")
                if user_name.lower() == creds_list[2] and user_pass == creds_list[3]:
                    print("SUCCESS")
                    return True

                creds = rf.readline()

        return False

    @staticmethod
    def get_user_data(key):
        """Returns non sensitive data about user"""

        if not os.path.exists(file_paths["data"]):
            os.mkdir(file_paths["data"])
            open(file_paths["keys"], "w").close()
            open(file_paths["users"], "w").close()

        with open(file_paths["keys"], "r") as rf:
            line = rf.readline()

            while line:
                if key in line:
                    user = line[len(key):].rstrip()
                    print(f"USER FOUND FROM KEY: {user}")
                    break
                line = rf.readline()

        with open(file_paths["users"], "r") as rf:
            user_data = rf.readline()
            print("SEARCHING FOR USER DATA: ", user)

            while user_data:
                if user_data.split(",")[2] == user:
                    print(f"DATA: {user_data} | {user}")
                    return user_data

                user_data = rf.readline()


class Session:
    """Handles operations on sessions and controls it"""

    def __init__(self, user_name, key=None):
        if key is None:
            # TODO: check how string formatting works!
            self.key = str(random.randint(0, 9999)).zfill(4) + "_t_stamp:_" + ("{:#.%df}" % (10, )).format(time.time()) + user_name.lower()
            # self.key = self.key[:30]
            self.put_key()
        else:
            self.key = key
            self.put_key()

    def put_key(self):
        """Puts key to keys holder"""

        if not os.path.exists(file_paths["data"]):
            os.mkdir(file_paths["data"])
            open(file_paths["keys"], "w").close()

        with open(file_paths["keys"], "a") as wf:
            wf.write(self.key + "\n")

    @staticmethod
    def check_key(key):
        """Checks if user key is registered and logged in"""

        if not os.path.exists(file_paths["data"]):
            os.mkdir(file_paths["data"])
            open(file_paths["keys"], "w").close()

        if os.path.exists(file_paths["keys"]):
            with open(file_paths["keys"], "r") as rf:
                check_key = rf.readline().rstrip("\n")

                while check_key:
                    if key in check_key:
                        return True
                    check_key = rf.readline().rstrip("\n")

        return False

    @staticmethod
    def terminate_session(key):
        """Deletes key of terminated session"""

        if not os.path.exists(file_paths["data"]):
            os.mkdir(file_paths["data"])
            open(file_paths["keys"], "w").close()

        with open(file_paths["keys"], "r") as wf:

            while True:
                key_line = wf.readline()

                if not key_line:
                    break
                # TODO: Find how to remove a specific line in a file
                if key_line == key:
                    pass


class ImageProcessor:
    """Processes images"""

    @staticmethod
    def add_corners(im, rad):
        circle = Image.new('L', (rad * 2, rad * 2), 0)
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
        alpha = Image.new('L', im.size, 255)
        w, h = im.size
        alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
        alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
        alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
        alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
        im.putalpha(alpha)
        return im

