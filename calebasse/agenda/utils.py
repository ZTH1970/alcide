from interval import IntervalSet

def free_time(date, timetables, events):
    timetables = IntervalSet((t.to_interval(date) for t in timetables))
    events = IntervalSet((e.to_interval() for e in events))
    for free_time in timetables - events:
        yield free_time
