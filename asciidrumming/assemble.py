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


def detect_component(term, phrases):
    for word in term.split():
        if word in phrases:
            return phrases[word]

def assemble_pieces(phrases, pieces):
    assembled = phrases.copy()
    retry = pieces
    todo = []
    while len(retry) != len(todo):
        todo = retry
        retry = {}
        for name, term in todo.items():
            parent = detect_component(term, assembled)
            env = {k: v['pattern'] for k, v in assembled.items()}
            try:
                new_pattern = eval(term, env)
            except NameError as ex:
                retry[name] = term
            else:
                assembled[name] = dict(pattern=''.join(new_pattern))
                assembled[name]['beat'] = parent['beat']
                if 'shuffle' in parent:
                    assembled[name]['shuffle'] = parent['shuffle']

    return assembled

def clean_phrases(phrases):
    for phrase in phrases.values():
        phrase['pattern'] = ''.join(phrase['pattern']).replace(' ', '')
        phrase['length'] = (len(phrase['pattern']) / phrase['beat']) + bool(len(phrase['pattern']) % phrase['beat'])


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
    effective = {}
    effective.update(composition['initial'])

    voices = set(composition['voices'])
    phrases = composition['phrases']

    verse_shuffle = False
    assembled = []
    for verse in composition['verses']:
        if verse_shuffle:
            effective.pop('shuffle')
        if 'bpm' in verse:
            effective['bpm'] += verse.pop('bpm')
        if 'shuffle' in verse:
            if 'shuffle' not in effective:
                verse_shuffle = True
            effective['shuffle'] = verse['shuffle']
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
    return render_shuffle(verse, offset)
    #return render_straight(verse, offset)

def render_shuffle(verse, offset):
    bpm = verse.pop('bpm')
    beat_secs = 60.0 / bpm
    verse_length = float('-inf')
    rendered = defaultdict(list)
    for voice, phrase in verse.items():
        pattern = phrase['pattern']
        shuffle = phrase.get('shuffle', 0)
        ticks_per_beat = phrase['beat']
        tick_secs = beat_secs / ticks_per_beat
        now = offset
        for idx, char in enumerate(pattern):
            if char not in '.':
                _now = now
                if (idx % 2):
                    _now += tick_secs * shuffle
                rendered[_now].append((voice, char))
            now += tick_secs
        verse_length = max(verse_length, now - offset)

    rendered['time_taken'] = verse_length
    return rendered

#def render_straight(verse, offset=0):
    #rendered = defaultdict(list)
    #bpm = verse.pop('bpm')
    #beat_secs = 60.0 / bpm
    #verse_length = float('-inf')
    #for voice, phrase in verse.items():
        #pattern = phrase['pattern']
        #ticks_per_beat = phrase['beat']
        #tick_secs = beat_secs / ticks_per_beat
        #now = offset
        #for char in pattern:
            #if char not in '.':
                #rendered[now].append((voice, char))
            #now += tick_secs
        #verse_length = max(verse_length, now - offset)

    #rendered['time_taken'] = verse_length
    #return rendered

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
