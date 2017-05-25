import py2exe
from distutils.core import setup


if __name__ == '__main__':
    setup(options={'py2exe': {'includes': ['yaml', 'twython']}},
          console=['main.py'])
