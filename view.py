import os
import tempfile
import uuid
import logging
from Tkinter import Toplevel, Tk
import tkinter
import yaml
from twython import Twython
from PIL import ImageTk, ImageEnhance
import event
import clipboard


logger = logging.getLogger()


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
    def __init__(self, parent):
        Toplevel.__init__(self, parent)
        self.withdraw()


# Has to be `Toplevel`; Any event emitted by `Frame` is ignored
class ImageUrlRetriever(HiddenWindow):
    def __init__(self, parent, image, twitter_settings):
        HiddenWindow.__init__(self, parent)
        self.image = image
        self.twitter_settings = twitter_settings

    def upload_image(self):
        """Upload image to twitter account"""
        api = get_api(self.twitter_settings)
        with ImageFileContext(self.image) as image_file:
            media_id = api.upload_media(media=image_file)['media_id']
        resp = api.update_status(media_ids=[media_id])
        return resp['entities']['media'][0]['display_url']

    def on_upload_request(self, _):
        logger.info('Got upload request')
        image_url = self.upload_image()
        logging.info('image_url ' + image_url)
        # I should decouple this from this class but I can't seem to find a better way to do this without
        # attaching data to the event
        clipboard.copy(image_url)
        self.event_generate(event.TWITTER_UPLOAD_FINISHED, when='tail')


def birange(start, end, step):
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


def generate_flashing_animation(image):
    delay = 10
    brightnesses = birange(1, 3, 0.2)
    frames = []
    for b in brightnesses:
        f = ImageEnhance.Brightness(image.copy()).enhance(b)
        frames.append(f)
    return Animation(frames, delay)


class ScreenshotCanvas(tkinter.Canvas):
    def __init__(self, parent, image, twitter_animation):
        tkinter.Canvas.__init__(self, parent)
        self.image = image
        self.twitter_animation = twitter_animation
        self.pack(fill=tkinter.BOTH, expand=tkinter.YES)
        # `PhotoImage` has to be instantiated after the root object and
        # also has to persist in a variable while the event loop is running
        self.tkimage = None
        self.set_image(image)

    def set_image(self, image):
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

    def on_twitter_upload_finished(self, _):
        logger.info('Upload finished')
        """Animate the image to notify the user"""
        self.after(0, self.play_animation, self.twitter_animation)


def run_image_view(image, area, twitter_settings):
    image_view = Tk()
    image_view.attributes('-topmost', True)
    # window needs to be shown before calculating the client area offset
    image_view.update()
    align_window_with_area(image_view, area)
    animation = generate_flashing_animation(image)
    canvas = ScreenshotCanvas(image_view, image, animation)
    menu = tkinter.Menu(image_view, tearoff=0)
    menu.add_command(label='Upload to twitter',
                     command=lambda: image_view.event_generate(event.TWITTER_UPLOAD_REQUEST, when='tail'))
    image_view.bind(event.RIGHT_PRESS, lambda e: menu.post(e.x_root, e.y_root))
    url_retriever = ImageUrlRetriever(image_view, image, twitter_settings)
    url_retriever.bind(event.TWITTER_UPLOAD_FINISHED, canvas.on_twitter_upload_finished)
    image_view.bind(event.TWITTER_UPLOAD_REQUEST, url_retriever.on_upload_request)
    image_view.mainloop()
