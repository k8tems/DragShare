from tkinter import Tk
from PIL import ImageEnhance, Image
import view


class LoadingAnimation(object):
    def __init__(self):
        self.delay = 10

    def overlay(self, img):
        return ImageEnhance.Brightness(img.copy()).enhance(3)


def on_timer(ani, img, canvas):
    canvas.set_image(ani.overlay(img))
    canvas.after(10, on_timer, ani, img, canvas)


if __name__ == '__main__':
    root = Tk()
    img = Image.open('base.png')
    root.geometry('%dx%d' % (img.width, img.height))
    canvas = view.ScreenshotCanvas(root, img)
    ani = LoadingAnimation()
    canvas.after(0, on_timer, ani, img, canvas)
    root.mainloop()
