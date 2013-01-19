import calebasse.settings
import django.core.management

django.core.management.setup_environ(calebasse.settings)

from calebasse.dossiers.models import PatientRecord
from calebasse.actes.models import Act

def main():
    seen = []
    i = 0
    for patient in PatientRecord.objects.all():
        acts = Act.objects.filter(patient=patient)
        for act in acts:
            if not (patient.id, act.date, act.time) in seen:
                seen.append((patient.id, act.date, act.time))
                same_acts = Act.objects.filter(patient=patient, date=act.date, time=act.time)
                nb = same_acts.count()
                if nb > 1:
                    keep = None
                    for a in same_actes:
                        state = a.get_state()
                        if state and state.name != 'NON_VALIDE' and a.validation_locked == True:
                            keep = a
                            break
                    if not keep:
                        lockeds = same_acts.filter(validation_locked=True)
                        if lockeds.count() >= 1:
                            keep = lockeds[0]
                        else:
                            keep = same_acts[0]
                    same_acts.exclude(pk=keep.pk).delete()
                    i += 1
    print "Nb actes redondants traites: %d" % i

if __name__ == "__main__":
    main()
