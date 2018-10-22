from distutils.core import setup
from setuptools import find_packages

setup(
  name='dbnet',
  version='0.0.1',
  description='DbNet.',
  author='Fritz Larco',
  author_email='flarco@live.com',
  url='https://github.com/flarco/dbnet',
  download_url='https://github.com/flarco/dbnet.git',
  keywords=['dbnet'],
  packages=find_packages(exclude=['tests']),
  include_package_data=True,
  install_requires=[
    "git+git://github.com/flarco/xutil.git",
    "verboselogs",
    "coloredlogs",
    "psutil",
    "jmespath",
    "eventlet",
  ],
  entry_points={
    'console_scripts': ['dbnet=dbnet.cli:dbnet_cli'],
  },
  classifiers=[
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3', 'Intended Audience :: Developers',
    'Intended Audience :: Education', 'Intended Audience :: Science/Research',
    'Operating System :: Windows', 'Operating System :: MacOS',
    'Operating System :: Unix', 'Topic :: Utilities'
  ])