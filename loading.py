from itertools import cycle
from collections import namedtuple
from PIL import Image


class LoadingAnimation(object):
    def __init__(self, gif):
        self.delay = gif.delay
        self.loading_frames = cycle(gif.frames)

    def overlay(self, img):
        front_img = Image.new('RGBA', img.size, (255, 255, 255, 200))
        frame = self.loading_frames.next()
        loc = (front_img.width/2-frame.width/2, front_img.height/2-frame.height/2)
        front_img.paste(frame, loc, frame)
        back_img = img.copy()
        back_img.paste(front_img, (0, 0), front_img)
        return back_img


Gif = namedtuple('Gif', 'frames delay')


def dissect_gif(gif):
    result = []
    for i in range(1, gif.n_frames):
        result.append(gif.copy().convert('RGBA'))
        gif.seek(i)
    return Gif(result, gif.info['duration'])


def create_loading_animation(fname):
    return LoadingAnimation(dissect_gif(Image.open(fname)))
