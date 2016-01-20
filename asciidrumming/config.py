import os
from glob import glob

LIB_DIR = os.path.dirname(__file__)

SAMPLE_LOOKUP = (
    os.curdir,
    os.path.join(os.curdir, 'samples'),
    os.path.join(LIB_DIR, 'samples'),
)

CONFIG_LOOKUP = (
    os.curdir,
    os.path.join(os.curdir, 'samples'),
    os.path.join(LIB_DIR, 'default')
)

def find_files(name, *dirs):
    found = []
    if not dirs:
        dirs = '.'
    for dir in dirs:
        glb = os.path.join(dir, name + '*')
        found.extend(glob(glb))
    return found

def find_sample_files(name, *dirs):
    global SAMPLE_LOOKUP
    return find_files(name, *(SAMPLE_LOOKUP + dirs))
