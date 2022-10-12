from datetime import date
from datetime import timedelta
from unittest import TestCase

from dateglob import strftime


def m(year, month):
    """Return a list of days in the given month"""
    d = start = date(year, month, 1)
    while d.month == start.month:
        yield d
        d += timedelta(1)


def y(year):
    """Return a list of days in the given year"""
    d = start = date(year, 1, 1)
    while d.year == start.year:
        yield d
        d += timedelta(1)


def t(year, month, day, period=11):
    """Return a list of days in the given year"""
    d = date(year, month, day)
    for i in range(period):
        yield d
        d += timedelta(1)


class TestStrftime(TestCase):

    def test_empty(self):
        self.assertEqual(strftime([], '%Y-%m-%d'), [])
        self.assertEqual(strftime((), '%Y-%m-%d'), [])

    def test_empty_with_bad_format(self):
        # don't look at format string if no dates
        self.assertEqual(strftime([], object()), [])

    def test_non_strftime_format(self):
        self.assertEqual(strftime(y(2010), 'foo'), ['foo'])

        # don't look at dates at all if it's not a format string
        self.assertEqual(strftime([object()], 'foo'), ['foo'])

    def test_month_globbing(self):
        self.assertEqual(strftime(m(2010, 6), '%Y-%m-%d'), ['2010-06-*'])

        # %b, and %B are okay too, but are locale-specific
        self.assertEqual(strftime(m(2010, 6), '%b %d, %Y'),
                     [date(2010, 6, 1).strftime('%b *, 2010')])
        self.assertEqual(strftime(m(2010, 6), '%B %d, %Y'),
                     [date(2010, 6, 1).strftime('%B *, 2010')])

    def test_month_no_globbing(self):
        # can't glob day-of-year (%j)
        self.assertEqual(strftime(m(2010, 6), '%Y-%j'),
                     [d.strftime('%Y-%j') for d in m(2010, 6)])

        # can't glob day-of-week (%a, %A, %W)
        self.assertEqual(strftime(m(2010, 6), '%Y-%a'),
                     sorted(set(d.strftime('%Y-%a') for d in m(2010, 6))))
        self.assertEqual(strftime(m(2010, 6), '%Y-%A'),
                     sorted(set(d.strftime('%Y-%A') for d in m(2010, 6))))
        self.assertEqual(strftime(m(2010, 6), '%Y-%w'),
                     sorted(set(d.strftime('%Y-%w') for d in m(2010, 6))))

        # can't glob whole date (%c, %x)
        self.assertEqual(strftime(m(2010, 6), '%c'),
                     sorted(d.strftime('%c') for d in m(2010, 6)))
        self.assertEqual(strftime(m(2010, 6), '%x'),
                     sorted(d.strftime('%x') for d in m(2010, 6)))

    def test_year_globbing(self):
        self.assertEqual(strftime(y(2010), '%Y-%m-%d'), ['2010-*-*'])
        self.assertEqual(strftime(y(2010), '%b %d, %Y'), ['* *, 2010'])
        self.assertEqual(strftime(y(2010), '%B %d, %Y'), ['* *, 2010'])

        # old two-digit year (%y)
        self.assertEqual(strftime(y(2010), '%y-%m-%d'), ['10-*-*'])

        # can handle day-of-week and day-of-year
        self.assertEqual(strftime(y(2010), '%Y: %a, %A, %j, %w'),
                     ['2010: *, *, *, *'])

    def test_year_no_globbing(self):
        # can't glob whole date (%c, %x)
        self.assertEqual(strftime(y(2010), '%c'),
                     sorted(d.strftime('%c') for d in y(2010)))
        self.assertEqual(strftime(y(2010), '%x'),
                     sorted(d.strftime('%x') for d in y(2010)))

    def test_ten_globbing(self):
        # Test first ten
        self.assertEqual(strftime(t(2016, 5, 1), '%Y-%m-%d'),
                     ['2016-05-0*', '2016-05-10', '2016-05-11'])
        # Test second ten
        self.assertEqual(strftime(t(2016, 5, 10), '%Y-%m-%d'),
                     ['2016-05-1*', '2016-05-20'])
        # Test third ten
        self.assertEqual(strftime(t(2016, 5, 20), '%Y-%m-%d'),
                     ['2016-05-2*', '2016-05-30'])

        # Test fourth ten on 30-day month
        self.assertEqual(strftime(t(2016, 4, 30, period=2), '%Y-%m-%d'),
                     ['2016-04-3*', '2016-05-01'])
        # Test fourth ten on 31-day month with all days
        self.assertEqual(strftime(t(2016, 1, 30, period=2), '%Y-%m-%d'),
                     ['2016-01-3*'])
        # Test fourth ten on 31-day month with one of the 2 days
        self.assertEqual(strftime(t(2016, 1, 30, period=1), '%Y-%m-%d'),
                     ['2016-01-30'])
        # Test fourth ten on 31-day month with one of the 2 days
        self.assertEqual(strftime(t(2016, 1, 31, period=1), '%Y-%m-%d'),
                     ['2016-01-31'])

        # Test February of Leap Year
        self.assertEqual(strftime(t(2016, 2, 20, period=10), '%Y-%m-%d'),
                     ['2016-02-2*'])
        # Test February of Normal Year
        self.assertEqual(strftime(t(2015, 2, 20, period=9), '%Y-%m-%d'),
                     ['2015-02-2*'])

    def test_readme(self):
        # good test of a range of dates
        dates = [date(2009, 12, 31) + timedelta(i) for i in range(1+365+31+1)]
        self.assertEqual(strftime(dates, '%Y-%m-%d'),
                     ['2009-12-31', '2010-*-*', '2011-01-*', '2011-02-01'])

    def test_sorting(self):
        # another test, of a discontinuous range of dates
        dates = ([date(2010, 6, 6)] +
                 list(m(2007, 7)) +
                 list(y(2011)) +
                 [date(2007, 5, 6)])

        self.assertEqual(strftime(dates, '%Y-%m-%d'),
                     ['2007-05-06', '2007-07-*', '2010-06-06', '2011-*-*'])

        # sorting is just alphabetical, not by date
        self.assertEqual(strftime(dates, '%m/%d/%y'),
                     ['*/*/11', '05/06/07', '06/06/10', '07/*/07'])

    def test_no_duplicates(self):
        dates = [date(2010, 6, 6)] * 10000
        self.assertEqual(strftime(dates, '%Y-%m-%d'), ['2010-06-06'])

    def test_time_fields_are_globbed(self):
        self.assertEqual(
            strftime([date(2010, 6, 6)], '%Y-%m-%dT%H:%M:%SZ'),
            ['2010-06-06T*:*:*Z'])

        self.assertEqual(
            strftime(y(2010), '%Y-%m-%d %f%I%p%S%X%z%Z'),
            ['2010-*-* *'])

    def test_no_double_wildcard(self):
        self.assertEqual(strftime(y(2010), '%Y%m%d'), ['2010*'])

    def test_percent_escaping(self):
        self.assertEqual(strftime(y(2011), '110%%'), ['110%'])

        # don't incorrectly grab % out of %% to do globbing
        self.assertEqual(strftime(y(2011), '%m %%m %%%m'), ['* %m %*'])
