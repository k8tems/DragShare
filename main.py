import tempfile
import uuid
import yaml
import os
from functools import partial
from pynput import mouse
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


def get_area_src(src, dest):
    return min(src[0], dest[0]), min(src[1], dest[1])


def get_area_dest(src, dest):
    return max(src[0], dest[0]), max(src[1], dest[1])


def on_click(result, x, y, button, pressed):
    if pressed:
        result['pressed_crd'] = x, y
    else:
        result['released_crd'] = x, y
        # return False to end listener
        return False


def get_area():
    result = {}
    with mouse.Listener(on_click=partial(on_click, result)) as listener:
        listener.join()
    src = get_area_src(result['pressed_crd'], result['released_crd'])
    dest = get_area_dest(result['pressed_crd'], result['released_crd'])
    return src[0], src[1], dest[0], dest[1]


if __name__ == '__main__':
    image = ImageGrab.grab(get_area())
    # can't get this to work with BytesIO
    fname = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
    image.save(fname, format='png')
    with open(fname, 'rb') as f:
        share_image(f)
