from os import path
from setuptools import setup

setup(
    name = 'dotconfig',
    version = '1.0',
    url='https://github.com/WarBean/dotconfig',
    py_modules = ['dotconfig'],
    author = 'Huabin Zheng',
    author_email = 'warbean@qq.com',
    description = 'Designed for highly convenient and flexible configuration in Deep Learning',
    long_description = open(path.join(path.abspath(path.dirname(__file__)), 'README.rst')).read(),
    license = 'MIT',
    keywords = 'dict dictionary configuration dot deep learning DL',
    zip_safe = False,
    install_requires = [],
)
