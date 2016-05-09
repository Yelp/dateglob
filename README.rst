dateglob
========

``dateglob`` converts a set of dates into a list of globs. For example:

>>> import dateglob; from datetime import date, timedelta
>>> # build list of dates from 2009-12-31 thru 2011-02-01
>>> dates = [date(2009, 12, 31) + timedelta(i) for i in xrange(1+365+31+1)]
>>> dateglob.strftime(dates, '%Y-%m-%d')
['2009-12-31', '2010-*-*', '2011-01-*', '2011-02-01']

The original use case for this library was to generate compact command lines
for command that take daily log files as input, for example:

>>> args += dateglob.strftime(dates, '/logs/foo/%Y/%m/%d/*.gz')

``dateglob.strftime()`` handles all of the standard arguments to ``datetime.strftime()``. Currently, it only does something special with
full months, years, and full ten-day periods (we don't glob weeks).

* source: <http://github.com/Yelp/dateglob>
* documentation: <http://packages.python.org/dateglob/>
* datetime.strftime(): <http://docs.python.org/library/datetime.html#strftime-and-strptime-behavior>
