
class QuerysetIndex(object):
    '''Create simple index of objects in a queryset'''
    def __init__(self, qs, *keywords):
        for keyword in keywords:
            setattr(self, 'by_' + keyword, dict())
        for obj in qs:
            for keyword in keywords:
                getattr(self, 'by_' + keyword)[getattr(obj, keyword)] = obj

def _to_datetime(str_date):
    if not str_date:
        return None
    return datetime.strptime(str_date[:19], "%Y-%m-%d %H:%M:%S")

def _to_date(str_date):
    dt = _to_datetime(str_date)
    return dt and dt.date()

def _to_time(str_date):
    dt = _to_datetime(str_date)
    return dt and dt.time()

def _to_duration(str_date):
    dt = _to_datetime(str_date)
    if dt is None:
        return timedelta(minutes=15)
    return dt - datetime(1900, 01, 01, 0, 0)

def _get_dict(cols, line):
    res = {}
    for i, data in enumerate(line):
        res[cols[i]] = data.decode('utf-8')
    return res

