from tkinter import filedialog
from tkinter import *
from PIL import Image

root = Tk()
root.filename = filedialog.askopenfilename(initialdir="/", title="Select file",
                                           filetypes=(("jpeg files", "*.jpg"), ("all files", "*.*")))
print(root.filename)
