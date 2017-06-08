import logging
from Tkinter import Tk, Toplevel
import screeninfo
import event
from exception import log_exception


logger = logging.getLogger(__name__)


class DragArea(object):
    """
    Class that represents the area dragged by mouse
    init_pos represents the location of which the mouse was pressed
    cur_pos represents the location of which the mouse was last seen
    """
    def __init__(self, init_pos=None, cur_pos=None):
        self.init_pos = init_pos
        self.cur_pos = cur_pos

    @property
    def left(self):
        return min(self.init_pos[0], self.cur_pos[0])

    @property
    def top(self):
        return min(self.init_pos[1], self.cur_pos[1])

    @property
    def right(self):
        return max(self.init_pos[0], self.cur_pos[0])

    @property
    def bottom(self):
        return max(self.init_pos[1], self.cur_pos[1])

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
        return self.init_pos and self.cur_pos and self.width > 0 and self.height > 0


def get_screen_resolution():
    """Get total screen resolution of all monitors"""
    monitors = screeninfo.get_monitors()
    width = 0
    height = 0
    for m in monitors:
        width += m.width
        height += m.height
    return width, height


class BackWindow(Toplevel):
    def __init__(self, parent):
        Toplevel.__init__(self, parent, cursor='cross')
        self.overrideredirect(1)
        self.attributes('-alpha', 0.01)
        self.geometry('+0+0')
        resolution = get_screen_resolution()
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

    @log_exception
    def on_back_motion(self, event):
        # make sure the mouse has been pressed
        if self.drag_area.init_pos:
            self.drag_area.cur_pos = event.x, event.y
            logger.debug('%s %s' % (self.drag_area.init_pos, self.drag_area.cur_pos))
            self.relocate(self.drag_area)

    @log_exception
    def on_back_press(self, event):
        self.drag_area.init_pos = event.x, event.y


class RootWindow(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.geometry('0x0')
        # setting geometry to 0x0 does not hide the title bar
        # so this has to be called in addition to completely hide the window
        self.overrideredirect(1)

    @log_exception
    def on_finish(self, _):
        self.destroy()


def create_windows(drag_area):
    root = RootWindow()
    drag_window = DragWindow(root, drag_area)
    back_window = BackWindow(root)
    back_window.bind(event.MOUSE_MOVE, drag_window.on_back_motion)
    back_window.bind(event.MOUSE_LEFT_PRESS, drag_window.on_back_press)
    back_window.bind(event.MOUSE_RIGHT_PRESS, root.on_finish)
    back_window.bind(event.MOUSE_LEFT_RELEASE, root.on_finish)
    return root


def monitor_drag():
    """
    Monitors and returns the area dragged by mouse
    :return: `DragArea` object representing the area dragged by mouse
    """
    drag_area = DragArea()
    root = create_windows(drag_area)
    logger.info('Monitoring mouse')
    root.mainloop()
    logger.info('Finished monitoring mouse')
    return drag_area
