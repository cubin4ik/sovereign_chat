"""USER DATABASE: social-database"""

# standard libraries
from tkinter import *
from tkinter import messagebox
import threading

# local files
from client_v10.controller import User, Session, Chat

file_paths = {
    "key": "data/key.txt"
}


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
        # self.root.resizable(0, 0)
        self.master.minsize(width=250, height=200)

        self.auth_frame = Frame(self.master)
        self.auth_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

        name_lbl = Label(self.auth_frame, text="User name")
        name_lbl.grid(row=0, column=0, sticky=E)
        pass_lbl = Label(self.auth_frame, text="Password")
        pass_lbl.grid(row=1, column=0, sticky=E)

        self.user_name_entry = Entry(self.auth_frame)
        self.user_name_entry.grid(row=0, column=1)
        self.user_name_entry.bind("<Return>", lambda event: [self.auth_frame.destroy(), self.main_form()] if Session.check_credentials(self.user_name_entry.get(),
                                                                                                                                                  self.user_pass_entry.get()) else None)
        self.user_pass_entry = Entry(self.auth_frame, show="*")
        self.user_pass_entry.grid(row=1, column=1)
        self.user_pass_entry.bind("<Return>", lambda event: [self.auth_frame.destroy(), self.main_form()] if Session.check_credentials(self.user_name_entry.get(),
                                                                                                                                                  self.user_pass_entry.get()) else None)

    def log_form(self):
        """Adds login functionality to authorization form"""

        login_btn = Button(self.auth_frame, text="Login",
                           command=lambda: [self.auth_frame.destroy(), self.main_form()] if Session.check_credentials(self.user_name_entry.get(),
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
        # self.root.resizable(0, 0)
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
                                                                   messagebox.showinfo("SNet", "User added")] if Session.new_user_reg(user_name_entry.get(),
                                                                                                                                      user_pass_entry.get()) else None)
        user_pass_entry = Entry(reg_frame, show="*")
        user_pass_entry.grid(row=1, column=1)
        user_pass_entry.bind("<Return>", lambda event: [master.destroy(),
                                                                   messagebox.showinfo("SNet", "User added")] if Session.new_user_reg(user_name_entry.get(),
                                                                                                                                      user_pass_entry.get()) else None)

        register_btn = Button(reg_frame, text="Register")
        register_btn.bind("<Button-1>", lambda event: [master.destroy(),
                                                       messagebox.showinfo("SNet", "User added")] if Session.new_user_reg(user_name_entry.get(),
                                                                                                                          user_pass_entry.get()) else None)
        register_btn.grid(row=2, column=1, sticky=E)

    def main_form(self):
        """Application's main window"""

        self.user = User.from_key()
        self.master.title("SNet Chat")
        self.master.geometry("300x400")
        self.master.minsize(width=300, height=400)
        # self.master.resizable(width=FALSE, height=FALSE)

        standard_theme = {
            "TOP_BAR": "#54b2ff",
            "BTN_BG": "#54b2ff",
            "BTN_FG": "#fcff9c",
            "ENT_BG": "WHITE",
            "GREY": "#c7c7c7",
            "FONT": "Arial"
        }

        # GUI
        work_frame = Frame(self.master)
        work_frame.pack(fill=BOTH, expand=TRUE)

        # Create the title field with user name and logout button
        title_frame = Frame(work_frame, bg=standard_theme["TOP_BAR"], height=50)
        title_frame.pack(side=TOP, fill=X)
        # title_frame.pack_propagate(0)

        # background_image = PhotoImage(file="img/wallpaper.png")
        # background_label = Label(title_frame, image=background_image)
        # background_label.image = background_image
        # background_label.place(x=0, y=0, relwidth=1, relheight=1)

        avatar_pic = PhotoImage(file=r"img/avatar_blank_small.png")
        avatar = Button(title_frame, text="set", image=avatar_pic, bd=0, bg=standard_theme["BTN_BG"],
                        activebackground=standard_theme["BTN_BG"],
                        command=lambda: self.setting_form())
        avatar.image = avatar_pic
        avatar.pack(side=LEFT, padx=(20, 0), pady=10)

        lbl = Label(title_frame, text=self.user.user_name.capitalize(),
                    bd=0, bg=standard_theme["TOP_BAR"],
                    font=(standard_theme["FONT"], "10", "bold"))
        lbl.pack(side=LEFT, padx=(30, 0), pady=10)

        exit_img = PhotoImage(file="img/button_exit_small.png")
        exit_btn = Button(title_frame, text="log out", image=exit_img,
                          bd=0, bg=standard_theme["BTN_BG"],
                          activebackground=standard_theme["BTN_BG"],
                          command=lambda: [Session.terminate_session(),
                                           self.chat_controller.stop_refresh(),
                                           work_frame.destroy(),
                                           self.auth_form(),
                                           self.log_form()])
        exit_btn.image = exit_img
        exit_btn.pack(side=RIGHT, padx=(20, 20), pady=10)

        list_img = PhotoImage(file="img/active_users_small.png")
        list_btn = Button(title_frame, text="active users", image=list_img, bd=0, bg=standard_theme["BTN_BG"],
                          activebackground=standard_theme["BTN_BG"],
                          command=lambda: self.active_users_form())
        list_btn.image = list_img
        list_btn.pack(side=RIGHT, padx=(20, 0), pady=10)

        # Create the bottom frame where Button to send messages is located
        ctr_frame = Frame(work_frame, height=5, bg=standard_theme["GREY"])
        ctr_frame.pack(fill=X, side=BOTTOM)

        # Create the frame and the box to enter message
        entry_frame = Frame(work_frame, bg=standard_theme["GREY"])
        entry_frame.pack(fill=X, side=BOTTOM)

        send_img = PhotoImage(file="img/button_send.png")
        send_btn = Button(entry_frame, font=10, text="send", image=send_img,
                          bd=0, bg=standard_theme["GREY"], activebackground=standard_theme["GREY"],
                          command=self.send_click)
        send_btn.image = send_img
        send_btn.pack(side=RIGHT)

        ent_text_frame = Frame(entry_frame, bg=standard_theme["ENT_BG"], )
        ent_text_frame.pack(fill=X, side=LEFT, expand=TRUE, pady=(5, 0), padx=(5, 0))

        self.entry_box = Text(ent_text_frame, bd=0, height=1,
                              bg=standard_theme["ENT_BG"], font=standard_theme["FONT"])
        self.entry_box.bind("<Return>", lambda event: [self.entry_box.config(state=DISABLED), self.send_press()])
        # self.entry_box.bind("<KeyRelease-Return>", lambda event: self.send_press())
        self.entry_box.pack(fill=X, side=LEFT, expand=TRUE, padx=5, pady=5)

        # Create a Chat window
        chat_frame = Frame(work_frame, bg=standard_theme["ENT_BG"])
        chat_frame.pack(fill=BOTH, side=BOTTOM, expand=TRUE)

        self.chat_win = Text(chat_frame, bd=0, bg=standard_theme["ENT_BG"], font=standard_theme["FONT"])
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

    def setting_form(self):
        """Settings"""

        master = Toplevel()
        master.title("SNet Settings")
        master.geometry("250x200")
        # self.root.resizable(0, 0)
        master.minsize(width=250, height=200)

        sett_frame = Frame(master)
        sett_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

        name_lbl = Label(sett_frame, text="User name: ")
        name_lbl.grid(row=0, column=0, sticky=E)
        f_name_lbl = Label(sett_frame, text="First name: ")
        f_name_lbl.grid(row=1, column=0, sticky=E)
        l_name_lbl = Label(sett_frame, text="Last name: ")
        l_name_lbl.grid(row=2, column=0, sticky=E)
        admin_lbl = Label(sett_frame, text="Admin: ")
        admin_lbl.grid(row=3, column=0, sticky=E)

        user_name_info = Label(sett_frame, text=self.user.user_name)
        user_name_info.grid(row=0, column=1, sticky=W)
        f_name_info = Label(sett_frame, text=self.user.f_name)
        f_name_info.grid(row=1, column=1, sticky=W)
        l_name_info = Label(sett_frame, text=self.user.l_name)
        print(repr(self.user.l_name))
        l_name_info.grid(row=2, column=1, sticky=W)
        admin_info = Label(sett_frame, text=self.user.admin)
        admin_info.grid(row=3, column=1, sticky=W)

    @staticmethod
    def active_users_form():
        """Shows active users"""

        master = Toplevel()
        master.title("SNet Active users")
        master.geometry("250x200")
        master.resizable(0, 1)
        master.minsize(width=200, height=200)

        users_list = "\n".join(Session.get_users_list().split(","))

        title_lbl = Label(master, text="Users online:", font=12, justify=LEFT)
        title_lbl.pack(side=TOP, anchor=W, padx=10, pady=(5, 5))

        print(repr(users_list))
        user_list_lbl = Label(master, text=users_list, font=10, justify=LEFT)
        user_list_lbl.pack(side=TOP, anchor=W, padx=10, pady=(5, 5))

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


root = Tk()
# root.overrideredirect(True)
app = Application(master=root)
app.mainloop()
app.chat_controller.stop_refresh()
