from os import path
from setuptools import setup

setup(
    name = 'jdconfig',
    version = '2.0',
    url='https://github.com/WarBean/jdconfig',
    py_modules = ['jdconfig'],
    author = 'Huabin Zheng',
    author_email = 'warbean@qq.com',
    description = 'Extended Python dict for flexible hyperparameter configuration in Deep Learning',
    long_description = open(path.join(path.abspath(path.dirname(__file__)), 'README.rst')).read(),
    license = 'MIT',
    keywords = 'json dict configuration deep-learning python',
    zip_safe = False,
    install_requires = ['json5'],
)
