import os
from glob import glob
from pydub import AudioSegment
from pydub import playback

play = playback.play
silence = AudioSegment.silent

from .config import find_sample_files

def load_sample(name, *dirs):
    found = find_sample_files(name, *dirs)
    if not found:
        raise FileNotFoundError('sample name: {}'.format(name))
    return AudioSegment.from_file(found[0])

cache = {}
def make_sound(term):
    if term in cache:
        return cache[term]
    term = term.split()
    sound = load_sample(term[0])
    if len(term) > 1:
        sound = eval(' '.join(term), {term[0]: sound})
    return cache.setdefault(' '.join(term), sound)

#from operator import itemgetter

def render_to_pydub(flat_song, instruments):
    END_BUFFER = 7
    FACTOR = 1000.0

    length = (flat_song[-1][0] + END_BUFFER) * FACTOR
    recording = silence(length)
    for idx, (ts, (instr, char)) in enumerate(flat_song):
        if not (idx % 10):
            print('overlaying... {}/{} {:.2%} ~ {:.2f}s'.format(
                    idx,
                    len(flat_song),
                    float(idx) / len(flat_song),
                    ts,
                )
            )
        if char in instruments[instr]:
            term = instruments[instr][char]
            sound = make_sound(term)

            #print((ts, instr, char, len(sound), len(recording)))
            recording = recording.overlay(sound, position=ts*FACTOR)

    return recording

