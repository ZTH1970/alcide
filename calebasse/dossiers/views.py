
from calebasse.cbv import ListView
from calebasse.agenda.models import Occurrence
from calebasse.dossiers.models import PatientRecord
from calebasse.dossiers.forms import SearchForm

class DossiersHomepageView(ListView):
    model = PatientRecord
    template_name = 'dossiers/index.html'

    def get_queryset(self):
        qs = super(DossiersHomepageView, self).get_queryset()
        first_name = self.request.GET.get('first_name')
        last_name = self.request.GET.get('last_name')
        paper_id = self.request.GET.get('paper_id')
        social_security_id = self.request.GET.get('social_security_id')
        if last_name:
            qs = qs.filter(last_name__icontains=last_name)
        if first_name:
            qs = qs.filter(first_name__icontains=first_name)
        if paper_id:
            qs = qs.filter(paper_id__contains=paper_id)
        if social_security_id:
            qs = qs.filter(social_security_id__contains=social_security_id)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super(DossiersHomepageView, self).get_context_data(**kwargs)
        ctx['patient_records'] = []
        if self.request.GET:
            for patient_record in ctx['object_list'].filter():
                next_rdv = {}
                occurrence = Occurrence.objects.next_appoinment(patient_record)
                next_rdv['start_datetime'] = occurrence.start_time
                next_rdv['participants'] = occurrence.event.participants.all()
                ctx['patient_records'].append(
                        {
                            'object': patient_record,
                            'next_rdv': next_rdv
                            }
                        )

        return ctx

