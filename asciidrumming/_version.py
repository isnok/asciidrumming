""" This file will be copied as a static drop-in into your source tree.
    This is the version of this file, that resides in the git repository.
"""

# TODO: make these files pass pylint regularly
# pylint: disable=E0401,E0602

get_version = lambda: 'magic'
VERSION_INFO = {}

template = '''"""
    This file was generated by flowtool-versioning.
    Homepage: https://github.com/isnok/py-flowlib
"""

VERSION_INFO = {}

no_version_version = '0'
git_export_version = '$Format:%d %H$'

def get_version():
    global VERSION_INFO
    if 'version' in VERSION_INFO:
        return VERSION_INFO['version']
    elif not 'Format' in git_export_version:
        return git_export_version
    else:
        return no_version_version
'''

exec(template)

from pprint import pformat

def render_static_file():
    """ Render the version information into the static file template.

        >>> render_static_file().startswith(template[:100])
        True
    """
    global VERSION_INFO
    return template.format(pformat(VERSION_INFO))

import os
from os.path import join, dirname, isfile

import sys
PYTHON = sys.version_info
configparser_module = 'ConfigParser' if PYTHON.major == 2 else 'configparser'
configparser = __import__(configparser_module)


def find_source_directory(fake_link=None, fake_absolute=None):
    """ Find a directory in the source tree.

        >>> from os.path import isdir
        >>> isdir(find_source_directory())
        True
        >>> find_source_directory(fake_link=True)
        'test_relative'
        >>> find_source_directory(fake_link=True, fake_absolute=True)
        'test_absolute'
    """

    if os.path.islink(__file__) or fake_link:
        link_target = os.readlink(__file__) if not fake_link else 'test_absolute'
        if link_target.startswith(os.sep) or fake_absolute:
            return link_target
        else:
            return os.path.join(
                dirname(__file__),
                link_target,
            ) if not fake_link else 'test_relative'
    else:
        return dirname(__file__)

def get_setup_cfg(name='setup.cfg'):
    """ Return the nearest directory in the parent dirs,
        that contains a setup.cfg, or None if no such
        parent dir exists.

        >>> hasattr(get_setup_cfg(), 'get')
        True
        >>> get_setup_cfg('_unFinDaBle__fIle_')
    """

    current = find_source_directory()

    while not isfile(join(current, name)):
        old = current
        current = dirname(current)
        if old == current:
            # if current == dirname(current)
            # then we cant ascend any further
            return None
    else:
        # loop was left without a break,
        # so there was a file with the name
        parser = configparser.ConfigParser()
        parser.read(join(current, name))
        return parser


import subprocess
def get_stdout(*command):
    """ Simply get the stdout of a subprocess.
        Todo: Maybe enhance this function a bit? (fail handling?)

        >>> get_stdout('echo', 'Hello, World!') == 'Hello, World!\\n'
        True
    """
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    return stdout.decode('utf-8')

#prefixed = [tag for tag in tags if tag.startswith(prefix)]
#print('--> %s' % prefixed)


import re
import sys

pep440_regex = re.compile('^((?P<epoch>[0-9]*)!)?(?P<release>[0-9][0-9]*(\.[0-9][0-9]*)*)\.?((?P<pre_stage>a|b|rc)?(?P<pre_ver>[0-9]*))((\.post(?P<post>[0-9]*)))?((\.dev(?P<dev>[0-9]*)))?$')

