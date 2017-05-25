import tempfile
import uuid
import yaml
import os
from twython import Twython
from PIL import ImageGrab


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
    api.update_status(status='test', media_ids=[media_id])


def get_image_of_area(area):
    img = ImageGrab.grab(area)
    return img


if __name__ == '__main__':
    image = get_image_of_area((0, 0, 50, 50))
    # can't get this to work with BytesIO
    fname = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
    image.save(fname, format='png')
    with open(fname, 'rb') as f:
        share_image(f)
    os.remove(fname)
