#!/usr/bin/env python

from setuptools import setup

from versioning import get_cmdclass, get_version

def read_requirements(name='requirements.txt'):

    with open(name, 'r') as fh:
        requirements = [l.strip() for l in fh.readlines() if l.strip()]

    return requirements

setup_args = dict(
    name='asciidrumming',
    version=get_version(),
    cmdclass=get_cmdclass(),
    description='Ascii-based (drum-)sequencer.',
    url='http://github.com/isnok/asciidrumming',
    author='Konstantin Martini',
    author_email='k@tuxcode.org',
    license='MIT',
    packages=['asciidrumming'],
    install_requires=read_requirements(),
    entry_points = {
        'console_scripts': ['ascii_drummer=asciidrumming.cli:cli'],
    },
    include_package_data=True,
    zip_safe=False,
)

if __name__ == '__main__': setup(**setup_args)