def parse_pep440(version_string):
    """ PEP440 versions look like this:

        [N!]N(.N)*[{a|b|rc}N][.postN][.devN]

        Epoch segment: N!
        Release segment: N(.N)*
        Pre-release segment: {a|b|rc}N
        Post-release segment: .postN
        Development release segment: .devN

        >>> parse_pep440('no_version')
        >>> parse_pep440('1.2.3.4')['release']
        (1, 2, 3, 4)
        >>> v = parse_pep440('0!1.2.3.4.b5.post6.dev7')
        >>> v['release']
        (1, 2, 3, 4)
        >>> v['pre_release']
        ('b', 5)
        >>> v['post_release']
        6
        >>> v['dev_release']
        7
        >>> v['epoch']
        '0'
    """

    try:
        match = pep440_regex.fullmatch(version_string)
    except AttributeError:
        match = pep440_regex.match(version_string)
    if match is None:
        return None

    parsed = match.group
    result = dict(
        version=version_string,
    )
    release = parsed('release')
    result.update(
        release=tuple(int(v) for v in release.split('.')),
    )

    if parsed('pre_stage'):
        pre_ver = 0 if not parsed('pre_ver') else int(parsed('pre_ver'))
        result['pre_release'] = (parsed('pre_stage'), pre_ver)

    if parsed('post'):
        result['post_release'] = 0 if not parsed('post') else int(parsed('post'))

    if parsed('dev'):
        result['dev_release'] = 0 if not parsed('dev') else int(parsed('dev'))

    if parsed('epoch'):
        result['epoch'] = parsed('epoch')

    result['normalized'] = normalize_pep440(**result)

    return result


def normalize_pep440(**kwd):
    """ Normalize the version.

        >>> normalize_pep440(**parse_pep440('1.2.3.4.rc5.post.dev'))
        '1.2.3.4rc5'
    """
    normalized = '.'.join(map(str, kwd['release']))
    if 'pre_release' in kwd:
        normalized += '%s%s' % kwd['pre_release']
    if 'post_release' in kwd:
        normalized += '.post' + str(kwd['post_release'])
    if 'dev_release' in kwd:
        normalized += '.dev' + str(kwd['dev_release'])
    if 'epoch' in kwd:
        normalized = '{}!{}'.format(kwd['epoch'], normalized)
    return normalized


#parsed = [parse_pep440(tag[len(prefix):]) for tag in prefixed]
#print(parsed)

def get_commit(identifier):
    return get_stdout('git', 'rev-parse', identifier).strip()


def commit_distance(a, b):
    """ Return the number of commits between a and b.

        >>> commit_distance('HEAD', 'HEAD^')
        1
    """
    rng = '%s...%s' % (a, b)
    return int(get_stdout('git', 'rev-list', '--count', rng))


def git_tags():
    return get_stdout('git', 'tag', '--list').split()

def git_is_dirty():
    return get_stdout('git', 'status', '--short', '--untracked-files=no')

def get_tags_matching(prefix=''):
    tags = git_tags()
    distances = {
        tag: commit_distance('HEAD', tag)
        for tag in tags if tag.startswith(prefix)
    }
    return distances


def gather_vcs_info(prefix):
    """ Gather information from the Version Control System (git).

        >>> i = gather_vcs_info('pfx')
        >>> i['prefix']
        'pfx'
        >>> j = gather_vcs_info('sfx')
        >>> j['commit'] == i['commit']
        True
        >>> j['dirt'] == i['dirt']
        True
    """
    distances = get_tags_matching(prefix)

    vcs_info = dict(
        prefix=prefix,
        prefix_tag_distances=distances,
        commit=get_commit('HEAD'),
        dirt=git_is_dirty(),
    )

    if not distances:
        return vcs_info

    latest_tag = sorted(distances, key=distances.__getitem__)[0]
    tag_version = latest_tag[len(prefix):]
    vcs_info.update(
        latest_tag=latest_tag,
        latest_tag_version=tag_version,
        latest_tag_commit=get_commit(latest_tag),
        tag_version=parse_pep440(tag_version),
    )

    return vcs_info

#print(pformat(VERSION_INFO))


### customizable versioning schemes

