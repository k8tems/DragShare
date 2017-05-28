import tkinter
from PIL import ImageTk
import clipboard


RIGHT_CLICK = '<Button-3>'


def align_window_with_area(window, area):
    """
    Adjust the geometry so that the client area of the window is
    aligned with the actual area of the screen shot
    """
    client_x_offset = window.winfo_rootx() - window.winfo_x()
    client_y_offset = window.winfo_rooty() - window.winfo_y()
    window.geometry('+%d+%d' % (area.left - client_x_offset, area.top - client_y_offset))
    window.geometry('%dx%d' % (area.width, area.height))


def create_image_view(image, area, upload_to_twitter):
    root = tkinter.Tk()
    root.attributes('-topmost', True)

    root.update()  # window needs to be shown before calculating the client area offset
    align_window_with_area(root, area)

    canvas = tkinter.Canvas(root)
    canvas.pack(fill=tkinter.BOTH, expand=tkinter.YES)

    # has to be stored in a variable
    photo = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, anchor='nw', image=photo)

    def copy_image_url():
        clipboard.copy(upload_to_twitter())

    menu = tkinter.Menu(root, tearoff=0)
    menu.add_command(label='Upload to twitter', command=copy_image_url)

    root.bind(RIGHT_CLICK, lambda event: menu.post(event.x_root, event.y_root))

    root.mainloop()
