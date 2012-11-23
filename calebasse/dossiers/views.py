
from calebasse.cbv import ListView
from calebasse.agenda.models import Occurrence
from calebasse.dossiers.models import PatientRecord
from calebasse.dossiers.forms import SearchForm
from calebasse.dossiers.states import STATES_MAPPING

class DossiersHomepageView(ListView):
    model = PatientRecord
    template_name = 'dossiers/index.html'

    def get_queryset(self):
        qs = super(DossiersHomepageView, self).get_queryset()
        first_name = self.request.GET.get('first_name')
        last_name = self.request.GET.get('last_name')
        paper_id = self.request.GET.get('paper_id')
        states = self.request.GET.getlist('states')
        social_security_id = self.request.GET.get('social_security_id')
        if last_name:
            qs = qs.filter(last_name__icontains=last_name)
        if first_name:
            qs = qs.filter(first_name__icontains=first_name)
        if paper_id:
            qs = qs.filter(paper_id__contains=paper_id)
        if social_security_id:
            qs = qs.filter(social_security_id__contains=social_security_id)
        if states:
            pass
        return qs

    def get_context_data(self, **kwargs):
        ctx = super(DossiersHomepageView, self).get_context_data(**kwargs)
        ctx['search_form'] = SearchForm(data=self.request.GET or None)
        ctx['patient_records'] = []
        ctx['stats'] = {"dossiers": 0,
                "En_contact": 0,
                "Fin_daccueil": 0,
                "Diagnostic": 0,
                "Traitement": 0,
                "Clos": 0}
        if self.request.GET:
            for patient_record in ctx['object_list'].filter():
                ctx['stats']['dossiers'] += 1
                next_rdv = {}
                occurrence = Occurrence.objects.next_appoinment(patient_record)
                if occurrence:
                    next_rdv['start_datetime'] = occurrence.start_time
                    next_rdv['participants'] = occurrence.event.participants.all()
                    next_rdv['act_type'] = occurrence.event.eventact.act_type
                occurrence = Occurrence.objects.last_appoinment(patient_record)
                last_rdv = {}
                if occurrence:
                    last_rdv['start_datetime'] = occurrence.start_time
                    last_rdv['participants'] = occurrence.event.participants.all()
                    last_rdv['act_type'] = occurrence.event.eventact.act_type
                occurrence = Occurrence.objects.next_appoinment(patient_record)
                if STATES_MAPPING.has_key(patient_record.last_state.status.type):
                    state = STATES_MAPPING[patient_record.last_state.status.type]
                else:
                    state = patient_record.last_state.status.name
                ctx['patient_records'].append(
                        {
                            'object': patient_record,
                            'next_rdv': next_rdv,
                            'last_rdv': last_rdv,
                            'state': state
                            }
                        )
                state = state.replace(' ', '_')
                state = state.replace("'", '')
                if not ctx['stats'].has_key(state):
                    ctx['stats'][state] = 0
                ctx['stats'][state] += 1

        return ctx

