import os
import re
import tempfile
import uuid
import logging
from functools import partial
from Tkinter import Toplevel, Tk
import tkinter
import tkFileDialog
from StringIO import StringIO
from threading import Thread
import clipboard
import win32clipboard
import yaml
from twython import Twython
from PIL import ImageTk
import event
import loading
import error
from exception import log_exception


logger = logging.getLogger(__name__)


def send_image_to_clipboard(img):
    output = StringIO()
    img.convert('RGB').save(output, 'BMP')
    data = output.getvalue()[14:]
    output.close()
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()


def get_winfo(geometry):
    """Working around by parsing the geometry since `winfo_x/y` returns 0 if the window is withdrawn"""
    regex = re.search('\d+x\d+\+(\d+)\+(\d+)', geometry)
    return int(regex.group(1)), int(regex.group(2))


def align_window_with_area(window, area):
    """
    Adjust the geometry so that the client area of the window is
    aligned with the actual area of the screen shot
    """
    winfo_x, winfo_y = get_winfo(window.geometry())
    client_x_offset = window.winfo_rootx() - winfo_x
    client_y_offset = window.winfo_rooty() - winfo_y
    window.geometry('+%d+%d' % (area.left - client_x_offset, area.top - client_y_offset))
    window.geometry('%dx%d' % (area.width, area.height))


def generate_temp_file_name():
    return os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))


class ImageFileContext(object):
    """
    Context that takes an image, saves it as a temp file and returns the file object
    It'd be better if I could just derive a BytesIO object from `image` but I can't get it to upload
    """
    def __init__(self, image):
        image_file_name = generate_temp_file_name()
        image.save(image_file_name, format='png')
        self.image_file = open(image_file_name, 'rb')

    def __enter__(self):
        return self.image_file

    def __exit__(self, *args, **kwargs):
        return self.image_file.close()


def get_api(twitter_settings):
    cfg = yaml.load(open(twitter_settings, 'rb'))
    return Twython(
        cfg['consumer_key'],
        cfg['consumer_secret'],
        cfg['access_token_key'],
        cfg['access_token_secret'])


class HiddenWindow(Toplevel):
    """Has to be `Toplevel`; Any event emitted by `Frame` is ignored"""
    def __init__(self, parent):
        Toplevel.__init__(self, parent)
        self.withdraw()


def upload_to_twitter(image, twitter_settings):
    """Upload image to twitter account"""
    api = get_api(twitter_settings)
    with ImageFileContext(image) as image_file:
        media_id = api.upload_media(media=image_file)['media_id']
    resp = api.update_status(media_ids=[media_id])
    return resp['entities']['media'][0]['display_url']


class ImageUrlRetriever(HiddenWindow):
    def __init__(self, parent, upload_image):
        HiddenWindow.__init__(self, parent)
        self.upload_image = upload_image

    def thread_proc(self):
        """
        https://mail.python.org/pipermail/python-list/2003-December/197985.html
        > The general rule is that the thread that owns the GUI can be the only one
        > that can directly manipulate the GUI (call it's functions). Sending messages
        > that the GUI thread processes is nearly always just fine since the GUI
        > thread, and it's state, are used to do the actual GUI manipulation.
        `event_generate` seems thread safe
        """
        try:
            image_url = self.upload_image()
            logging.info('image_url ' + image_url)
            clipboard.copy(image_url)
            # the event should be generated after the image url is copied
            self.event_generate(event.IMAGE_URL_RETRIEVED, when='tail')
        except:
            self.event_generate(event.IMAGE_URL_RETRIEVAL_FAILED, when='tail')
            raise

    @log_exception
    def on_upload_request(self):
        logger.info('Got upload request')
        Thread(target=self.thread_proc).start()


class CanvasImage(object):
    def __init__(self, img):
        # The original image without scaling or overlaying
        self.original = img
        # The scaled image without overlaying
        self.current = img

    def resize(self, size):
        self.current = self.original.resize(size)


class ScreenshotCanvas(tkinter.Canvas):
    def __init__(self, parent, image):
        tkinter.Canvas.__init__(self, parent)
        self.image = image
        self.pack(fill=tkinter.BOTH, expand=tkinter.YES)
        # `PhotoImage` has to be instantiated after the root object and
        # also has to persist in a variable while the event loop is running
        self.tkimage = None
        self.set_current_image()

    def set_image(self, image):
        self.tkimage = ImageTk.PhotoImage(image)
        self.create_image(0, 0, anchor='nw', image=self.tkimage)

    def set_current_image(self):
        self.set_image(self.image.current)

    def resize(self, size):
        self.image.resize(size)
        self.set_current_image()


