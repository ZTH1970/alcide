
from datetime import datetime

from django.views.generic.edit import DeleteView
from django.core.urlresolvers import reverse_lazy

from calebasse import cbv
from calebasse.agenda.models import Occurrence
from calebasse.dossiers.models import PatientRecord, Status, FileState, create_patient
from calebasse.dossiers.forms import (SearchForm, CivilStatusForm, StateForm,
        PhysiologyForm, FamillyForm, InscriptionForm, GeneralForm,
        NewPatientRecordForm)
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

class NewPatientRecordView(cbv.FormView, cbv.ServiceViewMixin,):
    form_class = NewPatientRecordForm
    template_name = 'dossiers/patientrecord_new.html'
    success_url = '..'

    def post(self, request, *args, **kwarg):
        self.user = request.user
        return super(NewPatientRecordView, self).post(request, *args, **kwarg)

    def form_valid(self, form):
        create_patient(form.data['first_name'], form.data['last_name'], self.service,
                self.user)
        return super(NewPatientRecordView, self).form_valid(form)

new_patient_record = NewPatientRecordView.as_view()

class StateFormView(cbv.FormView):
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


class PatientRecordView(cbv.ServiceViewMixin, cbv.MultiUpdateView):
    model = PatientRecord
    forms_classes = {
            'general': GeneralForm,
            'id': CivilStatusForm,
            'physiology': PhysiologyForm,
            'inscription': InscriptionForm,
            'familly': FamillyForm,
            }
    template_name = 'dossiers/patientrecord_update.html'
    success_url = './view'

    def get_success_url(self):
        if self.request.POST.has_key('tab'):
            return self.success_url + '#tab=' + self.request.POST['tab']
        else:
            return self.success_url

    def get_context_data(self, **kwargs):
        ctx = super(PatientRecordView, self).get_context_data(**kwargs)
        ctx['next_rdv'] = get_next_rdv(ctx['object'])
        ctx['last_rdv'] = get_last_rdv(ctx['object'])
        current_state = ctx['object'].get_current_state()
        if STATES_MAPPING.has_key(current_state.status.type):
            state = STATES_MAPPING[current_state.status.type]
        else:
            state = current_state.status.name
        ctx['current_state'] = current_state
        ctx['service_id'] = self.service.id
        ctx['states'] = FileState.objects.filter(patient=self.object).filter(status__services=self.service)
        return ctx

patient_record = PatientRecordView.as_view()

class PatientRecordsHomepageView(cbv.ListView):
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
            status_types = ['BILAN', 'SURVEILLANCE', 'SUIVI']
            for state in states:
                status_types.append(STATE_CHOICES_TYPE[state])
            qs = qs.filter(last_state__status__type__in=status_types)
        else:
            qs = qs.filter(last_state__status__type__in="")
        qs = qs.filter(service=self.service)
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
                current_state = patient_record.get_current_state()
                if STATES_MAPPING.has_key(current_state.status.type):
                    state = STATES_MAPPING[current_state.status.type]
                else:
                    state = current_state.status.name
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

class PatientRecordDeleteView(DeleteView):
    model = PatientRecord
    success_url = ".."
    template_name = 'dossiers/patientrecord_confirm_delete.html'

patientrecord_delete = PatientRecordDeleteView.as_view()

