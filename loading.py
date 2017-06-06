from itertools import cycle
from tkinter import Tk
from PIL import ImageEnhance, Image
import view


class LoadingAnimation(object):
    def __init__(self, loading_frames):
        self.delay = 10
        self.loading_frames = loading_frames

    def overlay(self, img):
        enhanced_img = ImageEnhance.Brightness(img.copy()).enhance(5)
        frame = self.loading_frames.next()
        loc = (enhanced_img.width/2-frame.width/2, enhanced_img.height/2-frame.height/2)
        enhanced_img.paste(frame, loc, frame)
        return enhanced_img


def on_timer(ani, img, canvas):
    canvas.set_image(ani.overlay(img))
    canvas.after(10, on_timer, ani, img, canvas)


def dissect_gif(gif):
    result = []
    for i in range(gif.n_frames):
        result.append(gif.copy().convert('RGBA'))
        gif.seek(i)
    return result


def create_loading_animation(fname):
    frames = dissect_gif(Image.open(fname))
    return LoadingAnimation(cycle(frames))


if __name__ == '__main__':
    root = Tk()
    img = Image.open('base.png')
    root.geometry('%dx%d' % (img.width, img.height))
    canvas = view.ScreenshotCanvas(root, img)
    canvas.after(0, on_timer, create_loading_animation('loading.gif'), img, canvas)
    root.mainloop()
