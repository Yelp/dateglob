# Copyright 2011 Yelp
# Copyright 2016 Patrick Boocock, Yelp
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Convert a set of dates into a compact list of globs. For example:

>>> import dateglob; from datetime import date, timedelta
>>> # build list of dates from 2009-12-31 thru 2011-02-01
>>> dates = [date(2009, 12, 31) + timedelta(i) for i in xrange(1+365+31+1)]
>>> dateglob.strftime(dates, '%Y-%m-%d')
['2009-12-31', '2010-*-*', '2011-01-*', '2011-02-01']

The original use case for this library was to generate compact command lines
for command that take daily log files as input, for example:

>>> args += dateglob.strftime(dates, '/logs/foo/%Y/%m/%d/*.gz')
"""
import calendar
from collections import defaultdict
import datetime
import re


__author__ = 'David Marin <dave@yelp.com>'

__credits__ = [
    'Patrick Boocock <pboocock@jawbone.com>'
]

__version__ = '0.2'

__all__ = ['strftime']


# match directives in a strftime format string (e.g. '%Y-%m-%d')
STRFTIME_FIELD_RE = re.compile('%(.)')

# used to compact multiple adjacent wildcards into a single wildcard.
MULTIPLE_WILDCARD_RE = re.compile(r'\*+')

# all fields handled by the default version of strftime; see
# http://docs.python.org/library/datetime.html#strftime-and-strptime-behavior

# divisions smaller than a day and time zones; always converted to *
TIME_FIELDS = 'fHIMpSXzZ'

DAY_OF_WEEK_FIELDS = 'aAw'

DAY_OF_MONTH_FIELDS = 'd'

DAY_OF_YEAR_FIELDS = 'j'

# week number in year, with weeks starting on Sunday
SUNDAY_WEEK_OF_YEAR_FIELDS = 'U'

# week number in year, with weeks starting on Monday
MONDAY_WEEK_OF_YEAR_FIELDS = 'W'

# month names and numbers
MONTH_FIELDS = 'bBm'

YEAR_FIELDS = 'yY'

# fields that describe the whole date at once (make globbing impossible)
WHOLE_DATE_FIELDS = 'cx'

# The "%%" format; always leave these alone
LITERAL_FIELDS = '%'

# fields that can be replaced with * if we have all days in a year
YEAR_GLOB_FIELDS = (TIME_FIELDS +
                    DAY_OF_WEEK_FIELDS +
                    DAY_OF_MONTH_FIELDS +
                    DAY_OF_YEAR_FIELDS +
                    SUNDAY_WEEK_OF_YEAR_FIELDS +
                    MONDAY_WEEK_OF_YEAR_FIELDS +
                    MONTH_FIELDS)

# fields that preclude globbing even if we have all days in a year
YEAR_BAD_FIELDS = WHOLE_DATE_FIELDS

# fields that can be replaced with * if we have all days in a month
MONTH_GLOB_FIELDS = (TIME_FIELDS +
                     DAY_OF_MONTH_FIELDS)

# fields that preclude globbing even if we have all days in a month
MONTH_BAD_FIELDS = (WHOLE_DATE_FIELDS +
                     DAY_OF_YEAR_FIELDS +
                     DAY_OF_WEEK_FIELDS +
                     SUNDAY_WEEK_OF_YEAR_FIELDS +
                     MONDAY_WEEK_OF_YEAR_FIELDS)

TEN_LENGTH = {
    0: 9,
    1: 10,
    2: 10
}


def strftime(dates, format):
    """Format a sequence of dates, using ``*`` when possible.

    For example, if *dates* contains all days in June 2011, and
    *format* is ``'%Y/%m/%d'``, we return ``['2011/06/*']``

    Divisions smaller than a day (e.g. ``%H``) and time zone fields
    (e.g. ``%Z``) are always converted to ``*``.

    Currently, we only do something special with full months, years, and full
    ten-day periods (we don't glob weeks).

    :param dates: a sequence of :py:class:`datetime.date` objects
    :param format: a :py:func:`~datetime.date.strftime` format string (see http://docs.python.org/library/datetime.html#strftime-and-strptime-behavior)
    :return: a list of strings corresponding to strftime-formatted dates, using ``*`` wherever possible. These will be distinct (no duplicates) and in alphabetical order.
    """
    # handle special cases quickly
    if not dates:
        return []
    elif not '%' in format:
        # don't use STRFTIME_FIELD_RE to check because we want to catch
        # malformed format strings as well.
        return [format]

    results = set()

    # year globbing
    if not has_fields(format, YEAR_BAD_FIELDS):
        full_years, dates = extract_full_years(dates)
        if full_years:
            year_glob = glob_fields(format, YEAR_GLOB_FIELDS)
            for year in full_years:
                results.add(datetime.date(year, 1, 1).strftime(year_glob))

    # month globbing
    if not has_fields(format, MONTH_BAD_FIELDS):
        full_months, dates = extract_full_months(dates)
        if full_months:
            month_glob = glob_fields(format, MONTH_GLOB_FIELDS)
            for year, month in full_months:
                results.add(datetime.date(year, month, 1).strftime(month_glob))

    # tens globbing
    if not has_fields(format, MONTH_BAD_FIELDS):
        full_tens, dates = extract_full_tens(dates)
        if full_tens:
            for year, month, ten in full_tens:
                tens_glob = glob_fields(format, MONTH_GLOB_FIELDS, day_str=str(ten))
                results.add(datetime.date(year, month, 1).strftime(tens_glob))

    # everything else
    for day in dates:
        day_glob = glob_fields(format, TIME_FIELDS)
        results.add(day.strftime(day_glob))

    return sorted(results)


def has_fields(format, fields):
    """Check a format string for fields of a given type.
    :param format: a :py:func:`~datetime.date.strftime` format string
    :type fields: str
    :param fields: one-character field types to look for
    :rtype: bool
    """
    return bool(set(STRFTIME_FIELD_RE.findall(format)) & set(fields))


def glob_fields(format, fields, day_str=''):
    """Replace fields in a format string with ``*``. Adjacent stars (`**`)
    will be merged into a single star.

    :param format: a :py:func:`~datetime.date.strftime` format string
    :type fields: str
    :param fields: one-character field types to replace with ``*``
    :type day_str: str
    :param day_str: can be substituted with ten-day period prefix as str
    :rtype: bool
    """
    format = STRFTIME_FIELD_RE.sub(
        lambda m: '%s*' % day_str if m.group(1) in fields else m.group(0),
        format)
    format = MULTIPLE_WILDCARD_RE.sub('*', format)
    return format


def extract_full_years(dates):
    """Find if there are any years where every day of the year is in *dates*.

    Returns ``full_years, other_dates``: *years* is a list of year
    numbers that *dates* contains all the days of, and *other_dates* is
    everything else.
    """
    year_to_dates = defaultdict(set)
    for d in dates:
        year_to_dates[d.year].add(d)

    full_years = set()
    other_dates = set()

    for year, dates in year_to_dates.iteritems():
        year_len = 365 + int(calendar.isleap(year))
        if len(dates) >= year_len:
            full_years.add(year)
        else:
            other_dates.update(dates)

    return sorted(full_years), sorted(other_dates)


def extract_full_months(dates):
    """Find if there are any years where every day of the year is in *dates*.

    Returns ``full_months, other_dates``: *months* is a list of tuples
    of ``(year, month)`` for months that *dates* contains all the days of,
    and *other_dates* is everything else.
    """
    month_to_dates = defaultdict(set)
    for d in dates:
        month_to_dates[(d.year, d.month)].add(d)

    full_months = set()
    other_dates = set()

    for (year, month), dates in month_to_dates.iteritems():
        month_len = calendar.monthrange(year, month)[1]
        if len(dates) >= month_len:
            full_months.add((year, month))
        else:
            other_dates.update(dates)

    return sorted(full_months), sorted(other_dates)


def extract_full_tens(dates):
    """
    Find if there are any series of dates containing a full range of ten
    dates in *dates*, e.g. 2016-01-0* 2016-01-1* 2016-01-2* 2016-01-3*.

    :type dates: list
    :param dates: list of dates to find ten-day periods in.
    :return full_tens: a set of dates that can be globbed into ten-day periods
    :return other_dates: remaining dates that cannot be globbed
    """
    ten_to_dates = defaultdict(set)

    for d in dates:
        ten_to_dates[(d.year, d.month, which_ten(d))].add(d)

    full_tens = set()
    other_dates = set()

    for (year, month, ten), dates in ten_to_dates.iteritems():
        mr = calendar.monthrange(year, month)[1]
        if ten < 3 and len(dates) == TEN_LENGTH[ten]:
            full_tens.add((year, month, ten))
        elif ten == 3 and len(dates) == mr - 30 + 1:  # Handle 30+ days
            full_tens.add((year, month, ten))
        elif month == 2 and ten == 2 and len(dates) == mr - 20 + 1:  # Handle February
            full_tens.add((year, month, ten))
        else:
            other_dates.update(dates)

    return sorted(full_tens), sorted(other_dates)


def which_ten(d):
    """
    Determine which ten-day period a date falls in.

    :type d: datetime.date
    :param d: day of date, e.g. 2016-01-02 in format %Y-%m-%d is 2
    :return: an integer that is the prefix of the relevant ten-day period.
    """
    if not calendar.monthrange(d.year, d.month)[1] >= d.day > 0:
        raise RuntimeError('Out of range date')

    if d.day < 10:
        return 0
    elif d.day < 20:
        return 1
    elif d.day < 30:
        return 2
    else:
        return 3
