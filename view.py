import tkinter
from PIL import ImageTk


def create_image_view(image, area):
    root = tkinter.Tk()
    root.attributes("-topmost", True)
    root.geometry('%dx%d' % (area.width, area.height))

    # Adjust the geometry so that the client area of the window is aligned with the actual area of the screen shot
    root.update()  # windows needs to be shown before calculating the client area offset
    x_offset = root.winfo_rootx() - root.winfo_x()
    y_offset = root.winfo_rooty() - root.winfo_y()
    root.geometry('+%d+%d' % (area.left_top[0] - x_offset, area.left_top[1] - y_offset))

    canvas = tkinter.Canvas(root)
    canvas.pack(fill=tkinter.BOTH, expand=tkinter.YES)

    # has to be stored in a variable
    photo = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, anchor='nw', image=photo)

    root.mainloop()
