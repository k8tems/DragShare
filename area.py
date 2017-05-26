from functools import partial
import threading
from Tkinter import Tk
from pynput import mouse


tk = Tk()
tk.attributes('-alpha', 0.7)
tk.overrideredirect(1)
tk.attributes('-topmost', True)
# had problems with `tk.deiconify`
tk.geometry('0x0')


class Area(dict):
    @property
    def src(self):
        return min(self['press'][0], self['release'][0]), min(self['press'][1], self['release'][1])

    @property
    def dest(self):
        return max(self['press'][0], self['release'][0]), max(self['press'][1], self['release'][1])

    @property
    def width(self):
        return self.dest[0] - self.src[0]

    @property
    def height(self):
        return self.dest[1] - self.src[1]

    @property
    def bbox(self):
        return self.src[0], self.src[1], self.dest[0], self.dest[1]


def on_click(area, x, y, button, pressed):
    if pressed:
        area['press'] = x, y
    else:
        area['release'] = x, y
        # return False to end listener
        return False


def update_geometry(press, release):
    window_area = Area(press=press, release=release)
    print(window_area['press'], window_area['release'])
    tk.geometry("+%d+%d" % window_area.src)
    tk.geometry("%dx%d" % (window_area.width, window_area.height))


def on_move(drag_area, x, y):
    if 'press' in drag_area:
        update_geometry(press=drag_area['press'], release=(x, y))


def get_area():
    t = threading.Thread(target=tk.mainloop, args=())
    t.start()
    drag_area = Area()
    with mouse.Listener(on_click=partial(on_click, drag_area),
                        on_move=partial(on_move, drag_area)) as listener:
        print('ready')
        listener.join()
    print(drag_area['press'], drag_area['release'])
    tk.destroy()
    t.join()
    return drag_area
