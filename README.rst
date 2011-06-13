``dateglob`` converts a set of dates into a list of globs, trying to use as 
few globs as possible. For example:

>>> import dateglob; from datetime import date, timedelta
>>> dates = [date(2009, 12, 31) + timedelta(i) for i in xrange(1+365+31+1)]
>>> dateglob.strftime(dates, '%Y-%m-%d')
['2009-12-31', '2010-*-*', '2011-01-*', '2011-02-01']

The original use case for this library was to generate compact command lines
for command that take daily log files as input, for example:

>>> args += dateglob.strftime(dates, '/logs/foo/%Y/%m/%d/*.gz')

Currently, ``datetime`` handles all of the standard arguments to ``datetime.strftime()``, and tries to use globs when you have all dates in 
a month or year.

* source: <http://github.com/Yelp/dateglob>
* documentation: <http://packages.python.org/dateglob/>

