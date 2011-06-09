# Copyright 2011 Yelp
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
"""Convert a set of dates to a compact list of globs, using strftime() format.

This library was designed for a specific use case, which was to express the
paths to several months of log files using as few globs as possible, so as
not to bump up against limits on maximum length of a command line.

You may find it useful for other tasks as well!
"""
import calendar
from collections import defaultdict
import datetime
import re

__author__ = 'David Marin <dave@yelp.com>'

__version__ = '0.1.0'

# match directives in a strftime format string (e.g. '%Y-%m-%d')
STRFTIME_FIELD_RE = re.compile('%(.)')

# used to compact multiple adjacent wildcards into a single wildcard.
MULTIPLE_WILDCARD_RE = re.compile(r'\*+')

# all fields handled by the default version of strftime; see
# http://docs.python.org/library/datetime.html#strftime-and-strptime-behavior

# divisions smaller than a day and time zones; always converted to *
TIME_FIELDS = 'fHIpSXzZ'

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
MONTH_BAD_FIELDS = (DAY_OF_YEAR_FIELDS +
                    SUNDAY_WEEK_OF_YEAR_FIELDS +
                    MONDAY_WEEK_OF_YEAR_FIELDS)


def strftime(dates, format):
    """Format a sequence of dates, using globs when possible.

    For example, if *dates* contained all days in June 2011, and
    *format* were ``'%Y/%m/%d'``, we could return ``['2011/06/*']``

    Divisions smaller than a day (e.g. ``%H``) are always converted to ``*``.

    Currently, we only do something special if we have all days in a month
    or a year (we don't handle week-in-year globbing).

    :param dates: a sequence of :py:class:`datetime.date`s
    :param format: a :py:func:`~datetime.date.strftime` format string
    :rtype: list of str
    """
    # handle special cases quickly
    if not dates:
        return []
    elif not STRFTIME_FIELD_RE.match(format):
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

    # everything else
    for day in dates:
        results.add(day.strftime(format))

    return sorted(results)
    

def has_fields(format, fields):
    """Check a format string for fields of a given type.

    :param format: a :py:func:`~datetime.date.strftime` format string
    :type fields: str
    :param fields: one-character field types to look for
    :rtype: bool
    """
    return bool(set(STRFTIME_FIELD_RE.findall(format)) & set(fields))


def glob_fields(format, fields):
    """Replace fields in a format string with ``*``. Adjacent stars (`**`)
    will be merged into a single star.

    :param format: a :py:func:`~datetime.date.strftime` format string
    :type fields: str
    :param fields: one-character field types to replace with ``*``
    :rtype: bool
    """
    format = STRFTIME_FIELD_RE.sub(
        lambda m: '*' if m.group(1) in fields else m.group(0),
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
        year_len = 365 + (1 if calendar.isleap(year) else 0)
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

