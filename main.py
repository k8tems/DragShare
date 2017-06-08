import argparse
import logging
import logging.config
import os
from ctypes import windll
import yaml
from desktopmagic.screengrab_win32 import getRectAsImage
from tkinter import Tk
import drag
from exception import log_exception
from view import run_image_view
import error


logger = logging.getLogger(__name__)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--twitter_settings', type=str, default='twitter.yml')
    parser.add_argument('--logging_settings', type=str, default='log.yml')
    return parser.parse_args()


def configure_logging(logging_settings):
    logging.config.dictConfig(yaml.load(open(logging_settings)))


def take_screen_shot(bbox):
    # `PIL.ImageGrab` does not support multi monitor environments
    return getRectAsImage(bbox)


def support_scaled_screen():
    windll.user32.SetProcessDPIAware()


@log_exception
def main():
    args = get_args()

    support_scaled_screen()
    configure_logging(args.logging_settings)
    logger.info('Initiating')

    if not os.path.exists(args.twitter_settings):
        # root is required to show message box
        Tk().withdraw()
        error.display('%s does not exist' % args.twitter_settings)
        return

    area = drag.monitor_drag()

    if not area.is_valid:
        logger.warning('Invalid area %s %s' % (area.init_pos, area.cur_pos))
        return

    image = take_screen_shot(area.bbox)
    run_image_view(image, area, args.twitter_settings, 'loading.gif')


if __name__ == '__main__':
    main()
