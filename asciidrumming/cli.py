#!/usr/bin/env python2

import click
import pprint

from .parse import parse_composition
#from sample import make_simple_instrument
#from sample import make_advanced_instrument

from .assemble import assemble_phrases
from .assemble import assemble_verses
from .assemble import render_verses

from .sample import render_to_pydub
from .sample import play

from .voice import load_voices

@click.command()
@click.option('--bpm', default=-1, help='base beats per minute')
@click.option('--output', default=None, help='output file to write')
@click.option('--voices', default='drumset.yaml', help='yaml voice configuration file (updates defaults)')
@click.option('--silent', type=bool, default=False, help='do not play the song immediatley')
@click.argument('composition', default='composition.yaml')
def main(bpm, composition, voices, silent, output=None):
    import yaml
    config = yaml.load(open(composition))
    #config = parse_composition(composition)
    if bpm > 0:
        config['initial']['bpm'] = bpm
    config.update(load_voices(voices))

    assemble_phrases(config)
    pprint.pprint(config)

    song = assemble_verses(config)
    pprint.pprint(song)

    rendering = render_verses(song, now=1)
    #pprint.pprint(rendering)

    song_segment = render_to_pydub(rendering, config['voices'])
    if output is not None:
        song_segment.export(output)

    if not silent:
        play(song_segment)

if __name__ == '__main__':
    main()
