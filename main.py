import os
import uuid
import tempfile
import yaml
from twython import Twython
from PIL import ImageGrab
import area


def get_api():
    cfg = yaml.load(open('settings.yml', 'rb'))
    return Twython(
        cfg['consumer_key'],
        cfg['consumer_secret'],
        cfg['access_token_key'],
        cfg['access_token_secret'])


def share_image(image_file):
    api = get_api()
    media_id = api.upload_media(media=image_file)['media_id']
    api.update_status(media_ids=[media_id])


if __name__ == '__main__':
    a = area.get_area()
    if a.width == 0 or a.height == 0:
        print('Invalid area ' + str(a))
    else:
        image = ImageGrab.grab(a.bbox)
        # can't get this to work with BytesIO
        fname = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
        image.save(fname, format='png')
        with open(fname, 'rb') as f:
            share_image(f)
