"""USER DATABASE: social-database"""

import os
from tkinter import *
from tkinter import messagebox
from main import *
from web.connection import Connection


def check_key():
    """Checks if user key is registered and logged in"""

    resp = False  # Not logged in
    if os.path.exists("data/key.txt"):
        with open("data/key.txt", "r") as rf:
            host_socket = Connection("client")
            resp = bool(host_socket.send_req(rf.read()))  # Either logged in or not (True or False)

    return resp


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


root = Tk()
root.title("SNet")
root.geometry("250x200")
# root.resizable(0, 0)
root.minsize(width=250, height=200)

main_frame = Frame(root)
main_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

name_lbl = Label(main_frame, text="User name")
name_lbl.grid(row=0, column=0, sticky=E)
pass_lbl = Label(main_frame, text="Password")
pass_lbl.grid(row=1, column=0, sticky=E)

user_name_entry = Entry(main_frame)
user_name_entry.grid(row=0, column=1)
user_pass = Entry(main_frame, show="*")
user_pass.grid(row=1, column=1)

register_btn = Button(main_frame, text="Register")
register_btn.bind("<Button-1>", lambda event: new_user_reg(user_name_entry.get(), user_pass.get()))
register_btn.grid(row=2, column=1, sticky=E)

root.mainloop()
