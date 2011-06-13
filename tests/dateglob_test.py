from datetime import date, timedelta

from testify import TestCase
from testify import assert_equal
from testify import run

import dateglob

class TestREADME(TestCase):

    def test_readme_is_correct(self):
        dates = [date(2009, 12, 31) + timedelta(i) for i in xrange(1+365+31+1)]
        assert_equal(dateglob.strftime(dates, '%Y-%m-%d'),
                     ['2009-12-31', '2010-*-*', '2011-01-*', '2011-02-01'])

if __name__ == '__main__':
    run()
