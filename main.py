import yaml
from twython import Twython


def get_api():
    cfg = yaml.load(open('settings.yml', 'rb'))
    return Twython(
        cfg['consumer_key'],
        cfg['consumer_secret'],
        cfg['access_token_key'],
        cfg['access_token_secret'])


if __name__ == '__main__':
    print('Hello world!')
    api = get_api()
    api.update_status(status='test')
