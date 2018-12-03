"""The setup script."""

from setuptools import setup, find_packages

setup(
    name='bqlint',
    version='0.0.0',
    author='shigeru',
    author_email='matsuzaki215@gmail.com',
    url='https://github.com/shigeru0215/bqlint',
    packages=find_packages(),
    test_suite='tests',
    install_requires=[
        'Click==7.0'
    ],
    entry_points={
        "console_scripts": [
            "bqlint=bqlint.bqlint:main",
        ]
    }
)
