"""USER DATABASE: social-database"""

import os
from tkinter import *
from tkinter import messagebox
from main import *


file_paths = {
    "key": "data/key.txt"
}


class EnterForm:
    """Creates login and registration form"""

    def __init__(self, form_type=None):
        self.root = Tk()
        self.root.title("SNet Authorization")
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

        login_btn = Button(self.main_frame, text="Login",
                           command=lambda: check_credentials(self.user_name_entry.get(), self.user_pass_entry.get()))
        login_btn.grid(row=2, column=1, sticky=E)

        empty_frame = Frame(self.main_frame, height=20)
        empty_frame.grid(row=3, columnspan=2)

        create_acc_btn = Button(self.main_frame, text="Create new account", bd=0, fg="GREY",
                                command=lambda: EnterForm("reg"))
        create_acc_btn.grid(row=4, columnspan=2)


class MainWindow:
    """Starts the application"""

    def __init__(self):
        root = Tk()
        root.title("SNet")
        root.mainloop()


def create_new_session():
    new_sess = Session()
    new_sess.put_key(new_sess.key)
    with open(file_paths["key"], "w") as wf:
        wf.write(new_sess.key)


def check_credentials(user_name, user_pass):
    """Checks if credentials are valid when login"""

    if DataHandling.user_exists(user_name):
        if DataHandling.check_pass(user_name, user_pass):
            messagebox.showinfo("SNet", f"Hello, {user_name}")
            MainWindow()
            create_new_session()
        else:
            messagebox.showerror("SNet", "Incorrect password")
    else:
        messagebox.showerror("SNet", f"User doesn't exist")


def new_user_reg(user_name, user_pass):
    """Check the existence. If not matches found - creates new user,
    puts data into database"""

    if not DataHandling.user_exists(user_name):
        new_user = User(user_name, user_pass, False)

        DataHandling.save_to_database(new_user.id,
                                      new_user.admin,
                                      new_user.user_name,
                                      new_user.user_pass,
                                      new_user.f_name,
                                      new_user.l_name)
        messagebox.showinfo("SNet", "User added")
    else:
        messagebox.showerror("SNet", "User already exists")


if os.path.exists(file_paths["key"]):
    with open(file_paths["key"], "r") as rf:
        my_key = rf.read().rstrip("\n")
        session_stat = Session.check_key(my_key)
    if session_stat:
        MainWindow()
    else:
        EnterForm("log")  # TODO: Create session after login
else:
    EnterForm("log")  # TODO: Create session after login

