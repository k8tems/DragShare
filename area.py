import logging
from functools import partial
import threading
from Tkinter import Tk
from pynput import mouse


logger = logging.getLogger()
tk = Tk()
tk.attributes('-alpha', 0.7)
tk.overrideredirect(1)
tk.attributes('-topmost', True)
# had problems with `tk.deiconify`
tk.geometry('0x0')


class Area(dict):
    def __init__(self):
        super(Area, self).__init__(init_pos=None, cur_pos=None)

    @property
    def src(self):
        return min(self['init_pos'][0], self['cur_pos'][0]), min(self['init_pos'][1], self['cur_pos'][1])

    @property
    def dest(self):
        return max(self['init_pos'][0], self['cur_pos'][0]), max(self['init_pos'][1], self['cur_pos'][1])

    @property
    def width(self):
        return self.dest[0] - self.src[0]

    @property
    def height(self):
        return self.dest[1] - self.src[1]

    @property
    def bbox(self):
        return self.src[0], self.src[1], self.dest[0], self.dest[1]


def on_click(area, x, y, button, init_posed):
    if init_posed:
        area['init_pos'] = x, y
    else:
        area['cur_pos'] = x, y
        # return False to end listener
        return False


def update_geometry(drag_area):
    tk.geometry("+%d+%d" % drag_area.src)
    tk.geometry("%dx%d" % (drag_area.width, drag_area.height))


def on_move(drag_area, x, y):
    if drag_area['init_pos']:
        drag_area['cur_pos'] = x, y
        print(drag_area['init_pos'], drag_area['cur_pos'])
        update_geometry(drag_area)


def get_area():
    logger.debug('starting thread')
    t = threading.Thread(target=tk.mainloop, args=())
    t.start()
    drag_area = Area()
    with mouse.Listener(on_click=partial(on_click, drag_area),
                        on_move=partial(on_move, drag_area)) as listener:
        logger.debug('ready')
        listener.join()
    logger.debug('%s %s' % (drag_area['init_pos'], drag_area['cur_pos']))
    tk.destroy()
    t.join()
    return drag_area
