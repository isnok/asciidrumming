#!/usr/bin/env python

import click
import pprint

from .parse import parse_composition
#from sample import make_simple_instrument
#from sample import make_advanced_instrument

from .assemble import assemble_phrases
from .assemble import assemble_verses
from .assemble import render_verses

from .sample import render_to_pydub
from .sample import play as play_song

from .voice import load_voices

from .config import yamload

@click.group()
def cli(**kwd):
    return kwd


@cli.command()
def drum():
    ''' soon to come: play strings from the command-line '''

@cli.command()
@click.option('--bpm', default=-1, help='base beats per minute')
@click.option('--output', default=None, help='output file to write')
@click.option('--voices', default='drumset.yaml', help='yaml voice configuration file (updates defaults)')
@click.option('--silent', type=bool, default=False, help='do not play the song immediatley')
@click.option('--backbeat', default=None, help='name of the backbeat phrase')
@click.option('--supporter', default='metronome', help='the instrument (voice) for the backbeat')
@click.argument('composition', default=None)
def play(bpm, composition, voices, backbeat, supporter, silent, output=None):

    ''' play a composition (utilizing the standard repertoire) '''

    config = yamload(composition)

    #config = parse_composition(composition)
    if bpm > 0:
        config['initial']['bpm'] = bpm
    config.update(load_voices(voices))

    assemble_phrases(config)

    song = assemble_verses(config)

    if backbeat is not None:
        backbeats = [k for k in config['phrases'] if config['phrases'][k]['length'] == 1]
        assert backbeat in backbeats
        config['voices']['backbeat'] = config['voices'][supporter].copy()
        for verse in song:
            backphrase = config['phrases'][backbeat].copy()
            backphrase['length'] = max([x['length'] for x in verse.values() if isinstance(x, dict)])
            backphrase['pattern'] *= backphrase['length']
            verse['backbeat'] = backphrase

    pprint.pprint(config)
    pprint.pprint(song)

    rendering = render_verses(song, now=1)
    click.echo('Rendering: {} samples...'.format(len(rendering)))

    song_segment = render_to_pydub(rendering, config['voices'])
    if output is not None:
        song_segment.export(output)

    if not silent:
        play_song(song_segment)

if __name__ == '__main__':
    cli()
