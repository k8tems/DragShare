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


def on_twitter_upload(image_file, twitter_settings, _):
    logger.info('on_twitter_upload')
    clipboard.copy(upload_image(image_file, twitter_settings))


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
    # can't get this to work with BytesIO
    image.save(image_file_name, format='png')
    with open(image_file_name, 'rb') as f:
        image_view = Tk()
        # has to be instantiated after the root object and
        # also has to persist in a variable while the event loop is running
        image = ImageTk.PhotoImage(image)
        view.setup_image_view(image_view, image, a)
        image_view.bind('<<Twitter-Upload>>', partial(on_twitter_upload, f, args.twitter_settings))
        image_view.mainloop()


if __name__ == '__main__':
    main()
