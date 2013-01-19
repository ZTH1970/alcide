from calebasse.dossiers.models import PatientRecord
from calebasse.actes.models import Act

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
                i += 1
                print nb
                j = 0
                print "Valide : %d" % same_acts.filter(valide=True).count()
                print "Locked : %d" % same_acts.filter(validation_locked=True).count()
print "Nb actes redondants : %d" % i
