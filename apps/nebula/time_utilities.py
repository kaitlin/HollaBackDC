from datetime import tzinfo, timedelta, datetime, date
import time

ZERO = timedelta(0)
EPOCHORDINAL = datetime.utcfromtimestamp(0).toordinal()

# A UTC class.

class UTC(tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO

class TZLocal(tzinfo):
    # copied from dateutil.tz
    _std_offset = timedelta(seconds=-time.timezone)
    if time.daylight:
        _dst_offset = timedelta(seconds=-time.altzone)
    else:
        _dst_offset = _std_offset

    def utcoffset(self, dt):
        if self._isdst(dt):
            return self._dst_offset
        else:
            return self._std_offset

    def dst(self, dt):
        if self._isdst(dt):
            return self._dst_offset-self._std_offset
        else:
            return ZERO

    def tzname(self, dt):
        return time.tzname[self._isdst(dt)]

    def _isdst(self, dt):
        # We can't use mktime here. It is unstable when deciding if
        # the hour near to a change is DST or not.
        #
        # timestamp = time.mktime((dt.year, dt.month, dt.day, dt.hour,
        #                         dt.minute, dt.second, dt.weekday(), 0, -1))
        # return time.localtime(timestamp).tm_isdst
        #
        # The code above yields the following result:
        #
        #>>> import tz, datetime
        #>>> t = tz.tzlocal()
        #>>> datetime.datetime(2003,2,15,23,tzinfo=t).tzname()
        #'BRDT'
        #>>> datetime.datetime(2003,2,16,0,tzinfo=t).tzname()
        #'BRST'
        #>>> datetime.datetime(2003,2,15,23,tzinfo=t).tzname()
        #'BRST'
        #>>> datetime.datetime(2003,2,15,22,tzinfo=t).tzname()
        #'BRDT'
        #>>> datetime.datetime(2003,2,15,23,tzinfo=t).tzname()
        #'BRDT'
        #
        # Here is a more stable implementation:
        #
        timestamp = ((dt.toordinal() - EPOCHORDINAL) * 86400
                     + dt.hour * 3600
                     + dt.minute * 60
                     + dt.second)
        return time.localtime(timestamp+time.timezone).tm_isdst

    def __eq__(self, other):
        if not isinstance(other, tzlocal):
            return False
        return (self._std_offset == other._std_offset and
                self._dst_offset == other._dst_offset)
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "%s()" % self.__class__.__name__

    __reduce__ = object.__reduce__

utc = UTC()
tzlocal = TZLocal()

def time_to_datetime(t, tz=None):
    if tz is None:
        tz = utc
    if not isinstance(t, datetime):
        year, month, day, hour, minute, second, wday, yday, isdst = t
        t = datetime(year, month, day, hour, minute, second, 0, utc)
        return t.astimezone(tz)
    else:
        return t

def get_next_prev(the_date):
    now = date.today()
    if the_date.month >= 12:
        next_month = 1
        next_year = the_date.year + 1
    else:
        next_month = the_date.month + 1
        next_year = the_date.year

    if the_date.month <= 1:
        prev_month = 12
        prev_year = the_date.year - 1
    else:
        prev_month = the_date.month - 1
        prev_year = the_date.year

    if the_date.month == now.month and the_date.year == now.year:
        next_month_dt = now
    else:
        next_month_dt = date(next_year, next_month, 1)
    prev_month_dt = date(prev_year, prev_month, 1)

    return next_month_dt, prev_month_dt

def days_in_month(year,month):
    year = str(year)
    if isinstance(month, unicode):
       month = convert_short_month_to_int(month)
    year = int(year)
    if (month+1) >= 12:
        month = 1
        year += 1
    else:
        month += 1
    return (date(year, month+1, 1) - timedelta(days=1)).day

def get_now():
    now = date.today()
    current_month = now.month
    current_year = now.year
    current_day = now.day
    return now, current_year, current_month, current_day

def convert_short_month_to_int(month):
    if isinstance(month, unicode):
       return int(date(*time.strptime(month, '%b')[:3]).month)
