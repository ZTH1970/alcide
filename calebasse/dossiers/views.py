
from datetime import datetime

from calebasse.cbv import ListView, MultiUpdateView, FormView, ServiceViewMixin
from calebasse.agenda.models import Occurrence
from calebasse.dossiers.models import PatientRecord, Status, FileState
from calebasse.dossiers.forms import SearchForm, CivilStatusForm, StateForm, PhysiologyForm
from calebasse.dossiers.states import STATES_MAPPING, STATE_CHOICES_TYPE
from calebasse.ressources.models import Service


def get_next_rdv(patient_record):
    next_rdv = {}
    occurrence = Occurrence.objects.next_appoinment(patient_record)
    if occurrence:
        next_rdv['start_datetime'] = occurrence.start_time
        next_rdv['participants'] = occurrence.event.participants.all()
        next_rdv['act_type'] = occurrence.event.eventact.act_type
    return next_rdv

def get_last_rdv(patient_record):
    last_rdv = {}
    occurrence = Occurrence.objects.last_appoinment(patient_record)
    if occurrence:
        last_rdv['start_datetime'] = occurrence.start_time
        last_rdv['participants'] = occurrence.event.participants.all()
        last_rdv['act_type'] = occurrence.event.eventact.act_type
    return last_rdv

class StateFormView(FormView):
    template_name = 'dossiers/state.html'
    form_class = StateForm
    success_url = '..'

    def post(self, request, *args, **kwarg):
        self.user = request.user
        return super(StateFormView, self).post(request, *args, **kwarg)

    def form_valid(self, form):
        service = Service.objects.get(id=form.data['service_id'])
        status = Status.objects.filter(services=service).filter(type=form.data['state_type'])
        patient = PatientRecord.objects.get(id=form.data['patient_id'])
        date_selected = datetime.strptime(form.data['date'], "%d/%m/%Y")
        patient.set_state(status[0], self.user, date_selected, form.data['comment'])
        return super(StateFormView, self).form_valid(form)

state_form = StateFormView.as_view()


class PatientRecordView(ServiceViewMixin, MultiUpdateView):
    """
    """
    model = PatientRecord
    forms_classes = {
            'id': CivilStatusForm,
            'physiology': PhysiologyForm
            }
    template_name = 'dossiers/patientrecord_update.html'
    success_url = './view'

    def get_context_data(self, **kwargs):
        ctx = super(PatientRecordView, self).get_context_data(**kwargs)
        ctx['next_rdv'] = get_next_rdv(ctx['object'])
        ctx['last_rdv'] = get_last_rdv(ctx['object'])
        ctx['service_id'] = self.service.id
        ctx['states'] = FileState.objects.filter(patient=self.object).filter(status__services=self.service)
        return ctx

patient_record = PatientRecordView.as_view()

class PatientRecordsHomepageView(ListView):
    model = PatientRecord
    template_name = 'dossiers/index.html'

    def get_queryset(self):
        qs = super(PatientRecordsHomepageView, self).get_queryset()
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
            status_types = []
            for state in states:
                status_types.append(STATE_CHOICES_TYPE[state])
            qs = qs.filter(last_state__status__type__in=status_types)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super(PatientRecordsHomepageView, self).get_context_data(**kwargs)
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
                next_rdv = get_next_rdv(patient_record)
                last_rdv = get_last_rdv(patient_record)
                if STATES_MAPPING.has_key(patient_record.last_state.status.type):
                    state = STATES_MAPPING[patient_record.last_state.status.type]
                else:
                    state = patient_record.last_state.status.name
                state_class = patient_record.last_state.status.type.lower()
                ctx['patient_records'].append(
                        {
                            'object': patient_record,
                            'next_rdv': next_rdv,
                            'last_rdv': last_rdv,
                            'state': state,
                            'state_class': state_class
                            }
                        )
                state = state.replace(' ', '_')
                state = state.replace("'", '')
                if not ctx['stats'].has_key(state):
                    ctx['stats'][state] = 0
                ctx['stats'][state] += 1

        return ctx

patientrecord_home = PatientRecordsHomepageView.as_view()

