import os
import uuid
import tempfile
import yaml
import logging
import logging.config
import tkMessageBox
from tkinter import Tk
from twython import Twython
from PIL import ImageGrab
from quicklock import singleton
import area


SETTINGS_FILE = 'settings.yml'
logger = logging.getLogger()


def get_api():
    cfg = yaml.load(open(SETTINGS_FILE, 'rb'))
    return Twython(
        cfg['consumer_key'],
        cfg['consumer_secret'],
        cfg['access_token_key'],
        cfg['access_token_secret'])


def share_image(image_file):
    api = get_api()
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


def configure_logging():
    logging.config.dictConfig(yaml.load(open('log.conf')))


def main():
    logger.info('Initiating')
    ensure_single_instance()
    configure_logging()

    if not os.path.exists(SETTINGS_FILE):
        show_error('%s does not exist' % SETTINGS_FILE)
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
        share_image(f)


if __name__ == '__main__':
    main()
