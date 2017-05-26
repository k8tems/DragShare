import os
import uuid
import tempfile
import yaml
import time
import logging
import logging.config
import tkMessageBox
from tkinter import Tk
from twython import Twython
from PIL import ImageGrab
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


def main():
    logging.config.dictConfig(yaml.load(open('log.conf')))
    logger.debug('initiating')

    if not os.path.exists(SETTINGS_FILE):
        show_error('%s does not exist' % SETTINGS_FILE)
        return

    a = area.get_area()

    if a.width == 0 or a.height == 0:
        show_error('Invalid area ' + str(a))
        return

    # wait until the window disappears
    time.sleep(1)

    image = ImageGrab.grab(a.bbox)
    # can't get this to work with BytesIO
    fname = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
    image.save(fname, format='png')
    with open(fname, 'rb') as f:
        share_image(f)


if __name__ == '__main__':
    main()
