from glob import glob
from pydub import AudioSegment
from pydub import playback

play = playback.play
silence = AudioSegment.silent

def find_samples(name, glb='samples/{name}*'):
    found = glob(glb.format(name=name))
    samples = [AudioSegment.from_file(f) for f in found]
    return samples

def make_advanced_instrument(name, voice):
    samples = {char: find_samples(smpl_id) for char, smpl_id in voice.items()}
    return samples

def find_sample(name, glb=None):
    if glb is None:
        args = (name,)
    else:
        args = (name, glb)
    return find_samples(*args)[0]

def make_simple_instrument(name, voice):
    samples = {char: find_sample(smpl_id) for char, smpl_id in voice.items()}
    return samples

from operator import itemgetter

def render_to_pydub(flat_song, instruments):
    END_BUFFER = 7
    FACTOR = 1000.0
    gig = []

    length = (flat_song[-1][0] + END_BUFFER) * FACTOR
    recording = silence(length)
    for ts, (instr, char) in flat_song:
        sound = find_sample(instruments[instr][char])
        #print((ts, instr, char, len(sound), len(recording)))
        recording = recording.overlay(sound, position=ts*FACTOR)

    return recording

