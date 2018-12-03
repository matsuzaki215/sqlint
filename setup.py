"""The setup script."""

import re
from setuptools import setup
from os import path

package_name = 'bqlint'

root_dir = path.abspath(path.dirname(__file__))


def _requirements():
    return [name.rstrip() for name in open(path.join(root_dir, 'requirements.txt')).readlines()]


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
    url='https://github.com/shigeru0215/bqlint',
    description='ref: https://github.com/shigeru0215/bqlint',
    packages=[package_name],
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