def vcs_versioning(version_info):
    """ Use the information from the vcs, and format it nicely.

        >>> vcs_versioning({'vcs_info': {}})
        '0'
        >>> vcs_versioning({'vcs_info': {'commit': 'b838e311995cd969932bad49b9757b95f55c6622',
        ...  'dirt': ' M ../versioning/flowtool_versioning/dropins/version.py\\n',
        ...  'latest_tag': 'flowtool-all-0.7.19',
        ...  'latest_tag_commit': '5d84b2dd0146ac2da8d736147d9c4bb41d4299dd',
        ...  'latest_tag_version': '0.7.19-boo!',
        ...  'prefix': 'flowtool-all-',
        ...  'prefix_tag_distances': {'flowtool-all-0.7.19': 98}},
        ... 'version': '0.7.19.dev98.dirty'})
        '0.dirty'
        >>> vcs_versioning({'vcs_info': {'commit': 'b838e311995cd969932bad49b9757b95f55c6622',
        ...  'dirt': ' M ../versioning/flowtool_versioning/dropins/version.py\\n',
        ...  'latest_tag': 'flowtool-all-0.7.19',
        ...  'latest_tag_commit': '5d84b2dd0146ac2da8d736147d9c4bb41d4299dd',
        ...  'latest_tag_version': '0.7.19',
        ...  'prefix': 'flowtool-all-',
        ...  'prefix_tag_distances': {'flowtool-all-0.7.19': 0},
        ...  'tag_version': {'normalized': '0.7.19',
        ...   'release': (0, 7, 19),
        ...   'version': '0.7.19'}},
        ... 'version': '0.7.19.dev98.dirty'})
        '0.7.19.dirty'
        >>> vcs_versioning({'vcs_info': {'commit': 'b838e311995cd969932bad49b9757b95f55c6622',
        ...  'dirt': '',
        ...  'latest_tag': 'flowtool-all-0.7.19',
        ...  'latest_tag_commit': '5d84b2dd0146ac2da8d736147d9c4bb41d4299dd',
        ...  'latest_tag_version': '0.7.19.dev2',
        ...  'prefix': 'flowtool-all-',
        ...  'prefix_tag_distances': {'flowtool-all-0.7.19': 98},
        ...  'tag_version': {'normalized': '0.7.19',
        ...   'release': (0, 7, 19),
        ...   'version': '0.7.19'}},
        ... 'version': '0.7.19.dev98.dirty'})
        '0.7.19.dev100'
        >>> vcs_versioning({'vcs_info': {'commit': 'b838e311995cd969932bad49b9757b95f55c6622',
        ...  'dirt': ' M ../versioning/flowtool_versioning/dropins/version.py\\n',
        ...  'latest_tag': 'flowtool-all-0.7.19',
        ...  'latest_tag_commit': '5d84b2dd0146ac2da8d736147d9c4bb41d4299dd',
        ...  'latest_tag_version': '0.7.19',
        ...  'prefix': 'flowtool-all-',
        ...  'prefix_tag_distances': {'flowtool-all-0.7.19': 98}},
        ... 'version': '0.7.19.dev98.dirty'})
        '0.7.19.dev98.dirty'
    """

    vcs_info = version_info['vcs_info']

    if not 'latest_tag' in vcs_info:
        return '0'

    tag = vcs_info['latest_tag']
    distance = vcs_info['prefix_tag_distances'][tag]

    vcs_version = parse_pep440(vcs_info['latest_tag_version'])

    if vcs_version and distance:
        if 'dev_release' in vcs_version:
            vcs_version['dev_release'] += distance
        else:
            vcs_version['dev_release'] = distance

        vcs_version = normalize_pep440(**vcs_version)
    elif vcs_version:
        vcs_version = normalize_pep440(**vcs_version)
    elif not vcs_version:
        vcs_version = '0'

    if vcs_info['dirt']:
        vcs_version += '.dirty'

    return vcs_version


setup_cfg = get_setup_cfg()
prefix = setup_cfg.get('versioning', 'tag_prefix') if setup_cfg else ''
vcs_info = gather_vcs_info(prefix)
VERSION_INFO.update(
    vcs_info=vcs_info,
)

assemble_version = vcs_versioning
#assemble_version = snapshot_versioning

version = assemble_version(VERSION_INFO)

if version:
    VERSION_INFO['version'] = version
