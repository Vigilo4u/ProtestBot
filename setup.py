import setuptools
from setuptools import setup, find_packages

setup(
    python_requires='>=3.0',
    name='ProtestBot',
    version='1.0',
    packages=['protestbot'],
    include_package_data=True,
    license='MIT',
    keywords='steemit steem downvote bot',
    url='http://github.com/viglilo4u/protestbot',
    author='Vigilo4u',
    install_requires=[
        'simplesteem==1.1.17',
        'screenlogger==1.3.1',
    ],
    py_modules=['protestbot'],
    entry_points = {
        'console_scripts': [
            'runbot=protestbot.runbot:run',
        ],
    },
    zip_safe=False
)
