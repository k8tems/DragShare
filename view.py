import os
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
from PIL import ImageTk, ImageEnhance
import event
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


def align_window_with_area(window, area):
    """
    Adjust the geometry so that the client area of the window is
    aligned with the actual area of the screen shot
    """
    client_x_offset = window.winfo_rootx() - window.winfo_x()
    client_y_offset = window.winfo_rooty() - window.winfo_y()
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
        image_url = self.upload_image()
        logging.info('image_url ' + image_url)
        clipboard.copy(image_url)
        # the event should be generated after the image url is copied
        self.event_generate(event.IMAGE_URL_RETRIEVED, when='tail')

    @log_exception
    def on_upload_request(self):
        logger.info('Got upload request')
        Thread(target=self.thread_proc).start()


class Animation(object):
    """Workaround for `iter` function that doesn't allow custom attributes"""
    def __init__(self, frames, delay):
        self.frames = frames
        self.delay = delay
        self.idx = 0

    def next(self):
        if self.idx >= len(self.frames):
            raise StopIteration()
        result = self.frames[self.idx]
        self.idx += 1
        return result


def generate_flashing_sequence(start, end, step):
    """Generate a sequence of brightness values that represent a flashing effect"""
    result = []
    i = start
    while i <= end:
        result.append(i)
        i += step
    i = end
    while i > start:
        i -= step
        result.append(i)
    return result


def generate_flashing_animation(image):
    delay = 10
    brightnesses = generate_flashing_sequence(1, 3, 0.2)
    frames = [ImageEnhance.Brightness(image.copy()).enhance(b) for b in brightnesses]
    return Animation(frames, delay)


class ScreenshotCanvas(tkinter.Canvas):
    def __init__(self, parent, image, generate_animation):
        tkinter.Canvas.__init__(self, parent)
        self.orig_image = image
        self.cur_image = self.orig_image
        self.generate_animation = generate_animation
        self.pack(fill=tkinter.BOTH, expand=tkinter.YES)
        # `PhotoImage` has to be instantiated after the root object and
        # also has to persist in a variable while the event loop is running
        self.tkimage = None
        self.set_image(image)

    def set_image(self, image):
        self.cur_image = image
        self.tkimage = ImageTk.PhotoImage(image)
        self.create_image(0, 0, anchor='nw', image=self.tkimage)

    def play_animation(self, ani):
        try:
            frame = ani.next()
            logger.debug('showing frame %s' % frame)
            self.set_image(frame)
            self.after(ani.delay, self.play_animation, ani)
        except StopIteration:
            logger.debug('animation ended')

    @log_exception
    def on_twitter_upload_finished(self, _):
        logger.info('Upload finished')
        """Animate the image to notify the user"""
        self.after(0, self.play_animation, self.generate_animation(self.cur_image))

    def resize(self, size):
        self.set_image(self.orig_image.resize(size))


class ViewScale(object):
    def __init__(self, orig_size):
        self.orig_size = orig_size
        self.cur_scale = 1

    def __call__(self, diff):
        new_scale = self.cur_scale + diff * 0.1
        if new_scale < 0.1:
            new_scale = 0.1
        logger.debug(new_scale)
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


def run_image_view(image, area, twitter_settings):
    image_view = Tk()
    # make sure the view has focus so that it can catch mouse/key events
    # `focus_force` implicitly moves the window so it has to be called before aligning the window
    image_view.focus_force()
    # window needs to be shown before calculating the client area offset
    image_view.update()
    align_window_with_area(image_view, area)
    canvas = ScreenshotCanvas(image_view, image, generate_flashing_animation)
    view_scale = ViewScale((area.width, area.height))
    image_view.bind('<MouseWheel>', partial(on_mouse_wheel, image_view, canvas, view_scale))
    url_retriever = ImageUrlRetriever(image_view, partial(upload_to_twitter, image, twitter_settings))
    url_retriever.bind(event.IMAGE_URL_RETRIEVED, canvas.on_twitter_upload_finished)
    menu = tkinter.Menu(image_view, tearoff=0)
    menu.add_command(label='Copy', command=lambda: send_image_to_clipboard(image))
    menu.add_command(label='Upload to twitter', command=url_retriever.on_upload_request)
    menu.add_command(label='Save', command=partial(save_file, image))
    image_view.bind(event.RIGHT_PRESS, lambda e: menu.post(e.x_root, e.y_root))
    image_view.mainloop()