class CanvasAnimation(HiddenWindow):
    def __init__(self, parent, animation, canvas, image):
        HiddenWindow.__init__(self, parent)
        self.animation = animation
        self.canvas = canvas
        self.image = image
        self.run_animation = False

    def play_animation(self):
        if not self.run_animation:
            logger.debug('animation ended')
            return
        frame = self.animation.overlay(self.image.current)
        logger.debug('showing frame %s' % frame)
        self.canvas.set_image(frame)
        self.after(self.animation.delay, self.play_animation)

    @log_exception
    def on_twitter_upload_finished(self):
        logger.info('Upload finished')
        self.run_animation = False
        self.canvas.set_current_image()

    def on_image_url_requested(self):
        """Animate the image to notify the user"""
        logger.info('Image url requested')
        self.run_animation = True
        self.after(0, self.play_animation)


class ViewScale(object):
    def __init__(self, orig_size):
        self.orig_size = orig_size
        self.cur_scale = 1
        self.min_scale = 0.1

    def __call__(self, diff):
        new_scale = self.cur_scale + diff * 0.1
        if new_scale < self.min_scale:
            new_scale = self.min_scale
        self.cur_scale = new_scale
        new_size = (int(self.orig_size[0] * self.cur_scale), int(self.orig_size[1] * self.cur_scale))
        return new_size


@log_exception
def on_mouse_wheel(image_view, canvas, view_scale, e):
    if e.state == 12:
        canvas.pack(fill=tkinter.BOTH, expand=tkinter.YES)
        new_size = view_scale(e.delta / 120)
        logger.debug('new_size ' + str(new_size))
        image_view.geometry('%dx%d' % new_size)
        canvas.resize(new_size)


def save_file(image):
    f = tkFileDialog.asksaveasfile(mode='w', defaultextension='.png')
    if not f:
        logger.info('save aborted')
        return
    logger.info('saving to ' + f.name)
    image.save(os.path.abspath(f.name))
    f.close()


def run_image_view(image, area, twitter_settings, loading_gif):
    image_view = Tk()
    # make sure the view has focus so that it can catch mouse/key events
    # `focus_force` implicitly moves the window so it has to be called before aligning the window
    image_view.focus_force()
    # `update` needs to be called before calculating the client area offset
    # `withdraw` should be called prior to hide the ugly default window
    image_view.wm_withdraw()
    image_view.update()
    align_window_with_area(image_view, area)
    # `deiconify` does not show the window
    image_view.wm_deiconify()
    canvas_img = CanvasImage(image)
    canvas = ScreenshotCanvas(image_view, canvas_img)
    animation = loading.create_loading_animation(loading_gif)
    canvas_animation = CanvasAnimation(image_view, animation, canvas, canvas_img)
    view_scale = ViewScale((area.width, area.height))
    image_view.bind(event.MOUSE_WHEEL, partial(on_mouse_wheel, image_view, canvas, view_scale))
    url_retriever = ImageUrlRetriever(image_view, partial(upload_to_twitter, image, twitter_settings))

    def on_upload_finished(_):
        canvas_animation.on_twitter_upload_finished()

    def on_upload_failed(_):
        on_upload_finished(_)
        error.display('Upload failed')

    url_retriever.bind(event.IMAGE_URL_RETRIEVED, on_upload_finished)
    url_retriever.bind(event.IMAGE_URL_RETRIEVAL_FAILED, on_upload_failed)
    menu = tkinter.Menu(image_view, tearoff=0)
    menu.add_command(label='Copy', command=lambda: send_image_to_clipboard(image))
    menu.add_command(label='Save', command=partial(save_file, image))
    menu.add_command(label='Upload to twitter',
                     command=lambda: image_view.event_generate(event.IMAGE_URL_REQUEST, when='tail'))
    image_view.bind(event.MOUSE_RIGHT_PRESS, lambda e: menu.post(e.x_root, e.y_root))
    image_view.bind(event.IMAGE_URL_REQUEST, lambda e: canvas_animation.on_image_url_requested(), add='+')
    image_view.bind(event.IMAGE_URL_REQUEST, lambda e: url_retriever.on_upload_request(), add='+')
    image_view.mainloop()
