try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup

config = {
    'description': 'A markdown previewer that will auto-update as the file it is watching changes.',
    'author': 'David Beckingsale',
    'url': 'URL to get it at.',
    'download_url': 'Where to download it.',
    'author_email': 'davidbeckingsale@gmail.com',
    'version': '0.1',
    'install_requires': ['nose'] ,
    'packages': ['pmdp'],
    'scripts': [],
    'name': 'pmdp'
    }

setup(**config)
