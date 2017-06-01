import sys
import traceback
import logging


logger = logging.getLogger(__name__)


def log_exception(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            # looks ugly without the initial newline
            logger.warning('\n' + ''.join(traceback.format_exception(*sys.exc_info())))
            raise
    return inner
