from tkinter import Tk
import main
import view
import loading


def on_timer(ani, img, canvas):
    canvas.set_image(ani.overlay(img))
    canvas.after(ani.delay, on_timer, ani, img, canvas)


if __name__ == '__main__':
    root = Tk()
    img = main.take_screen_shot((100, 100, 300, 300))
    root.geometry('%dx%d' % (img.width, img.height))
    canvas = view.ScreenshotCanvas(root, img)
    canvas.after(0, on_timer, loading.create_loading_animation('loading.gif'), img, canvas)
    root.mainloop()
