"""USER DATABASE: social-database"""

from tkinter import *
from tkinter import messagebox
from main import User


def register(f_name, l_name):

    User(f_name, l_name, True)


root = Tk()
root.title("DATABASE")
root.geometry("300x300")
root.resizable(0, 0)
# root.minsize(width=300, height=300)

f_name_entry = Entry(root)
f_name_entry.pack()
l_name_entry = Entry(root)
l_name_entry.pack()

register_btn = Button(root, text="Register")
register_btn.bind("<Button-1>", lambda event: register(f_name_entry.get(), l_name_entry.get()))
register_btn.pack()

root.mainloop()
