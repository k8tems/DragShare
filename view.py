from tkinter import Tk, Label
from PIL import ImageTk


def create_image_view(image, area):
    root = Tk()
    root.attributes("-topmost", True)
    root.geometry('+%d+%d' % area.left_top)
    root.geometry('%dx%d' % (area.width, area.height))
    panel = Label(root, image=ImageTk.PhotoImage(image))
    panel.pack(side='bottom', fill='both', expand='yes')
    root.mainloop()
