import os
import uuid
import tempfile
import yaml
import logging
import logging.config
import argparse
from functools import partial
import tkMessageBox
from ctypes import windll
from tkinter import Tk
import clipboard
from twython import Twython
from PIL import ImageGrab, ImageTk
from quicklock import singleton
import area
import view
import event


logger = logging.getLogger()


def get_api(twitter_settings):
    cfg = yaml.load(open(twitter_settings, 'rb'))
    return Twython(
        cfg['consumer_key'],
        cfg['consumer_secret'],
        cfg['access_token_key'],
        cfg['access_token_secret'])


def upload_image(image_file, twitter_settings):
    """Upload image to dummy account"""
    api = get_api(twitter_settings)
    # It'd be better if I could just upload a BytesIO object but I can't get it to work
    media_id = api.upload_media(media=image_file)['media_id']
    resp = api.update_status(media_ids=[media_id])
    return resp['entities']['media'][0]['display_url']


def show_error(msg):
    # hide required tkinter root window
    root = Tk()
    root.withdraw()
    tkMessageBox.showerror('Error', msg)


def generate_temp_file_name():
    return os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))


def take_screen_shot(bbox):
    return ImageGrab.grab(bbox)


def ensure_single_instance():
    singleton('DragShare')


def configure_logging(logging_settings):
    logging.config.dictConfig(yaml.load(open(logging_settings)))


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--twitter_settings', type=str, default='twitter.yml')
    parser.add_argument('--logging_settings', type=str, default='log.conf')
    return parser.parse_args()


def on_twitter_upload(image_file_name, twitter_settings, _):
    logger.info('on_twitter_upload')
    with open(image_file_name, 'rb') as f:
        clipboard.copy(upload_image(f, twitter_settings))


def run_image_view(image_file_name, a, twitter_settings):
    image_view = Tk()
    # `PhotoImage` has to be instantiated after the root object and
    # also has to persist in a variable while the event loop is running
    tkimage = ImageTk.PhotoImage(file=image_file_name)
    view.setup_image_view(image_view, tkimage, a)
    image_view.bind(event.TWITTER_UPLOAD, partial(on_twitter_upload, image_file_name, twitter_settings))
    image_view.mainloop()


def main():
    args = get_args()

    ensure_single_instance()
    configure_logging(args.logging_settings)
    logger.info('Initiating')

    # this is required if the screen is scaled
    windll.user32.SetProcessDPIAware()

    if not os.path.exists(args.twitter_settings):
        show_error('%s does not exist' % args.twitter_settings)
        return

    a = area.monitor_area()

    if not a.is_valid:
        logger.warning('Invalid area ' + str(a))
        return

    image = take_screen_shot(a.bbox)
    image_file_name = generate_temp_file_name()
    image.save(image_file_name, format='png')
    run_image_view(image_file_name, a, args.twitter_settings)


if __name__ == '__main__':
    main()
