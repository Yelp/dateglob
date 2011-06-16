from datetime import date, timedelta

from testify import TestCase
from testify import assert_equal
from testify import assert_raises
from testify import run

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


class TestStrftime(TestCase):

    def test_empty(self):
        assert_equal(strftime([], '%Y-%m-%d'), [])
        assert_equal(strftime((), '%Y-%m-%d'), [])

    def test_empty_with_bad_format(self):
        # don't look at format string if no dates
        assert_equal(strftime([], object()), [])

    def test_nonempty_with_bad_format(self):
        # don't let the user pass in the wrong sorts of args
        assert_raises(AssertionError, strftime, 'swapped-%Y', y(2010))

    def test_non_strftime_format(self):
        assert_equal(strftime(y(2010), 'foo'), ['foo'])

        # don't look at dates at all if it's not a format string
        assert_equal(strftime([object()], 'foo'), ['foo'])

    def test_month_globbing(self):
        assert_equal(strftime(m(2010, 6), '%Y-%m-%d'), ['2010-06-*'])

        # %b, and %B are okay too, but are locale-specific
        assert_equal(strftime(m(2010, 6), '%b %d, %Y'),
                     [date(2010, 6, 1).strftime('%b *, 2010')])
        assert_equal(strftime(m(2010, 6), '%B %d, %Y'),
                     [date(2010, 6, 1).strftime('%B *, 2010')])

    def test_month_no_globbing(self):
        # can't glob day-of-year (%j)
        assert_equal(strftime(m(2010, 6), '%Y-%j'),
                     [d.strftime('%Y-%j') for d in m(2010, 6)])
        
        # can't glob day-of-week (%a, %A, %W)
        assert_equal(strftime(m(2010, 6), '%Y-%a'),
                     sorted(set(d.strftime('%Y-%a') for d in m(2010, 6))))
        assert_equal(strftime(m(2010, 6), '%Y-%A'),
                     sorted(set(d.strftime('%Y-%A') for d in m(2010, 6))))
        assert_equal(strftime(m(2010, 6), '%Y-%w'),
                     sorted(set(d.strftime('%Y-%w') for d in m(2010, 6))))
        
        # can't glob whole date (%c, %x)
        assert_equal(strftime(m(2010, 6), '%c'),
                     sorted(d.strftime('%c') for d in m(2010, 6)))
        assert_equal(strftime(m(2010, 6), '%x'),
                     sorted(d.strftime('%x') for d in m(2010, 6)))
        
    def test_year_globbing(self):
        assert_equal(strftime(y(2010), '%Y-%m-%d'), ['2010-*-*'])
        assert_equal(strftime(y(2010), '%b %d, %Y'), ['* *, 2010'])
        assert_equal(strftime(y(2010), '%B %d, %Y'), ['* *, 2010'])

        # old two-digit year (%y)
        assert_equal(strftime(y(2010), '%y-%m-%d'), ['10-*-*'])

        # can handle day-of-week and day-of-year
        assert_equal(strftime(y(2010), '%Y: %a, %A, %j, %w'),
                     ['2010: *, *, *, *'])

    def test_year_no_globbing(self):
        # can't glob whole date (%c, %x)
        assert_equal(strftime(y(2010), '%c'),
                     sorted(d.strftime('%c') for d in y(2010)))
        assert_equal(strftime(y(2010), '%x'),
                     sorted(d.strftime('%x') for d in y(2010)))

    def test_readme(self):
        # good test of a range of dates
        dates = [date(2009, 12, 31) + timedelta(i) for i in xrange(1+365+31+1)]
        assert_equal(strftime(dates, '%Y-%m-%d'),
                     ['2009-12-31', '2010-*-*', '2011-01-*', '2011-02-01'])

    def test_sorting(self):
        # another test, of a discontinuous range of dates
        dates = ([date(2010, 6, 6)] +
                 list(m(2007, 7)) +
                 list(y(2011)) +
                 [date(2007, 5, 6)])

        assert_equal(strftime(dates, '%Y-%m-%d'),
                     ['2007-05-06', '2007-07-*', '2010-06-06', '2011-*-*'])

        # sorting is just alphabetical, not by date
        assert_equal(strftime(dates, '%m/%d/%y'),
                     ['*/*/11', '05/06/07', '06/06/10', '07/*/07'])        

    def test_no_duplicates(self):
        dates = [date(2010, 6, 6)] * 10000
        assert_equal(strftime(dates, '%Y-%m-%d'), ['2010-06-06'])

    def test_time_fields_are_globbed(self):
        assert_equal(
            strftime([date(2010, 6, 6)], '%Y-%m-%dT%H:%M:%SZ'),
            ['2010-06-06T*:*:*Z'])

        assert_equal(
            strftime(y(2010), '%Y-%m-%d %f%I%p%S%X%z%Z'),
            ['2010-*-* *'])

    def test_no_double_wildcard(self):
        assert_equal(strftime(y(2010), '%Y%m%d'), ['2010*'])

    def test_percent_escaping(self):
        assert_equal(strftime(y(2011), '110%%'), ['110%'])

        # don't incorrectly grab % out of %% to do globbing
        assert_equal(strftime(y(2011), '%m %%m %%%m'), ['* %m %*'])

        # catch invalid strftime string
        assert_raises(ValueError, strftime, y(2011), '110%')


if __name__ == '__main__':
    run()
