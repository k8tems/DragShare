import tkinter
from PIL import ImageTk


def create_image_view(image, area):
    root = tkinter.Tk()
    root.attributes("-topmost", True)
    root.geometry('+%d+%d' % area.left_top)
    root.geometry('%dx%d' % (area.width, area.height))

    canvas = tkinter.Canvas(root)
    canvas.pack(fill=tkinter.BOTH, expand=tkinter.YES)

    # has to be stored in a variable
    photo = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, anchor='nw', image=photo)

    root.mainloop()
