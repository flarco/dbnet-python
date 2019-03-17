from distutils.core import setup
from setuptools import find_packages

version = '0.0.2'

setup(
  name='dbnet',
  version=version,
  description='DbNet.',
  author='Fritz Larco',
  author_email='flarco@live.com',
  url='https://github.com/flarco/dbnet',
  download_url='https://github.com/flarco/dbnet/archive/{}.tar.gz'.format(version),
  keywords=['dbnet'],
  packages=find_packages(exclude=['tests']),
  include_package_data=True,
  install_requires=[
    "python-socketio",
    "verboselogs",
    "coloredlogs",
    "psutil",
    "jmespath",
    "eventlet",
    "xutil",
  ],
  entry_points={
    'console_scripts': ['dbnet=dbnet.cli:dbnet_cli'],
  },
  classifiers=[
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3', 'Intended Audience :: Developers',
    'Intended Audience :: Education', 'Intended Audience :: Science/Research',
    'Operating System :: MacOS', 'Operating System :: Unix',
    'Topic :: Utilities'
  ])