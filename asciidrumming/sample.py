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

#from operator import itemgetter

def render_to_pydub(flat_song, instruments):
    END_BUFFER = 7
    FACTOR = 1000.0
    gig = []

    length = (flat_song[-1][0] + END_BUFFER) * FACTOR
    recording = silence(length)
    for ts, (instr, char) in flat_song:
        if char in instruments[instr]:
            term = instruments[instr][char].split()
            sound = load_sample(term[0])
            if len(term) > 1:
                sound = eval(' '.join(term), {term[0]: sound})

            #print((ts, instr, char, len(sound), len(recording)))
            recording = recording.overlay(sound, position=ts*FACTOR)

    return recording

