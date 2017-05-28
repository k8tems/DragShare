import time
import logging
from functools import partial
import threading
from Tkinter import Tk, Toplevel
from pynput import mouse


logger = logging.getLogger()


class DragArea(dict):
    """
    Class that represents the area dragged by mouse
    init_pos represents the location of which the mouse was pressed
    cur_pos represents the location of which the mouse was last seen
    """
    def __init__(self):
        super(DragArea, self).__init__(init_pos=None, cur_pos=None)

    @property
    def left_top(self):
        return min(self['init_pos'][0], self['cur_pos'][0]), min(self['init_pos'][1], self['cur_pos'][1])

    @property
    def right_bottom(self):
        return max(self['init_pos'][0], self['cur_pos'][0]), max(self['init_pos'][1], self['cur_pos'][1])

    @property
    def width(self):
        return self.right_bottom[0] - self.left_top[0]

    @property
    def height(self):
        return self.right_bottom[1] - self.left_top[1]

    @property
    def bbox(self):
        return self.left_top[0], self.left_top[1], self.right_bottom[0], self.right_bottom[1]

    @property
    def is_valid(self):
        return self.width > 0 and self.height > 0


def on_move(drag_window, drag_area, x, y):
    # make sure the mouse has been pressed
    if drag_area['init_pos']:
        drag_area['cur_pos'] = x, y
        logger.debug('%s %s' % (drag_area['init_pos'], drag_area['cur_pos']))
        drag_window.relocate(drag_area)


def on_click(area, x, y, button, pressed):
    if pressed:
        area['init_pos'] = x, y
    else:
        area['cur_pos'] = x, y
        # return False to end listener
        return False


class MonitorContext(object):
    def __init__(self, tkinter):
        self.tkinter = tkinter
        # needs to start after all the windows have been created
        self.thread = threading.Thread(target=tkinter.mainloop)
        self.thread.start()

    def __enter__(self):
        logger.debug('Entering context')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.debug('Leaving context')
        self.tkinter.destroy()
        self.thread.join()
        if exc_val:
            raise exc_val
        # wait until the drag window disappears so that it doesn't interfere with the screenshot
        # apparently, this is the only place I can do this
        time.sleep(1)
        return self


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
    def __init__(self, parent):
        Toplevel.__init__(self, parent)
        self.attributes('-alpha', 0.7)
        self.overrideredirect(1)
        # hide window(had problems with `deiconify()`)
        self.geometry('0x0')

    def relocate(self, drag_area):
        self.geometry("+%d+%d" % drag_area.left_top)
        self.geometry("%dx%d" % (drag_area.width, drag_area.height))


class RootWindow(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.geometry('0x0')
        # setting geometry to 0x0 does not hide the title bar
        # so this has to be called in addition to completely hide the window
        self.overrideredirect(1)


def monitor_area():
    """
    Monitors and returns the area dragged by mouse
    :return: Area object representing the area dragged by mouse
    """
    root = RootWindow()
    back_window = BackWindow(root)
    drag_window = DragWindow(root)
    # No windows are visible at this point so everything should be fine if something happens pre-context
    with MonitorContext(root):
        # resize the background window post-context
        # so that proper clean up is done in case something happens
        back_window.cover_screen()
        logger.info('Monitoring mouse')
        drag_area = DragArea()
        with mouse.Listener(on_click=partial(on_click, drag_area),
                            on_move=partial(on_move, drag_window, drag_area)) as listener:
            listener.join()
        logger.debug('%s %s' % (drag_area['init_pos'], drag_area['cur_pos']))
        logger.info('Finished monitoring mouse')
        return drag_area
