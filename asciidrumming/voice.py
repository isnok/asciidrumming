import yaml
from glob import glob

from .config import find_config_files
from .config import yamload

def load_voices(name):
    found = find_config_files('drumset.yaml')
    config = yamload(found[0])
    found = find_config_files(name, '.')
    config.update(yamload(found[0]))
    if not found:
        raise FileNotFoundError('voice config: {}'.format(name))
    return config
