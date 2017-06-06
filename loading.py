from itertools import cycle
from tkinter import Tk
from PIL import ImageEnhance, Image
import view


class LoadingAnimation(object):
    def __init__(self, loading_frames):
        self.delay = 10
        self.loading_frames = loading_frames

    def overlay(self, img):
        enhanced_img = ImageEnhance.Brightness(img.copy()).enhance(3)
        enhanced_img.paste(self.loading_frames.next())
        return enhanced_img


def on_timer(ani, img, canvas):
    canvas.set_image(ani.overlay(img))
    canvas.after(10, on_timer, ani, img, canvas)


def dissect_gif(img):
    result = []
    for i in range(img.n_frames):
        img.seek(i)
        result.append(img)
    return result


if __name__ == '__main__':
    root = Tk()
    img = Image.open('base.png')
    root.geometry('%dx%d' % (img.width, img.height))
    canvas = view.ScreenshotCanvas(root, img)
    frames = dissect_gif(Image.open('loading.gif'))
    ani = LoadingAnimation(cycle(frames))
    canvas.after(0, on_timer, ani, img, canvas)
    root.mainloop()
