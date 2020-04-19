from tkinter import *

root = Tk()
root.title("SNet Chat")
root.geometry("400x500")
root.minsize(width=300, height=400)

work_frame = Frame(root, bg="YELLOW")
work_frame.pack(fill=BOTH, expand=TRUE)

title_frame = Frame(work_frame, bg="BLUE", height=50)
title_frame.pack(side=TOP, fill=X)

lbl = Label(title_frame, text="Cubin4ik")
lbl.pack(side=LEFT)

set_img = PhotoImage(file="../client_v10/img/gear_small.png")
btn_send = Button(title_frame, text="Send", image=set_img, bd=0, bg="RED")
btn_send.pack(side=RIGHT)
# btn_send.pack_propagate(0)

set_img = PhotoImage(file="../client_v10/img/gear_small.png")
btn_send = Button(title_frame, text="Send", image=set_img, bd=0, bg="RED")
btn_send.pack(side=RIGHT)

ctr_frame = Frame(work_frame, bg="RED", height=50)
ctr_frame.pack(fill=X, side=BOTTOM)


btn_send = Button(ctr_frame, text="Send", image=set_img, bd=0, bg="RED")
btn_send.pack(side=RIGHT)
# btn_send.pack_propagate(0)

msg_frame = Frame(work_frame, bg="GREY", height=100)
msg_frame.pack(fill=X, side=BOTTOM)
msg_frame.pack_propagate(0)

ent = Entry(msg_frame)
ent.pack(fill=BOTH, side=LEFT, expand=TRUE)

chat_frame = Frame(work_frame, bg="WHITE")
chat_frame.pack(fill=BOTH, side=BOTTOM, expand=TRUE)

chat_win = Text(chat_frame)
chat_win.pack(fill=BOTH, side=BOTTOM, expand=TRUE)

root.mainloop()