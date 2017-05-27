import time
import logging
from functools import partial
import threading
from Tkinter import Tk
from pynput import mouse


logger = logging.getLogger()
drag_window = Tk()
drag_window.attributes('-alpha', 0.7)
drag_window.overrideredirect(1)
drag_window.attributes('-topmost', True)
# had problems with `deiconify()`
drag_window.geometry('0x0')


class Area(dict):
    """
    Class that represents the area dragged by mouse
    init_pos represents the location of which the mouse was pressed
    cur_pos represents the location of which the mouse was last seen
    """
    def __init__(self):
        super(Area, self).__init__(init_pos=None, cur_pos=None)

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
        return self.width >= 0 and self.height >= 0


def relocate_drag_window(drag_area):
    drag_window.geometry("+%d+%d" % drag_area.left_top)
    drag_window.geometry("%dx%d" % (drag_area.width, drag_area.height))


def on_move(drag_area, x, y):
    # make sure the mouse has been pressed
    if drag_area['init_pos']:
        drag_area['cur_pos'] = x, y
        logger.debug('%s %s' % (drag_area['init_pos'], drag_area['cur_pos']))
        relocate_drag_window(drag_area)


def on_click(area, x, y, button, pressed):
    if pressed:
        area['init_pos'] = x, y
    else:
        area['cur_pos'] = x, y
        # return False to end listener
        return False


def monitor_area():
    """
    Monitors and returns the area dragged by mouse
    This method is not thread safe
    :return: Area object representing the area dragged by mouse
    """
    logger.debug('starting thread')
    t = threading.Thread(target=drag_window.mainloop)
    t.start()
    drag_area = Area()
    with mouse.Listener(on_click=partial(on_click, drag_area),
                        on_move=partial(on_move, drag_area)) as listener:
        logger.debug('ready')
        listener.join()
    logger.debug('%s %s' % (drag_area['init_pos'], drag_area['cur_pos']))
    drag_window.destroy()
    t.join()
    # wait until the window disappears
    time.sleep(1)
    return drag_area
