from tkinter import Tk
from itertools import cycle
from collections import namedtuple
from PIL import Image
import view


class LoadingAnimation(object):
    def __init__(self, gif):
        self.delay = gif.delay
        self.loading_frames = cycle(gif.frames)

    def overlay(self, img):
        back_img = Image.new('RGBA', img.size, (255, 255, 255, 200))
        frame = self.loading_frames.next()
        loc = (back_img.width/2-frame.width/2, back_img.height/2-frame.height/2)
        back_img.paste(frame, loc, frame)
        base_img = img.copy()
        base_img.paste(back_img, (0, 0), back_img)
        return base_img


Gif = namedtuple('Gif', 'frames delay')


def dissect_gif(gif):
    result = []
    for i in range(1, gif.n_frames):
        result.append(gif.copy().convert('RGBA'))
        gif.seek(i)
    return Gif(result, gif.info['duration'])


def create_loading_animation(fname):
    return LoadingAnimation(dissect_gif(Image.open(fname)))


def on_timer(ani, img, canvas):
    canvas.set_image(ani.overlay(img))
    canvas.after(ani.delay, on_timer, ani, img, canvas)


if __name__ == '__main__':
    root = Tk()
    img = Image.open('base.png')
    root.geometry('%dx%d' % (img.width, img.height))
    canvas = view.ScreenshotCanvas(root, img)
    canvas.after(0, on_timer, create_loading_animation('loading.gif'), img, canvas)
    root.mainloop()
