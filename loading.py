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
        frame = self.loading_frames.next()
        enhanced_img.paste(frame, (0, 0), frame)
        return enhanced_img


def on_timer(ani, img, canvas):
    canvas.set_image(ani.overlay(img))
    canvas.after(10, on_timer, ani, img, canvas)


def dissect_gif(gif):
    result = []
    for i in range(gif.n_frames):
        gif.copy().save('a/%d.png' % i)
        result.append(gif.copy().convert('RGBA'))
        gif.seek(i)
    return result


if __name__ == '__main__':
    root = Tk()
    img = Image.open('base.png')
    img = img.convert('RGBA')
    root.geometry('%dx%d' % (img.width, img.height))
    canvas = view.ScreenshotCanvas(root, img)
    gif = Image.open('loading2.gif')
    frames = dissect_gif(gif)
    ani = LoadingAnimation(cycle(frames))
    canvas.after(0, on_timer, ani, img, canvas)
    root.mainloop()
