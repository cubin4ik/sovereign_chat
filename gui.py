"""USER DATABASE: social-database"""

import os
from tkinter import *
from tkinter import messagebox
from main import *


class EnterForm:
    """Creates login and registration form"""

    def __init__(self, form_type=None):
        self.root = Tk()
        self.root.title("SNet")
        self.root.geometry("250x200")
        # self.root.resizable(0, 0)
        self.root.minsize(width=250, height=200)

        self.main_frame = Frame(self.root)
        self.main_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

        name_lbl = Label(self.main_frame, text="User name")
        name_lbl.grid(row=0, column=0, sticky=E)
        pass_lbl = Label(self.main_frame, text="Password")
        pass_lbl.grid(row=1, column=0, sticky=E)

        self.user_name_entry = Entry(self.main_frame)
        self.user_name_entry.grid(row=0, column=1)
        self.user_pass_entry = Entry(self.main_frame, show="*")
        self.user_pass_entry.grid(row=1, column=1)

        if not form_type or form_type.lower() == "log":
            self.log_form()
        elif form_type.lower() == "reg":
            self.reg_form()
        else:
            raise ValueError("Check the form type")

        self.root.mainloop()

    def reg_form(self):
        """Creates registration buttons"""

        register_btn = Button(self.main_frame, text="Register")
        register_btn.bind("<Button-1>", lambda event: [new_user_reg(self.user_name_entry.get(), self.user_pass_entry.get()),
                                                       self.root.destroy()])
        register_btn.grid(row=2, column=1, sticky=E)

    def log_form(self):
        """Creates login buttons"""

        login_btn = Button(self.main_frame, text="Login")
        login_btn.grid(row=2, column=1, sticky=E)

        empty_frame = Frame(self.main_frame, height=20)
        empty_frame.grid(row=3, columnspan=2)

        create_acc_btn = Button(self.main_frame, text="Create new account", bd=0, fg="GREY",
                                command=lambda: EnterForm("reg"))
        create_acc_btn.grid(row=4, columnspan=2)


def create_new_session():
    new_sess = Session()
    new_sess.put_key(new_sess.key)
    with open("data/key.txt", "w") as wf:
        wf.write(new_sess.key)


def new_user_reg(user_name, user_pass):
    """Check the existence. If not matches found - creates new user,
    puts data into database"""

    if not DataHandling.user_exists("data/users.txt", user_name):
        new_user = User(user_name, user_pass, False)

        DataHandling.save_to_database("data/users.txt",
                                      new_user.id,
                                      new_user.admin,
                                      new_user.user_name,
                                      new_user.user_pass,
                                      new_user.f_name,
                                      new_user.l_name)
        messagebox.showinfo("SNet", "User added")
    else:
        messagebox.showerror("SNet", "User already exists")


if os.path.exists("data/key.txt"):
    with open("data/key.txt", "r") as rf:
        my_key = rf.read().rstrip("\n")
        session_stat = Session.check_key(my_key)
    if session_stat:
        print(f"System entered")  # TODO: enter the system
    else:
        EnterForm("log")  # TODO: Spit registration form and only then create session
else:
    EnterForm("log")  # TODO: Spit registration form and only then create session

