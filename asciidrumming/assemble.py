def assemble_pieces(phrases, pieces):
    env = {k: v['pattern'] for k, v in phrases.items()}
    assembled = {}
    for name, term in pieces.items():
        for word in term.split():
            if word in env:
                beat = phrases[word]['beat']
                break
        else:
            raise RuntimeError('invalid piece: {}'.format(term))
        assembled[name] = dict(beat=beat, pattern=eval(term, env))
    return assembled

def clean_phrases(phrases):
    for phrase in phrases.values():
        phrase['pattern'] = phrase['pattern'].replace(' ', '')

from .config import find_config_files
from .config import yamload

def load_phrases(name):
    files = find_config_files(name)
    phrases = {}
    pieces = {}
    for name in reversed(files):
        cfg = yamload(name)
        phrases.update(cfg['phrases'])
        pieces.update(cfg['pieces'])
    return phrases, pieces

def assemble_phrases(config):
    phrases, pieces = load_phrases('phrases.yaml')
    if 'pieces' in config:
        pieces.update(config.pop('pieces'))
    phrases.update(config.get('phrases', {}))
    pieces = assemble_pieces(phrases, pieces)
    phrases.update(pieces)
    clean_phrases(phrases)
    config['phrases'] = phrases



def assemble_verses(composition):
    effective = {
        'bpm': 80,
    }
    effective.update(composition['initial'])

    voices = set(composition['voices'])
    phrases = composition['phrases']

    assembled = []
    for verse in composition['verses']:
        if 'bpm' in verse:
            effective['bpm'] += verse.pop('bpm')
        now = effective.copy()
        for name, phrase in verse.items():
            if name in voices:
                now[name] = phrases[phrase]
            else:
                now[name] = phrase

        assembled.append(now)

    return assembled

from collections import defaultdict

def render_verse(verse, offset=0):
    rendered = defaultdict(list)
    bpm = verse.pop('bpm')
    beat_secs = 60.0 / bpm
    verse_length = float('-inf')
    for voice, phrase in verse.items():
        pattern = phrase['pattern']
        ticks_per_beat = phrase['beat']
        tick_secs = beat_secs / ticks_per_beat
        now = offset
        for char in pattern:
            if char not in '.':
                rendered[now].append((voice, char))
            now += tick_secs
        verse_length = max(verse_length, now - offset)

    rendered['time_taken'] = verse_length
    return rendered

def render_verses(verses, now=0):

    collector = defaultdict(list)
    for verse in verses:
        rendered = render_verse(verse, now)
        #pprint.pprint(rendered)
        now += rendered.pop('time_taken')
        for k, v in rendered.items():
            collector[k].extend(v)

    flattened = []
    for ts in sorted(collector):
        for sound in collector[ts]:
            flattened.append((ts, sound))
    return flattened
