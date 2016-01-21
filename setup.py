#!/usr/bin/env python

from setuptools import setup

def read_requirements(name='requirements.txt'):

    with open(name, 'r') as fh:
        requirements = [l.strip() for l in fh.readlines() if l.strip()]

    return requirements

setup(
    name='asciidrumming',
    version='0.2',
    description='Ascii-based (drum-)sequencer.',
    url='http://github.com/isnok/asciidrumming',
    author='Konstantin Martini',
    author_email='flyingcircus@example.com',
    license='None yet',
    packages=['asciidrumming'],
    zip_safe=False,
    install_requires=read_requirements(),
    entry_points = {
        'console_scripts': ['ascii_drummer=asciidrumming.cli:cli'],
    },
    include_package_data=True,
)
