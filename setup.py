"""The setup script."""

import re
import pathlib
from setuptools import setup, find_packages
from os import path

<<<<<<< Updated upstream
package_name = 'bqlint'

root_dir = path.abspath(path.dirname(__file__))
=======
# The directory containing this file
root_dir = pathlib.Path(__file__).parent
>>>>>>> Stashed changes


def _requirements():
    return [name.rstrip() for name in open(path.join(root_dir, 'requirements.txt')).readlines()]


<<<<<<< Updated upstream
=======
try:
    with open(path.join(root_dir, 'README.rst')) as f:
        long_description = f.read()
except IOError:
    long_description = ''

>>>>>>> Stashed changes
# read __init__
with open(path.join(root_dir, package_name, '__init__.py')) as f:
    init_text = f.read()
    version = re.search(r'__version__\s*=\s*[\'\"](.+?)[\'\"]', init_text).group(1)
assert version

setup(
    name=package_name,
    version=version,
    # license=_license,
    author='shigeru',
    author_email='matsuzaki215@gmail.com',
<<<<<<< Updated upstream
    url='https://github.com/shigeru0215/bqlint',
    description='ref: https://github.com/shigeru0215/bqlint',
    packages=[package_name],
=======
    url='https://github.com/shigeru0215/sqlint',
    description='Simple Sql Linter',
    long_description=long_description,
    packages=find_packages(exclude=("tests",)),
>>>>>>> Stashed changes
    test_suite='tests',
    install_requires=_requirements(),
    classifiers=[
        # 'Development Status :: 5 - Production/Stable',
        # 'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    entry_points={
        "console_scripts": [
            'bqlint=bqlint.__main__:main',
        ]
    }
)
