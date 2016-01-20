import os
from glob import glob

LIB_DIR = os.path.dirname(__file__)

SAMPLE_LOOKUP = (
    os.curdir,
    os.path.join(os.curdir, 'samples'),
    os.path.join(LIB_DIR, 'samples'),
)

CONFIG_LOOKUP = (
    os.path.join(LIB_DIR, 'default'),
)

def find_files(name, fmt, *dirs):
    found = []
    if not dirs:
        dirs = '.'
    for dir in dirs:
        glb = os.path.join(dir, fmt.format(name))
        found.extend(glob(glb))
    return found

def find_sample_files(name, *dirs):
    global SAMPLE_LOOKUP
    return find_files(name, '{}*', *(SAMPLE_LOOKUP + dirs))

def find_config_files(name, *dirs):
    global CONFIG_LOOKUP
    return find_files(name, '{}', *(CONFIG_LOOKUP + dirs))

import yaml
def yamload(name):
    with open(name) as fh:
        yamyam = yaml.load(fh)
    return yamyam
