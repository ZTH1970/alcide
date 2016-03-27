import django.core.management
import alcide.settings

django.core.management.setup_environ(alcide.settings)

from alcide.facturation.models import Invoice

if __name__ == "__main__":
    for invoice in Invoice.objects.all():
        if invoice.acts.count() > 0:
            acts = invoice.acts.order_by('date')
            invoice.first_tag = acts[0].get_hc_tag()
            if not invoice.first_tag:
                print 'Facture %s avec actes de type indetermine' % invoice.number
            invoice.list_dates = '$'.join([act.date.strftime('%d/%m/%Y') for act in acts])
            invoice.save()
        else:
            print 'Facture %s sans actes' % invoice.number
