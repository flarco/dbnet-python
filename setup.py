from distutils.core import setup
from setuptools import find_packages
import os

version = '0.2.5'

setup(
  name='dbnet',
  version=version,
  description='DbNet.',
  author='Fritz Larco',
  author_email='flarco@live.com',
  url='https://github.com/flarco/dbnet',
  download_url='https://github.com/flarco/dbnet/archive/master.zip',
  keywords=['dbnet'],
  packages=find_packages(exclude=['tests']),
  include_package_data=True,
  long_description=open(os.path.join(os.path.dirname(__file__),
                                     'README.rst')).read(),
  install_requires=[
    "python-dateutil==2.7.5",
    "verboselogs",
    "coloredlogs",
    "psutil",
    "jmespath",
    "eventlet==0.31.0",
    "PyYAML==5.1.2",
    "flask==0.11.1",
    "Flask-SSLify==0.1.5",
    "xutil",
    "apprise==0.8.4",
    "ruamel.yaml==0.16.7",
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
