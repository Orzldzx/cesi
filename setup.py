from distutils.core import setup
from setuptools import setup, find_packages

setup(
  name='cesi',
  version='0.1.1',
  description='Centralized supervisor interface.',
  long_description=open('README.md').read(),
  url='http://github.com/ggiovinazzo/cesi',
  license='GPLv3',
  author='Gulsah Kose',
  author_email='gulsah.1004@gmail.com',
  install_requires=[
    "Flask==0.10.1",
    "requests"
  ],
  include_package_data=True,
)
