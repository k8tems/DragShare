from itertools import cycle
from PIL import ImageEnhance, Image
from collections import namedtuple


class LoadingAnimation(object):
    def __init__(self, gif):
        self.delay = gif.delay
        self.loading_frames = cycle(gif.frames)

    def overlay(self, img):
        enhanced_img = ImageEnhance.Brightness(img.copy()).enhance(4)
        frame = self.loading_frames.next()
        loc = (enhanced_img.width/2-frame.width/2, enhanced_img.height/2-frame.height/2)
        enhanced_img.paste(frame, loc, frame)
        return enhanced_img


Gif = namedtuple('Gif', 'frames delay')


def dissect_gif(gif):
    result = []
    for i in range(1, gif.n_frames):
        result.append(gif.copy().convert('RGBA'))
        gif.seek(i)
    return Gif(result, gif.info['duration'])


def create_loading_animation(fname):
    return LoadingAnimation(dissect_gif(Image.open(fname)))
