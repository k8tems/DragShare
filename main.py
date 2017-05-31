import argparse
import logging
import logging.config
import os
import tkMessageBox
from ctypes import windll
import yaml
from desktopmagic.screengrab_win32 import getRectAsImage
from quicklock import singleton
from tkinter import Tk
import drag
from view import run_image_view


logger = logging.getLogger()


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--twitter_settings', type=str, default='twitter.yml')
    parser.add_argument('--logging_settings', type=str, default='log.conf')
    return parser.parse_args()


def ensure_single_instance():
    singleton('DragShare')


def configure_logging(logging_settings):
    logging.config.dictConfig(yaml.load(open(logging_settings)))


def show_error(msg):
    # hide required tkinter root window
    # is it an anti-pattern to instantiate multiple root objects within the application lifetime??
    root = Tk()
    root.withdraw()
    tkMessageBox.showerror('Error', msg)


def take_screen_shot(bbox):
    # `PIL.ImageGrab` does not support multi monitor environments
    return getRectAsImage(bbox)


def support_scaled_screen():
    windll.user32.SetProcessDPIAware()


def main():
    args = get_args()

    ensure_single_instance()
    support_scaled_screen()
    configure_logging(args.logging_settings)
    logger.info('Initiating')

    if not os.path.exists(args.twitter_settings):
        show_error('%s does not exist' % args.twitter_settings)
        return

    area = drag.monitor_drag()

    if not area.is_valid:
        logger.warning('Invalid area ' + str(area))
        return

    image = take_screen_shot(area.bbox)
    run_image_view(image, area, args.twitter_settings)


if __name__ == '__main__':
    main()
