import yaml
from twython import Twython


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


if __name__ == '__main__':
    image_file = open('test.png', 'rb')
    share_image(image_file)
