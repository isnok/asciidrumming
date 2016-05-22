""" An abstraction layer for a new attempt on generating songs. """

from collections import defaultdict

def getlen(item):
    if hasattr(item, 'length'):
        return item.length()
    return len(item)


class TimeSeries(defaultdict):
    """ Basically a MultiSet (implemented defaultdict-style)
        with numeric (linear ordered) keys.

        >>> t = TimeSeries({1: [[1, 2]]})
        >>> t
        TimeSeries({1: [[1, 2]]})
        >>> len(t)
        1
        >>> t.length()
        2
        >>> t.starts()
        1
        >>> t.ends()
        3

        The values are suppoed to be (sample) objects, that have a length.
        This length is used to calculate the length of the Timeseries object.

        >>> t[0]
        []
        >>> len(t)
        2
        >>> t.length()
        3
        >>> t[0].append('long sequence')
        >>> t.length() == 13 == len('long sequence')
        True
        >>> u = t >> 2
        >>> t == u << 2
        True
        >>> u.ends()
        15
        >>> v = t % u
        >>> len(v)
        4
        >>> v == u % t
        True
        >>> v.length()
        15
        >>> sorted(v.keys()) == range(4)
        True
        >>> (v+v).length()
        30
        >>> sorted((v+v).keys())
        [0, 1, 2, 3, 15, 16, 17, 18]
        >>> (3*u) == (u*3)
        True
        >>> len(3*u) == 3 * len(u)
        True
        >>> (3*u).length() == 3 * u.length()
        True
    """

    def __init__(self, iterable=(), **kwd):
        super(TimeSeries, self).__init__(list, iterable, **kwd)

    def __setitem__(self, key, value):
        if not isinstance(value, (list, tuple)):
            raise ValueError('TimeSeries object prevented invalid (not list-ish) value: %s' % value)
        super(TimeSeries, self).__setitem__(key, value)

    def __repr__(self):
        return '%s(%s)' % (
            self.__class__.__name__,
            dict.__repr__(self),
        )

    def length(self):
        """ Determine the length of the series. It may start at negaive indexes. """
        if not self:
            return 0
        mx = 0
        mn = float('inf')
        for start, samples in self.items():
            mn = min(start, mn)
            if samples:
                longest = max([getlen(x) for x in samples])
                mx = max(mx, start + longest)
        return mx - mn

    def starts(self):
        """ The first timeslot that is part of the timeseries. """
        if self:
            return min(self)

    def ends(self):
        """ The first timeslot that is not part of the timeseries anymore. """
        if self:
            mx = 0
            for start, samples in self.items():
                if samples:
                    longest = max([getlen(x) for x in samples])
                    mx = max(mx, start + longest)
            return mx

    def __rshift__(self, other):
        """ Move the series to the future.  """
        return self.__class__((s+other, l[:]) for s, l in self.items())

    def __lshift__(self, other):
        """ Move the series to the past.  """
        return self.__class__((s-other, l[:]) for s, l in self.items())

    def __mod__(self, other):
        """ Merge the two timeseries. """
        result = self.__class__(self)
        for k, v in other.items():
            result[k].extend(v)
        return result

    def __add__(self, other):
        """ Concatenate the two timeseries. """
        if not other:
            return self.__class__(self)
        elif not self:
            return self.__class__(other)
        return self % (other >> self.length())

    def __mul__(self, other):
        """ Multiply (replay) the timeseries. """
        result = self.__class__()
        if self and other:
            l = self.length()
            for n in range(other):
                result %= (self >> (l*n))
        return result

    __rmul__ = __mul__


class Track(object):
    """ A Track can contain any highlevel abstraction it requires,
        it just needs to provide a way to produce itself as a timeseries
        (of Sample objects).

        These timeseries can then be merged, and finally be 'rendered'
        (to audio or text).

        The Track so adds meaning (aka metadata) to a TimeSeries.
        At first, we don't add any abstraction, but just define an interface
        (for the composition rendering / reusability).
    """
    def produce(self):
        return TimeSeries()


def render_tracks(lst):
    result = TimeSeries()
    for t in lst:
        result %= t.produce()
    return result
