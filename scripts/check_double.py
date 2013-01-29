# -*- coding: utf-8 -*-
import sys
import calebasse.settings
import django.core.management
from datetime import datetime
import csv

django.core.management.setup_environ(calebasse.settings)

from calebasse.dossiers.models import PatientRecord
from calebasse.actes.models import Act

from django.db import transaction

@transaction.commit_manually
def main():
    print datetime.now()
    f = open('./scripts/actes_to_modify.csv', 'wb')
    writer = csv.writer(f, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['id_act_keep', 'locked', 'billed', 'lost', 'switch', 'pause', 'comment'])

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
        if patient.last_name == 'Mazoyer' and patient.first_name == 'Manon':
            for a in same_acts_set[len(same_acts_set)-1]:
                print a
                print a.get_state()
                print a.is_billed
    total = len(same_acts_set)
    i = 0
    for same_acts in same_acts_set:
        i += 1
        # Recherche du parent event
        parent_event_id = None
        for a in same_acts:
            if a.parent_event:
#                if parent_event_id and parent_event_id != a.parent_event.id:
#                    print "Il y a plusieurs evenement parent, bizarre"
                parent_event_id = a.parent_event.id
        keep = None
        should = None
        for a in same_acts:
            state = a.get_state()
            if state and state.state_name == 'VALIDE' and a.validation_locked == True:
                should = a
                break
        for a in same_acts:
            state = a.get_state()
            if state and state.state_name != 'NON_VALIDE' and a.validation_locked == True:
                keep = a
                break
        if should and keep and should != keep:
            writer.writerow([str(keep.id), str(should.validation_locked), str(should.is_billed), str(should.is_lost), str(should.switch_billable), str(should.pause), str(should.comment)])
            print "%s aurait du etre valide, facture: %s" % (keep, str(keep.is_billed))
        if not keep:
            lockeds = same_acts.filter(validation_locked=True)
            if lockeds.count() >= 1:
                keep = lockeds[0]
            else:
                for a in same_acts:
                    state = a.get_state()
                    if state and state.state_name == 'VALIDE':
                        should = a
                        break
                for a in same_acts:
                    state = a.get_state()
                    if state and state.state_name != 'NON_VALIDE':
                        keep = a
                        break
                if should and keep and should != keep:
                    writer.writerow([str(keep.id), str(should.validation_locked), str(should.is_billed), str(should.is_lost), str(should.switch_billable), str(should.pause), str(should.comment)])
                    print "Non verr, %s aurait du etre valide, facture: %s" % (keep, str(keep.is_billed))
                if not keep:
                    keep = same_acts[0]
        if parent_event_id and not keep.parent_event:
            keep.parent_event_id = parent_event_id
            keep.save()
        acts_to_remove = same_acts.exclude(pk=keep.pk)
        for act in acts_to_remove:
            if act.parent_event:
                if act.parent_event.recurrence_periodicity:
                    pass#print "attention, le parent de %d est un event periodique." % act.id
                elif act.parent_event != keep.parent_event:
                    act.parent_event.delete()
            if act.is_billed:
                print "Suppresion de l'acte facture %s" % act
            act.delete()
        if not i % 100:
            percent  = int(round((float(i) / float(total)) * 100))
            out = '\r %20s [%s%s] %3d %%' % ("Traitement des doublons : ", '=' * percent, ' ' * (100 - percent), percent)
            sys.stdout.write(out)
            sys.stdout.flush()
    transaction.rollback()#commit()
    print "Nb de doublons traites: %d" % total
    print datetime.now()

if __name__ == "__main__":
    main()
