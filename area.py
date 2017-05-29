import logging
from Tkinter import Tk, Toplevel
import event


logger = logging.getLogger()


class DragArea(dict):
    """
    Class that represents the area dragged by mouse
    init_pos represents the location of which the mouse was pressed
    cur_pos represents the location of which the mouse was last seen
    """
    def __init__(self, init_pos=None, cur_pos=None):
        super(DragArea, self).__init__(init_pos=init_pos, cur_pos=cur_pos)

    @property
    def left(self):
        return min(self['init_pos'][0], self['cur_pos'][0])

    @property
    def top(self):
        return min(self['init_pos'][1], self['cur_pos'][1])

    @property
    def right(self):
        return max(self['init_pos'][0], self['cur_pos'][0])

    @property
    def bottom(self):
        return max(self['init_pos'][1], self['cur_pos'][1])

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.bottom - self.top

    @property
    def bbox(self):
        return self.left, self.top, self.right, self.bottom

    @property
    def is_valid(self):
        return self.width > 0 and self.height > 0


class BackWindow(Toplevel):
    def __init__(self, parent):
        Toplevel.__init__(self, parent, cursor='cross')
        self.overrideredirect(1)
        self.attributes('-alpha', 0.01)
        # hide initially
        # setting alpha to 0 will also hide the window but to avoid confusion,
        # it's better to just stick with geometry
        self.geometry('0x0')

    def cover_screen(self):
        self.geometry('+0+0')
        resolution = (self.winfo_screenwidth(), self.winfo_screenheight())
        logger.info('resolution %dx%d' % resolution)
        self.geometry('%dx%d' % resolution)


class DragWindow(Toplevel):
    def __init__(self, parent, drag_area):
        Toplevel.__init__(self, parent)
        self.attributes('-alpha', 0.7)
        self.overrideredirect(1)
        # hide window(had problems with `deiconify()`)
        self.geometry('0x0')
        self.drag_area = drag_area

    def relocate(self, drag_area):
        self.geometry("+%d+%d" % (drag_area.left, drag_area.top))
        self.geometry("%dx%d" % (drag_area.width, drag_area.height))

    def on_back_motion(self, event):
        # make sure the mouse has been pressed
        if self.drag_area['init_pos']:
            self.drag_area['cur_pos'] = event.x, event.y
            logger.debug('%s %s' % (self.drag_area['init_pos'], self.drag_area['cur_pos']))
            self.relocate(self.drag_area)

    def on_back_press(self, event):
        self.drag_area['init_pos'] = event.x, event.y


class RootWindow(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.geometry('0x0')
        # setting geometry to 0x0 does not hide the title bar
        # so this has to be called in addition to completely hide the window
        self.overrideredirect(1)

    def on_finish(self, _):
        self.destroy()


def create_windows(drag_area):
    root = RootWindow()
    drag_window = DragWindow(root, drag_area)
    back_window = BackWindow(root)
    back_window.cover_screen()
    back_window.bind(event.MOUSE_MOVE, drag_window.on_back_motion)
    back_window.bind(event.LEFT_PRESS, drag_window.on_back_press)
    back_window.bind(event.RIGHT_CLICK, root.on_finish)
    back_window.bind(event.LEFT_RELEASE, root.on_finish)
    return root


def monitor_area():
    """
    Monitors and returns the area dragged by mouse
    :return: Area object representing the area dragged by mouse
    """
    drag_area = DragArea()
    root = create_windows(drag_area)
    logger.info('Monitoring mouse')
    root.mainloop()
    logger.info('Finished monitoring mouse')
    return drag_area
