import sys
import calebasse.settings
import django.core.management
from datetime import datetime

django.core.management.setup_environ(calebasse.settings)

from django.db import transaction
from calebasse.actes.models import Act

@transaction.commit_manually
def main():
    print datetime.now()
    total = Act.objects.all().count()
    i = 0
    for a in Act.objects.all():
        i += 1
        try:
            state = a.actvalidationstate_set.latest('created')
            if state.state_name == 'VALIDE':
                a.valide = True
                a.save()
        except:
            pass
        if not i % 100:
            percent  = int(round((float(i) / float(total)) * 100))
            out = '\r %20s [%s%s] %3d %%' % ("Actes traites : ", '=' * percent, ' ' * (100 - percent), percent)
            sys.stdout.write(out)
            sys.stdout.flush()
    transaction.commit()
    print datetime.now()

if __name__ == "__main__":
    main()
