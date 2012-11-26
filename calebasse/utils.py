from datetime import timedelta, datetime

__EPOCH = datetime(day=5,month=1,year=1970)

def __date_to_datetime(date):
    return datetime(date.year, date.month, date.day)

def weeks_since_epoch(date):
    days_since_epoch = (__date_to_datetime(date) - __EPOCH).days
    return days_since_epoch // 7

def weekday_ranks(date):
    '''Returns n so that if date occurs on a certain weekday, this is the
    n-th weekday of the month counting from 0. Also return 4 if this the
    last suck weekday of the month. '''
    n = 0
    month = date.month
    i = date - timedelta(days=7)
    while i.month == month:
        n += 1
        i = i - timedelta(days=7)
    if (date+timedelta(days=7)).month != month and n != 4:
        return n, 4
    else:
        return n,
