import string

from itertools import chain
from fractions import Fraction
from fractions import gcd

from .tracks import Track, TimeSeries

class BeatChar(object):

    def __init__(self, char, length=None):
        self.char = char
        self._length = length

    def length(self):
        return self._length if self._length is not None else len(self.char)

    def __repr__(self):
        return repr(self.char)

class AsciiPhrase:
    """ A series of notes (plus beat-resolution).

        >>> AsciiPhrase('D.dk  ').length()
        Fraction(1, 1)
        >>> AsciiPhrase('D.dk..').length()
        Fraction(3, 2)
        >>> AsciiPhrase('D.dk..')
        AsciiPhrase(4, 3/2, 'D.dk ..')
        >>> AsciiPhrase('D.. k.. d.. k..\\n', 6)
        AsciiPhrase(6, 2, 'D..k.. d..k..')
        >>> AsciiPhrase('D', 1) + AsciiPhrase('D.dkDk.k')
        AsciiPhrase(4, 3, 'D... D.dk Dk.k')
        >>> AsciiPhrase('D.dk', 4).as_timeseries().length() == 1
        True
    """

    def __init__(self, pattern, beat=4):
        self.pattern = self.flatten_and_clean(pattern)
        self.beat = Fraction(1, beat)


    ALLOWED_CHARS =  string.ascii_letters + string.digits + string.punctuation

    def flatten_and_clean(self, pattern, keep_chars=ALLOWED_CHARS):
        if isinstance(pattern, (list, tuple)):
            return ''.join(self.flatten_and_clean(p) for p in pattern)
        return ''.join(p for p in pattern if p in self.ALLOWED_CHARS)


    def __repr__(self):
        return '{}({}, {}, {})'.format(
            self.__class__.__name__,
            self.beat.denominator,
            self.length(),
            repr(self.pretty_pattern()),
        )


    def length(self):
        return len(self.pattern) * self.beat


    def pretty_pattern(self, step=None, spacer=' '):
        at = 0
        if step is None:
            step = self.beat.denominator
        fmt = []
        while at < len(self.pattern):
            fmt.append(self.pattern[at:at+step])
            at += step
        return spacer.join(fmt)


    FILLVALUE = '.'

    def scale_to_freq(self, freq, seq, fillvalue=None):
        cnt = 0
        for item in seq:
            yield item
            cnt += 1
            while cnt % freq:
                yield self.FILLVALUE if fillvalue is None else fillvalue
                cnt += 1


    def __add__(self, other):
        new_beat = gcd(self.beat, other.beat)
        assert new_beat.numerator == 1, 'bad beat fraction? {}'.format(new_beat)
        self_freq = self.beat / new_beat
        other_freq = other.beat / new_beat
        new_pattern = chain(
            self.scale_to_freq(self_freq, self.pattern),
            self.scale_to_freq(other_freq, other.pattern),
        )
        return self.__class__(''.join(new_pattern), new_beat.denominator)


    def __mul__(self, other):
        new = self.__class__('', beat=1)
        for i in range(int(other)):
            new += self
        return new

    __rmul__ = __mul__

    def as_timeseries(self):
        now = Fraction()
        result = TimeSeries()
        for idx, c in enumerate(self.pattern):
            result[now].append(BeatChar(c, self.beat))
            now += self.beat
        return result

class AsciiTrack(Track):
    """ A track made from (small/reusable) ascii characters.
        Adds BPM metadata and handles it.

        >>> a = AsciiTrack(['D.dkD.dkD.dkDk.k'],bpm=60)
        >>> a.beat_ms()
        1000.0
        >>> a.bpm = 120
        >>> a.beat_ms()
        500.0
        >>> a.produce().length()
        2000.0
        >>> sorted(a.produce()) == range(0, 2000, 125)
        True
    """

    bpm = 95
    phrases = None

    def __init__(self, phrases=(), bpm=None):
        self.phrases = TimeSeries()
        aps = [AsciiPhrase(p) for p in phrases]
        if aps:
            self.phrases = aps
        if bpm:
            self.bpm = bpm

    def beat_ms(self):
        return 60000. / float(self.bpm)

    def produce(self):
        """ Convert tacts to ms floats (using bpm). """
        result = TimeSeries()
        mule = self.beat_ms()
        for phrase in self.phrases:
            for t, lst in phrase.as_timeseries().items():
                result[float(t * mule)] = [BeatChar(lst[0].char, float(lst[0]._length * mule))]
        return result
