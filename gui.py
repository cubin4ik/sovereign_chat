"""USER DATABASE: social-database"""

from tkinter import *
from tkinter import messagebox
from main import *


def new_user_reg(f_name, l_name):
    """Check the existence. If not matches found - creates new user,
    puts data into database"""

    if not DataHandling.user_exists("data/users.txt", f_name, l_name):
        new_user = User(f_name, l_name, False)

        DataHandling.save_to_database("data/users.txt",
                                      new_user.id,
                                      new_user.f_name,
                                      new_user.l_name,
                                      new_user.admin)
        messagebox.showinfo("SNet", "User added")
    else:
        messagebox.showerror("SNet", "User already exists")


root = Tk()
root.title("SNet")
root.geometry("300x300")
root.resizable(0, 0)
# root.minsize(width=300, height=300)

f_name_entry = Entry(root)
f_name_entry.pack()
l_name_entry = Entry(root)
l_name_entry.pack()

register_btn = Button(root, text="Register")
register_btn.bind("<Button-1>", lambda event: new_user_reg(f_name_entry.get(), l_name_entry.get()))
register_btn.pack()

root.mainloop()
