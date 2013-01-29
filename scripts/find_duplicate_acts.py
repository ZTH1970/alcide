#!/usr/bin/env python
import sys
import os
import datetime as dt
from collections import defaultdict

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "calebasse.settings")

from django.db import transaction

@transaction.commit_on_success
def main():
    from calebasse.actes.validation import get_days_with_acts_not_locked
    from calebasse.actes.models import Act

    doubles = defaultdict(lambda: set())
    days_with_acts_not_locked = get_days_with_acts_not_locked(dt.date(2010,1,1), dt.date.today())
    acts = Act.objects.filter(date__in=days_with_acts_not_locked) \
            .order_by('time') \
            .prefetch_related('doctors', 'patient__service')
    for act in acts:
        participants_id = [doctor.id for doctor in act.doctors.all()]
        key = (act.date, act.patient_id, act.act_type_id, tuple(sorted(participants_id)))
        doubles[key].add(act)
    for key in doubles.keys():
        if len(doubles[key]) < 2:
            del doubles[key]
    date = None
    total = 0
    for key in sorted(doubles.iterkeys()):
        for act in doubles[key]:
            if not act.validation_locked:
                break
        else:
            continue
        if key[0] != date:
            if date is not None:
                print
            date = key[0]
            print ' = Acte en double le ', date, '='
            print '{:>6} {:>6} {:>6} {:>6} {:>6} {:>6} {:>6}'.format('act_id', 'ev_id', 'exc_id', 'old_id', 'rr_id', 'rs_id', 'heure')
            for act in sorted(doubles[key]):
                total += 1
                exception_to = ''
                rr_id = ''
                rs_id = ''
                if act.parent_event:
                    exception_to = act.parent_event.exception_to_id
                    rr_id = act.parent_event.old_rr_id or ''
                    rs_id = act.parent_event.old_rs_id or ''
                print '%06d' % act.id, '%6s' % act.parent_event_id, '%6s' % exception_to, '%6s' % act.old_id, '%6s' % rr_id, '%6s' % rs_id, \
                        '%6s' % act.time.strftime('%H:%M'), act, act.validation_locked, act.actvalidationstate_set.all(), act.patient.service.slug
            print
            if '--delete' in sys.argv:
                x = raw_input('Delete non locked acts ?')
                if x.lower() == 'y':
                    for act in doubles[key]:
                        if not act.validation_locked:
                            print 'Deleted act', act.id
                            act.delete()
    print 'Total', total, 'actes'

if __name__ == "__main__":
    main()
