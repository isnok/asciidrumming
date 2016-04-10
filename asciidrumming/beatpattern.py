#from .config import yamload

from fractions import Fraction
from fractions import gcd

from itertools import chain

def at_freq(freq, seq, fillvalue='.'):
    cnt = 0
    for item in seq:
        yield item
        cnt += 1
        while cnt % freq:
            yield fillvalue
            cnt += 1


class Phrase:

    def __init__(self, pattern, beat=4):
        self.pattern = ''.join(pattern).replace(' ', '')
        self.beat = Fraction(1, beat)

    def __repr__(self):
        return '{}({}, {}, {})'.format(
            self.__class__.__name__,
            self.beat.denominator,
            self.length,
            repr(self.format_pattern()),
        )

    @property
    def length(self):
        return len(self.pattern) * self.beat

    def format_pattern(self, step=None, spacer=' '):
        at = 0
        if step is None:
            step = self.beat.denominator
        fmt = []
        while at < len(self.pattern):
            fmt.append(self.pattern[at:at+step])
            at += step
        return spacer.join(fmt)

    def __add__(self, other):
        new_beat = gcd(self.beat, other.beat)
        assert new_beat.numerator == 1, 'bad beat fraction? {}'.format(new_beat)
        self_freq = self.beat / new_beat
        other_freq = other.beat / new_beat
        new_pattern = chain(
            at_freq(self_freq, self.pattern),
            at_freq(other_freq, other.pattern),
        )
        return self.__class__(''.join(new_pattern), new_beat.denominator)

    def __mul__(self, other):
        new = Phrase('', beat=1)
        for i in range(other):
            new += self
        return new

    def __rmul__(self, other):
        return self.__mul__(int(other))

    def render(self, offset=0, effects=None):
        now = Fraction(offset, 1)
        for char in self.pattern:
            yield now, char, effects
            now += self.beat

from collections import defaultdict

class RootPiece:

    def __init__(self, voices, effects=None):
        self.voices = voices
        if effects is None:
            self.effects = {}
        else:
            self.effects = effects

    def __repr__(self):
        return '{}({}, {}, {})'.format(
            self.__class__.__name__,
            self.length,
            ' '.join(['{}={}'.format(k, v) for k, v in self.effects.items()]),
            ' '.join(['{}:{}'.format(n, str(v.length)) for n, v in self.voices.items()]),
        )

    @property
    def length(self):
        return max([p.length for p in self.voices.values()])

    def apply(self, effects):
        new_fx = effects.copy()
        new_fx.update(self.effects)
        return self.__class__(self.voices.copy(), new_fx)

    def render(self, offset=0):
        my_voices = []



class CompositePiece:

    def __init__(self, pieces, effects=None):
        if effects is None:
            self.effects = {}
        else:
            self.effects = effects

        self.pieces = self.apply(self.effects, pieces)

    def apply(self, effects, pieces=None):
        if pieces is None:
            pieces = self.pieces
        new_fx = effects.copy()
        new_fx.update(self.effects)
        done = []
        for p in pieces:
            if isinstance(p, CompositePiece):
                done.extend(p.apply(new_fx))
            else:
                done.append(p.apply(new_fx))
        return done

    def __repr__(self):
        return '{}({}, {})'.format(
            self.__class__.__name__,
            self.length,
            #' '.join(['{}={}'.format(k, v) for k, v in self.effects.items()]),
            [p for p in self.pieces],
        )

    @property
    def length(self):
        return sum([p.length for p in self.pieces])

def main():
    voices = {
        'a': 3 * Phrase('abcd', 4) + Phrase('123', 3),
        'b': Phrase('123456', 3) + Phrase('', 4),
    }
    for v in voices.values():
        print(v)
        for x in v.render():
            print('->', x)
    p1 = RootPiece(voices, {'bpm': 60})
    p2 = RootPiece({
        'c': Phrase('Y', 4) + Phrase('D', 1) + Phrase('X', 4)
    })
    c = CompositePiece([p1, p2], {'bpm': 80, 'shuffle': 0.3})
    d = CompositePiece([p1, c, p2], {'bpm': 120})
    print(d)

if __name__ == '__main__':
    main()

