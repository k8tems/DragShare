import os
import uuid
import tempfile
import yaml
import logging
import logging.config
import argparse
import tkMessageBox
from tkinter import Tk
from twython import Twython
from PIL import ImageGrab
from quicklock import singleton
import area


logger = logging.getLogger()


def get_api(twitter_settings):
    cfg = yaml.load(open(twitter_settings, 'rb'))
    return Twython(
        cfg['consumer_key'],
        cfg['consumer_secret'],
        cfg['access_token_key'],
        cfg['access_token_secret'])


def share_image(image_file, twitter_settings):
    api = get_api(twitter_settings)
    media_id = api.upload_media(media=image_file)['media_id']
    api.update_status(media_ids=[media_id])


def show_error(msg):
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


def main():
    args = get_args()

    ensure_single_instance()
    configure_logging(args.logging_settings)
    logger.info('Initiating')

    if not os.path.exists(args.twitter_settings):
        show_error('%s does not exist' % args.twitter_settings)
        return

    a = area.monitor_area()

    if not a.is_valid:
        show_error('Invalid area ' + str(a))
        return

    image = take_screen_shot(a.bbox)
    # can't get this to work with BytesIO
    image_file_name = generate_temp_file_name()
    image.save(image_file_name, format='png')
    with open(image_file_name, 'rb') as f:
        share_image(f, args.twitter_settings)


if __name__ == '__main__':
    main()
