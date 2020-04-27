"""SNet group chat with centralized server"""

# Features:
# - Authentication system with registration option
# - Session system based on simple key generated on server side
# - User may stay logged in and launch chat automatically by local key
# - User data is stored on server side only
# - User can change his data any time
# - Thumbnail for user image (avatar) is processed on server side
# - Online users list for every user

# standard libraries
from tkinter import *
from tkinter import messagebox, filedialog
import threading
import os

# local files
from client.controller import User, Session, Chat


class Application(Frame):

    def __init__(self, master):
        super().__init__()
        self.master = master

        # If session is valid returns True, if invalid - False, if server error - 504
        session_status = Session.valid_session()

        if session_status is True:
            self.main_form()
        elif session_status == 504:
            messagebox.showinfo("SNet", "Server is not responding")
            self.master.destroy()
        else:
            self.auth_form()
            self.log_form()

    def auth_form(self):
        """Creates common widgets for login and register forms"""

        self.master.title("SNet Authorization")
        self.master.geometry("250x200")
        self.master.resizable(0, 0)
        self.master.minsize(width=250, height=200)

        self.auth_frame = Frame(self.master)
        self.auth_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

        name_lbl = Label(self.auth_frame, text="User name")
        name_lbl.grid(row=0, column=0, sticky=E)
        pass_lbl = Label(self.auth_frame, text="Password")
        pass_lbl.grid(row=1, column=0, sticky=E)

        self.user_name_entry = Entry(self.auth_frame)
        self.user_name_entry.grid(row=0, column=1)
        self.user_name_entry.bind("<Return>", lambda event: [self.auth_frame.destroy(),
                                                             self.main_form()] if Session.check_credentials(
            self.user_name_entry.get(),
            self.user_pass_entry.get()) else None)
        self.user_pass_entry = Entry(self.auth_frame, show="*")
        self.user_pass_entry.grid(row=1, column=1)
        self.user_pass_entry.bind("<Return>", lambda event: [self.auth_frame.destroy(),
                                                             self.main_form()] if Session.check_credentials(
            self.user_name_entry.get(),
            self.user_pass_entry.get()) else None)

    def log_form(self):
        """Adds login functionality to authorization form"""

        login_btn = Button(self.auth_frame, text="Login",
                           command=lambda: [self.auth_frame.destroy(), self.main_form()] if Session.check_credentials(
                               self.user_name_entry.get(),
                               self.user_pass_entry.get()) else None)

        login_btn.grid(row=2, column=1, sticky=E)

        empty_frame = Frame(self.auth_frame, height=20)
        empty_frame.grid(row=3, columnspan=2)

        create_acc_btn = Button(self.auth_frame, text="Create new account", bd=0, fg="GREY",
                                command=lambda: self.reg_form())
        create_acc_btn.grid(row=4, columnspan=2)

    def reg_form(self):
        """Creates registration pop-up form"""

        # TODO: Find how to integrate with authorization form
        master = Toplevel()
        master.title("SNet Registration")
        master.geometry("250x200")
        master.resizable(0, 0)
        master.minsize(width=250, height=200)

        reg_frame = Frame(master)
        reg_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

        name_lbl = Label(reg_frame, text="User name")
        name_lbl.grid(row=0, column=0, sticky=E)
        pass_lbl = Label(reg_frame, text="Password")
        pass_lbl.grid(row=1, column=0, sticky=E)

        user_name_entry = Entry(reg_frame)
        user_name_entry.grid(row=0, column=1)
        user_name_entry.bind("<Return>", lambda event: [master.destroy(),
                                                        messagebox.showinfo("SNet",
                                                                            "User added")] if Session.new_user_reg(
            user_name_entry.get(),
            user_pass_entry.get()) else None)
        user_pass_entry = Entry(reg_frame, show="*")
        user_pass_entry.grid(row=1, column=1)
        user_pass_entry.bind("<Return>", lambda event: [master.destroy(),
                                                        messagebox.showinfo("SNet",
                                                                            "User added")] if Session.new_user_reg(
            user_name_entry.get(),
            user_pass_entry.get()) else None)

        register_btn = Button(reg_frame, text="Register")
        register_btn.bind("<Button-1>", lambda event: [master.destroy(),
                                                       messagebox.showinfo("SNet",
                                                                           "User added")] if Session.new_user_reg(
            user_name_entry.get(),
            user_pass_entry.get()) else None)
        register_btn.grid(row=2, column=1, sticky=E)

    def main_form(self):
        """Application's main window"""

        self.user = User.from_key()
        self.avatar_path = None  # Avatar path is chosen by user in "Edit profile" by get_img() function

        self.master.title("SNet Chat")
        self.master.geometry("300x400")
        self.master.minsize(width=310, height=200)
        self.master.resizable(1, 1)

        self.standard_theme = {
            "TOP_BAR": "#54b2ff",
            "BTN_BG": "#54b2ff",
            "BTN_FG": "#fcff9c",
            "ENT_BG": "WHITE",
            "GREY": "#c7c7c7",
            "FONT": ("Arial", 12)
        }

        # GUI
        work_frame = Frame(self.master)
        work_frame.pack(fill=BOTH, expand=TRUE)

        # Create the title field with user name and logout button
        title_frame = Frame(work_frame, bg=self.standard_theme["TOP_BAR"], height=50)
        title_frame.pack(side=TOP, fill=X)
        # title_frame.pack_propagate(0)

        # background_image = PhotoImage(file="img/wallpaper.png")
        # background_label = Label(title_frame, image=background_image)
        # background_label.image = background_image
        # background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.info_frame = Frame(title_frame, bg=self.standard_theme["TOP_BAR"])
        self.info_frame.pack(side=LEFT, padx=0, pady=0)
        self.info_widget(self.info_frame)

        # avatar_pic = PhotoImage(data=self.user.avatar())
        # avatar = Button(title_frame, text="set", image=avatar_pic, bd=0, bg=self.standard_theme["BTN_BG"],
        #                 activebackground=self.standard_theme["BTN_BG"],
        #                 command=lambda: self.profile_form())
        # avatar.image = avatar_pic
        # avatar.pack(side=LEFT, padx=(20, 0), pady=10)
        #
        # name_lbl = Label(title_frame, text=self.user.user_name.capitalize(),
        #             bd=0, bg=self.standard_theme["TOP_BAR"],
        #             font=(self.standard_theme["FONT"], 10, "bold"))
        # name_lbl.pack(side=LEFT, padx=(30, 0), pady=10)

        exit_img = PhotoImage(file="img/button_exit_small.png")
        exit_btn = Button(title_frame, text="log out", image=exit_img,
                          bd=0, bg=self.standard_theme["BTN_BG"],
                          activebackground=self.standard_theme["BTN_BG"],
                          command=lambda: [Session.terminate_session(),
                                           self.chat_controller.stop_refresh(),
                                           work_frame.destroy(),
                                           self.auth_form(),
                                           self.log_form()])
        exit_btn.image = exit_img
        exit_btn.pack(side=RIGHT, padx=(20, 20), pady=10)

        list_img = PhotoImage(file="img/active_users_small.png")
        list_btn = Button(title_frame, text="active users", image=list_img, bd=0, bg=self.standard_theme["BTN_BG"],
                          activebackground=self.standard_theme["BTN_BG"],
                          command=lambda: self.active_users_form())
        list_btn.image = list_img
        list_btn.pack(side=RIGHT, padx=(20, 0), pady=10)

        # Create the bottom frame where Button to send messages is located
        ctr_frame = Frame(work_frame, height=5, bg=self.standard_theme["GREY"])
        ctr_frame.pack(fill=X, side=BOTTOM)

        # Create the frame and the box to enter message
        entry_frame = Frame(work_frame, bg=self.standard_theme["GREY"])
        entry_frame.pack(fill=X, side=BOTTOM)

        send_img = PhotoImage(file="img/button_send.png")
        send_btn = Button(entry_frame, font=10, text="send", image=send_img,
                          bd=0, bg=self.standard_theme["GREY"], activebackground=self.standard_theme["GREY"],
                          command=self.send_click)
        send_btn.image = send_img
        send_btn.pack(side=RIGHT)

        ent_text_frame = Frame(entry_frame, bg=self.standard_theme["ENT_BG"], )
        ent_text_frame.pack(fill=X, side=LEFT, expand=TRUE, pady=(5, 0), padx=(5, 0))

        self.entry_box = Text(ent_text_frame, bd=0, height=1,
                              bg=self.standard_theme["ENT_BG"], font=self.standard_theme["FONT"])
        self.entry_box.bind("<Return>", lambda event: [self.entry_box.config(state=DISABLED), self.send_press()])
        # self.entry_box.bind("<KeyRelease-Return>", lambda event: self.send_press())
        self.entry_box.pack(fill=X, side=LEFT, expand=TRUE, padx=5, pady=5)

        # Create a Chat window
        chat_frame = Frame(work_frame, bg=self.standard_theme["ENT_BG"])
        chat_frame.pack(fill=BOTH, side=BOTTOM, expand=TRUE)

        self.chat_win = Text(chat_frame, bd=0, bg=self.standard_theme["ENT_BG"], font=self.standard_theme["FONT"])
        # self.chat_win.insert(END, f"Hello, {self.user.user_name}!\n")
        self.chat_win.config(state=DISABLED)
        self.chat_win.pack(fill=BOTH, side=BOTTOM, expand=TRUE, padx=5, pady=5)

        # Starting a thread of fetching messages from server
        self.chat_controller = Chat(self.chat_win, self.user.user_name)
        refresh_thread = threading.Thread(target=self.chat_controller.refresh)
        refresh_thread.start()

        # Bind a scrollbar to the Chat window
        # self.scrollbar = Scrollbar(chat_frame, command=self.chat_win.yview, cursor="heart")
        # self.chat_win['yscrollcommand'] = self.scrollbar.set

    def info_widget(self, master):
        """Creates info in title frame"""

        self.tmp_frame = Frame(master, bg=self.standard_theme["TOP_BAR"])
        self.tmp_frame.pack(side=LEFT, padx=0, pady=0)

        avatar_pic = PhotoImage(data=self.user.avatar())
        avatar = Button(self.tmp_frame, text="set", image=avatar_pic, bd=0, bg=self.standard_theme["BTN_BG"],
                        activebackground=self.standard_theme["BTN_BG"],
                        command=lambda: self.profile_form())
        avatar.image = avatar_pic
        avatar.pack(side=LEFT, padx=(20, 0), pady=10)

        name_lbl = Label(self.tmp_frame, text=self.user.user_name.capitalize(),
                         bd=0, bg=self.standard_theme["TOP_BAR"],
                         font=(self.standard_theme["FONT"], 10, "bold"))
        name_lbl.pack(side=LEFT, padx=(30, 0), pady=10)

    def profile_form(self):
        """Settings"""

        master = Toplevel()
        master.title("SNet Active users")
        # master.geometry("250x200")
        master.resizable(0, 0)
        master.minsize(width=200, height=30)

        title_frame = Frame(master, bg="#54b2ff", height=20)
        title_frame.pack(side=TOP, fill=X)

        title_lbl = Label(title_frame, text="Profile",
                          bd=0, bg="#54b2ff",
                          font=("Arial", 10, "bold"))
        title_lbl.pack(side=LEFT, padx=(15, 0), pady=10)

        decor_frame = Frame(master, bg="#54b2ff", width=5)
        decor_frame.pack(side=LEFT, anchor=W, fill=Y, padx=(15, 0), pady=(0, 10))

        sett_frame = Frame(master)
        sett_frame.pack(side=LEFT, anchor=NW, padx=10, pady=(5, 5))

        id_lbl = Label(sett_frame, text="User ID: ")
        id_lbl.grid(row=0, column=0, sticky=E)
        name_lbl = Label(sett_frame, text="User name: ")
        name_lbl.grid(row=1, column=0, sticky=E)
        f_name_lbl = Label(sett_frame, text="First name: ")
        f_name_lbl.grid(row=2, column=0, sticky=E)
        l_name_lbl = Label(sett_frame, text="Last name: ")
        l_name_lbl.grid(row=3, column=0, sticky=E)
        admin_lbl = Label(sett_frame, text="Admin: ")
        admin_lbl.grid(row=4, column=0, sticky=E)

        user_id_info = Label(sett_frame, text=self.user.id, font=("Arial", 10, "bold"))
        user_id_info.grid(row=0, column=1, sticky=W)
        user_name_info = Label(sett_frame, text=self.user.user_name.capitalize(), font=("Arial", 10, "bold"))
        user_name_info.grid(row=1, column=1, sticky=W)
        f_name_info = Label(sett_frame, text=self.user.f_name.capitalize(), font=("Arial", 10, "bold"))
        f_name_info.grid(row=2, column=1, sticky=W)
        l_name_info = Label(sett_frame, text=self.user.l_name.capitalize(), font=("Arial", 10, "bold"))
        print(repr(self.user.l_name))
        l_name_info.grid(row=3, column=1, sticky=W)
        admin_info = Label(sett_frame, text=self.user.admin, font=("Arial", 10, "bold"))
        admin_info.grid(row=4, column=1, sticky=W)

        edit_img = PhotoImage(file="img/pencil_small.png")
        edit_btn = Button(title_frame, text="Edit", image=edit_img,
                          bd=0, bg=self.standard_theme["BTN_BG"],
                          activebackground=self.standard_theme["BTN_BG"])
        edit_btn.bind("<Button-1>", lambda event: [self.edit_profile(master),
                                                   sett_frame.destroy(),
                                                   edit_btn.destroy()
                                                   ])
        edit_btn.image = edit_img
        edit_btn.pack(side=RIGHT, padx=(20, 20), pady=10)

    def edit_profile(self, master):
        """Changes the profile form and let the user edit data"""

        edit_frame = Frame(master)
        edit_frame.pack(side=LEFT, anchor=NW, padx=10, pady=(5, 5))

        f_name_lbl = Label(edit_frame, text="First name: ")
        f_name_lbl.grid(row=0, column=0, sticky=E)
        l_name_lbl = Label(edit_frame, text="Last name: ")
        l_name_lbl.grid(row=1, column=0, sticky=E)
        avatar_lbl = Label(edit_frame, text="Profile image: ")
        avatar_lbl.grid(row=2, column=0, sticky=E)

        f_name_info = Entry(edit_frame, font=("Arial", 10))
        f_name_info.grid(row=0, column=1, sticky=W)
        f_name_info.insert(0, self.user.f_name.capitalize())
        l_name_info = Entry(edit_frame, font=("Arial", 10))
        l_name_info.grid(row=1, column=1, sticky=W)
        l_name_info.insert(0, self.user.l_name.capitalize())
        avatar_req = Button(edit_frame, text="Select image", command=lambda: [self.get_img(),
                                                                              edit_frame.focus_set(),
                                                                              avatar_req.config(
                                                                                  text=os.path.split(self.avatar_path)[
                                                                                      1])])
        avatar_req.grid(row=2, column=1, sticky=W)

        submit_btn = Button(edit_frame, text="Submit changes",
                            command=lambda: [
                                self.user.update(f_name=f_name_info.get(), l_name=l_name_info.get(),
                                                 avatar_path=self.avatar_path),
                                master.destroy(),
                                self.tmp_frame.destroy(),
                                self.info_widget(self.info_frame),
                                self.profile_form()
                            ])
        submit_btn.grid(row=3, columnspan=2, sticky=E, pady=(5, 0))

    @staticmethod
    def active_users_form():
        """Shows active users"""

        master = Toplevel()
        master.title("SNet Active users")
        # master.geometry("250x200")
        master.resizable(0, 1)
        master.minsize(width=200, height=30)

        users_list = "\n".join(Session.get_users_list().split(","))

        title_frame = Frame(master, bg="#54b2ff", height=20)
        title_frame.pack(side=TOP, fill=X)

        title_lbl = Label(title_frame, text="Users online",
                          bd=0, bg="#54b2ff",
                          font=("Arial", 10, "bold"))
        title_lbl.pack(side=LEFT, padx=(15, 0), pady=10)

        decor_frame = Frame(master, bg="#54b2ff", width=5)
        decor_frame.pack(side=LEFT, anchor=W, fill=Y, padx=(15, 0), pady=(0, 10))

        print(repr(users_list))
        user_list_lbl = Label(master, text=users_list, font=("Arial", 10), justify=LEFT)
        user_list_lbl.pack(side=LEFT, anchor=NW, padx=10, pady=(5, 5))

    def send_click(self):
        """Sends message"""

        entry_text = Chat.filter_msg(self.entry_box.get("0.0", END))

        # Send my message to all others
        self.chat_controller.send_all(entry_text)

        # if not received_by_server:
        #     entry_text = "Error sending to server.." + "\n"

        # self.chat_win.yview(END)  # Scroll to the bottom of chat windows
        self.entry_box.delete("0.0", END)  # Erase previous message in Entry Box

    def send_press(self):
        """Sends message"""

        self.entry_box.config(state=NORMAL)
        self.send_click()

    def get_img(self):
        """Suggests a user to select an image and stores it in a variable"""

        self.avatar_path = filedialog.askopenfilename(initialdir="/", title="Select file",
                                                      filetypes=(("PNG files", "*.png"), ("All files", "*.*")))

        if os.stat(self.avatar_path).st_size > 2 ** 22:
            self.avatar_path = None
            messagebox.showerror("SNet", "Image size should be less the 4 MB")


root = Tk()
# root.overrideredirect(True)
app = Application(master=root)
app.mainloop()

try:
    app.chat_controller.stop_refresh()
except AttributeError:
    pass
