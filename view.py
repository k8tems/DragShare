import tkinter
import event


def align_window_with_area(window, area):
    """
    Adjust the geometry so that the client area of the window is
    aligned with the actual area of the screen shot
    """
    client_x_offset = window.winfo_rootx() - window.winfo_x()
    client_y_offset = window.winfo_rooty() - window.winfo_y()
    window.geometry('+%d+%d' % (area.left - client_x_offset, area.top - client_y_offset))
    window.geometry('%dx%d' % (area.width, area.height))


def setup_image_view(root, image, area):
    root.attributes('-topmost', True)

    root.update()  # window needs to be shown before calculating the client area offset
    align_window_with_area(root, area)

    canvas = tkinter.Canvas(root)
    canvas.pack(fill=tkinter.BOTH, expand=tkinter.YES)

    # has to be stored in a variable
    canvas.create_image(0, 0, anchor='nw', image=image)

    menu = tkinter.Menu(root, tearoff=0)
    menu.add_command(label='Upload to twitter',
                     command=lambda: root.event_generate(event.TWITTER_UPLOAD, when='tail'))
    root.bind(event.RIGHT_CLICK, lambda event: menu.post(event.x_root, event.y_root))
