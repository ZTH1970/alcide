import sys
import calebasse.settings
import django.core.management
from datetime import datetime

django.core.management.setup_environ(calebasse.settings)

from calebasse.dossiers.models import PatientRecord
from calebasse.actes.models import Act

from django.db import transaction

@transaction.commit_manually
def main():
    print datetime.now()
    same_acts_set = []
    seen = []
    i = 0
    total = PatientRecord.objects.all().count()
    for patient in PatientRecord.objects.all():
        i += 1
        acts = Act.objects.filter(patient=patient)
        for act in acts:
            if not (patient.id, act.date, act.time, act.act_type) in seen:
                seen.append((patient.id, act.date, act.time, act.act_type))
                same_acts = Act.objects.filter(patient=patient, date=act.date, time=act.time, act_type=act.act_type)
                nb = same_acts.count()
                if nb > 1:
                    same_acts_set.append(same_acts)
        if not i % 100:
            percent  = int(round((float(i) / float(total)) * 100))
            out = '\r %20s [%s%s] %3d %%' % ("Recherche des doublons : ", '=' * percent, ' ' * (100 - percent), percent)
            sys.stdout.write(out)
            sys.stdout.flush()
    total = len(same_acts_set)
    i = 0
    for same_acts in same_acts_set:
        i += 1
        # Recherche du parent event
        parent_event_id = None
        for a in same_acts:
            if a.parent_event:
                if parent_event_id and parent_event_id != a.parent_event.id:
                    print "Il y a plusieurs evenement parent, bizarre"
                parent_event_id = a.parent_event.id
        keep = None
        for a in same_acts:
            state = a.get_state()
            if state and state.state_name != 'NON_VALIDE' and a.validation_locked == True:
                keep = a
                break
        if not keep:
            lockeds = same_acts.filter(validation_locked=True)
            if lockeds.count() >= 1:
                keep = lockeds[0]
            else:
                for a in same_acts:
                    state = a.get_state()
                    if state and state.state_name != 'NON_VALIDE':
                        keep = a
                        break
                if not keep:
                    keep = same_acts[0]
        if parent_event_id and not keep.parent_event:
            keep.parent_event_id = parent_event_id
            keep.save()
        acts_to_remove = same_acts.exclude(pk=keep.pk)
        for act in acts_to_remove:
            if act.parent_event:
                if act.parent_event.recurrence_periodicity:
                    print "attention, le parent de %d est un event periodique." % act.id
                elif act.parent_event != keep.parent_event:
                    act.parent_event.delete()
            act.delete()
        if not i % 100:
            percent  = int(round((float(i) / float(total)) * 100))
            out = '\r %20s [%s%s] %3d %%' % ("Traitement des doublons : ", '=' * percent, ' ' * (100 - percent), percent)
            sys.stdout.write(out)
            sys.stdout.flush()
    transaction.commit()
    print "Nb de doublons traites: %d" % total
    print datetime.now()

if __name__ == "__main__":
    main()
