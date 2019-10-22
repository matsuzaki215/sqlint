"""The setup script."""

import re
import pathlib
from setuptools import setup, find_packages
from os import path

# The directory containing this file
root_dir = pathlib.Path(__file__).parent


def _requirements():
    return [name.rstrip() for name in open(path.join(root_dir, 'requirements.txt')).readlines()]


try:
    with open(path.join(root_dir, 'README.rst')) as f:
        long_description = f.read()
except IOError:
    long_description = ''

# read __init__
with open(path.join(root_dir, 'src/sqlint', '__init__.py')) as f:
    init_text = f.read()
    version = re.search(r'__version__\s*=\s*[\'\"](.+?)[\'\"]', init_text).group(1)
assert version

setup(
    name='sqlint',
    version=version,
    description='Simple Sql Linter',
    long_description=long_description,
    url='https://github.com/shigeru0215/sqlint',
    author='shigeru0215',
    author_email='matsuzaki215@gmail.com',
    license="MIT",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Text Processing :: General',
    ],
    packages=find_packages('src', exclude=['tests']),
    package_dir={'': 'src'},
    package_data={'': ['config/default.ini']},
    test_suite='tests',
    install_requires=_requirements(),
    entry_points={
        "console_scripts": [
            'sqlint=sqlint.__main__:main',
        ]
    }
)
