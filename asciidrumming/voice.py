import yaml
from glob import glob

from .config import find_config_files

def load_voices(name):
    found = find_config_files(name)
    if not found:
        raise FileNotFoundError('voice config: {}'.format(name))
    with open(found[0]) as fh:
        return yaml.load(fh)
