
class QuerysetIndex(object):
    '''Create simple index of objects in a queryset'''
    def __init__(self, qs, *keywords):
        for keyword in keywords:
            setattr(self, 'by_' + keyword, dict())
        for obj in qs:
            for keyword in keywords:
                getattr(self, 'by_' + keyword)[getattr(obj, keyword)] = obj
