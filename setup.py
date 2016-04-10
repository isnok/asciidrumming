#!/usr/bin/env python

from setuptools import setup, find_packages
from versioning import get_cmdclass, get_version

def read_requirements(name='requirements.txt'):
    """ Read reqiurements.txt file into a list of lines, that are
        non-empty, and do not start with a `#`-character.

        >>> len(read_requirements(__file__)) > 0
        True
    """

    with open(name, 'r') as fh:
        lines = [l.strip() for l in fh.readlines() if l.strip()]

    return [r for r in lines if not r.startswith('#')]

setup_args = dict(
    name='asciidrumming',
    description='Ascii-based (drum-)sequencer.',
    url='http://github.com/isnok/asciidrumming',
    author='Konstantin Martini',
    author_email='k@tuxcode.org',
    license='MIT',
)

setup_args.update(
    version=get_version(),
    cmdclass=get_cmdclass(),
    packages=find_packages(),
    install_requires=read_requirements(),
    include_package_data=True,
    zip_safe=False,
)

setup_args.update(
    entry_points={
        'console_scripts': ['ascii_drummer=asciidrumming.cli:cli'],
    },
)

if __name__ == '__main__':
    setup(**setup_args)
