import yaml
from glob import glob

from .config import find_config_files
from .config import yamload

def load_voices(name):
    found = find_config_files(name)
    if not found:
        raise FileNotFoundError('voice config: {}'.format(name))
    return yamload(found[0])
