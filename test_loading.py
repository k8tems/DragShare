from tkinter import Tk
from PIL import Image
import view
import main
import loading


def on_timer(ani, img, canvas):
    canvas.set_image(ani.overlay(img))
    canvas.after(ani.delay, on_timer, ani, img, canvas)


def create_loading_animation(fname):
    return loading.LoadingAnimation(loading.dissect_gif(Image.open(fname)))


if __name__ == '__main__':
    root = Tk()
    img = main.take_screen_shot((100, 100, 300, 300))
    root.geometry('%dx%d' % (img.width, img.height))
    canvas = view.ScreenshotCanvas(root, img)
    canvas.after(0, on_timer, create_loading_animation('loading.gif'), img, canvas)
    root.mainloop()
