# -*- coding: utf-8 -*-

import os

from datetime import datetime, date

from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.db import models
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import View
from django.views.generic.edit import DeleteView, FormMixin
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files import File
from django.forms import Form
from django.utils import formats

from calebasse import cbv
from calebasse.doc_templates import make_doc_from_template
from calebasse.dossiers import forms
from calebasse.dossiers.transport import render_transport
from calebasse.agenda.models import Event, EventWithAct
from calebasse.actes.models import Act
from calebasse.agenda.appointments import Appointment
from calebasse.dossiers.models import (PatientRecord, PatientContact,
        PatientAddress, Status, FileState, create_patient, CmppHealthCareTreatment,
        CmppHealthCareDiagnostic, SessadHealthCareNotification, HealthCare,
        TransportPrescriptionLog)
from calebasse.dossiers.states import STATES_MAPPING, STATE_CHOICES_TYPE, STATES_BTN_MAPPER
from calebasse.ressources.models import (Service,
    SocialisationDuration, MDPHRequest, MDPHResponse)
from calebasse.facturation.list_acts import list_acts_for_billing_CMPP_2_per_patient

from calebasse.decorators import validator_only

def get_next_rdv(patient_record):
    Q = models.Q
    today = date.today()
    qs = EventWithAct.objects.filter(patient=patient_record) \
            .filter(exception_to__isnull=True, canceled=False) \
            .filter(Q(start_datetime__gte=today) \
            |  Q(exceptions__isnull=False) \
            | ( Q(recurrence_periodicity__isnull=False) \
            & (Q(recurrence_end_date__gte=today) \
            | Q(recurrence_end_date__isnull=True) \
            ))) \
            .distinct() \
            .select_related() \
            .prefetch_related('participants', 'exceptions__eventwithact')
    occurrences = []
    for event in qs:
        occurrences.extend(filter(lambda e: e.start_datetime.date() >= today, event.all_occurences(limit=180)))
    occurrences = sorted(occurrences, key=lambda e: e.start_datetime)
    if occurrences:
        return occurrences[0]
    else:
        return None

def get_last_rdv(patient_record):
    last_rdv = {}
    event = Event.objects.last_appointment(patient_record)
    if event:
        last_rdv['start_datetime'] = event.start_datetime
        last_rdv['participants'] = event.participants.all()
        last_rdv['act_type'] = event.eventwithact.act_type
        last_rdv['act_state'] = event.act.get_state()
        last_rdv['is_absent'] = event.is_absent()
    return last_rdv

class NewPatientRecordView(cbv.FormView, cbv.ServiceViewMixin):
    form_class = forms.NewPatientRecordForm
    template_name = 'dossiers/patientrecord_new.html'
    success_url = '..'
    patient = None

    def post(self, request, *args, **kwarg):
        self.user = request.user
        return super(NewPatientRecordView, self).post(request, *args, **kwarg)

    def form_valid(self, form):
        self.patient = create_patient(form.data['first_name'], form.data['last_name'], self.service,
                self.user, date_selected=datetime.strptime(form.data['date_selected'], "%d/%m/%Y"))
        return super(NewPatientRecordView, self).form_valid(form)

    def get_success_url(self):
        return '%s/view' % self.patient.id

new_patient_record = NewPatientRecordView.as_view()

class RecordPatientRecordIdMixing(object):
    def dispatch(self, request, *args, **kwargs):
        self.patientrecord_id = request.session['patientrecord_id'] = int(kwargs['patientrecord_id'])
        return super(RecordPatientRecordIdMixing, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(RecordPatientRecordIdMixing, self).get_form_kwargs()
        kwargs['patient'] = PatientRecord.objects.get(id=self.patientrecord_id)
        return kwargs

class NewPatientContactView(RecordPatientRecordIdMixing, cbv.CreateView):
    model = PatientContact
    form_class = forms.PatientContactForm
    template_name = 'dossiers/patientcontact_new.html'
    success_url = '../view#tab=2'

new_patient_contact = NewPatientContactView.as_view()

class UpdatePatientContactView(RecordPatientRecordIdMixing, cbv.UpdateView):
    model = PatientContact
    form_class = forms.PatientContactForm
    template_name = 'dossiers/patientcontact_new.html'
    success_url = '../../view#tab=2'

update_patient_contact = UpdatePatientContactView.as_view()

class DeletePatientContactView(cbv.DeleteView):
    model = PatientContact
    form_class = forms.PatientContactForm
    template_name = 'dossiers/patientcontact_confirm_delete.html'
    success_url = '../../view#tab=2'

    def post(self, request, *args, **kwargs):
        try:
            patient = PatientRecord.objects.get(id=kwargs.get('pk'))
        except PatientRecord.DoesNotExist:
            return super(DeletePatientContactView, self).post(request, *args, **kwargs)
        # the contact is also a patient record; it shouldn't be deleted; just
        # altered to remove an address
        patient.addresses.remove(self.request.GET['address'])
        return HttpResponseRedirect(self.get_success_url())

delete_patient_contact = DeletePatientContactView.as_view()

class NewPatientAddressView(cbv.CreateView):
    model = PatientAddress
    form_class = forms.PatientAddressForm
    template_name = 'dossiers/patientaddress_new.html'
    success_url = '../view#tab=2'

    def get_success_url(self):
        return self.success_url

    def form_valid(self, form):
        patientaddress = form.save()
        patientrecord = PatientRecord.objects.get(id=self.kwargs['patientrecord_id'])
        patientrecord.addresses.add(patientaddress)
        messages.add_message(self.request, messages.INFO, u'Nouvelle adresse enregistrée avec succès.')
        return HttpResponseRedirect(self.get_success_url())

new_patient_address = NewPatientAddressView.as_view()

class UpdatePatientAddressView(cbv.UpdateView):
    model = PatientAddress
    form_class = forms.PatientAddressForm
    template_name = 'dossiers/patientaddress_new.html'
    success_url = '../../view#tab=2'

    def form_valid(self, form):
        messages.add_message(self.request, messages.INFO, u'Modification enregistrée avec succès.')
        return super(UpdatePatientAddressView, self).form_valid(form)

update_patient_address = UpdatePatientAddressView.as_view()

class DeletePatientAddressView(cbv.DeleteView):
    model = PatientAddress
    form_class = forms.PatientAddressForm
    template_name = 'dossiers/patientaddress_confirm_delete.html'
    success_url = '../../view#tab=2'

delete_patient_address = DeletePatientAddressView.as_view()


class NewHealthCareView(cbv.CreateView):

    def get_initial(self):
        initial = super(NewHealthCareView, self).get_initial()
        initial['author'] = self.request.user.id
        initial['patient'] = self.kwargs['patientrecord_id']
        return initial

new_healthcare_treatment = \
    NewHealthCareView.as_view(model=CmppHealthCareTreatment,
        template_name = 'dossiers/generic_form.html',
        success_url = '../view#tab=3',
        form_class=forms.CmppHealthCareTreatmentForm)
new_healthcare_diagnostic = \
    NewHealthCareView.as_view(model=CmppHealthCareDiagnostic,
        template_name = 'dossiers/generic_form.html',
        success_url = '../view#tab=3',
        form_class=forms.CmppHealthCareDiagnosticForm)
new_healthcare_notification = \
    NewHealthCareView.as_view(model=SessadHealthCareNotification,
        template_name = 'dossiers/generic_form.html',
        success_url = '../view#tab=3',
        form_class=forms.SessadHealthCareNotificationForm)
update_healthcare_treatment = \
    cbv.UpdateView.as_view(model=CmppHealthCareTreatment,
        template_name = 'dossiers/generic_form.html',
        success_url = '../../view#tab=3',
        form_class=forms.CmppHealthCareTreatmentForm)
update_healthcare_diagnostic = \
    cbv.UpdateView.as_view(model=CmppHealthCareDiagnostic,
        template_name = 'dossiers/generic_form.html',
        success_url = '../../view#tab=3',
        form_class=forms.CmppHealthCareDiagnosticForm)
update_healthcare_notification = \
    cbv.UpdateView.as_view(model=SessadHealthCareNotification,
        template_name = 'dossiers/generic_form.html',
        success_url = '../../view#tab=3',
        form_class=forms.SessadHealthCareNotificationForm)
delete_healthcare_treatment = \
    cbv.DeleteView.as_view(model=CmppHealthCareTreatment,
        template_name = 'dossiers/generic_confirm_delete.html',
        success_url = '../../view#tab=3')
delete_healthcare_diagnostic = \
    cbv.DeleteView.as_view(model=CmppHealthCareDiagnostic,
        template_name = 'dossiers/generic_confirm_delete.html',
        success_url = '../../view#tab=3')
delete_healthcare_notification = \
    cbv.DeleteView.as_view(model=SessadHealthCareNotification,
        template_name = 'dossiers/generic_confirm_delete.html',
        success_url = '../../view#tab=3')


class StateFormView(cbv.FormView):
    template_name = 'dossiers/state.html'
    form_class = forms.StateForm
    success_url = './view#tab=0'


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
            'general': forms.GeneralForm,
            'id': forms.CivilStatusForm,
            'physiology': forms.PhysiologyForm,
            'inscription': forms.InscriptionForm,
            'out': forms.OutForm,
            'family': forms.FamilyForm,
            'transport': forms.TransportFrom,
            'followup': forms.FollowUpForm,
            'policyholder': forms.PolicyHolderForm
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
        ctx['initial_state'] = ctx['object'].get_initial_state()
        current_state = ctx['object'].get_current_state()
        if STATES_MAPPING.has_key(current_state.status.type):
            state = STATES_MAPPING[current_state.status.type]
        else:
            state = current_state.status.name
        ctx['current_state'] = current_state
        ctx['service_id'] = self.service.id
        ctx['states'] = FileState.objects.filter(patient=self.object) \
                .filter(status__services=self.service) \
                .order_by('-date_selected')
        ctx['next_rdvs'] = []
        Q = models.Q
        today = date.today()
        qs = EventWithAct.objects.filter(patient=ctx['object']) \
                .filter(exception_to__isnull=True, canceled=False) \
                .filter(Q(start_datetime__gte=today) \
                |  Q(exceptions__isnull=False) \
                | ( Q(recurrence_periodicity__isnull=False) \
                & (Q(recurrence_end_date__gte=today) \
                | Q(recurrence_end_date__isnull=True) \
                ))) \
                .distinct() \
                .select_related() \
                .prefetch_related('participants', 'exceptions__eventwithact',
                        'act_set__actvalidationstate_set')
        occurrences = []
        for event in qs:
            occurrences.extend(filter(lambda e: e.start_datetime.date() >= today,
                event.all_occurences(limit=180)))
        occurrences = sorted(occurrences, key=lambda e: e.start_datetime)
        for event in occurrences:
            state = None
            if event.act:
                state = event.act.get_state()
            if state and not state.previous_state and state.state_name == 'NON_VALIDE':
                state = None
            ctx['next_rdvs'].append((event, state))
        if ctx['next_rdvs']:
            ctx['next_rdv'] = ctx['next_rdvs'][0][0]
        ctx['last_rdvs'] = []
        for act in Act.objects.last_acts(ctx['object']).prefetch_related('doctors'):
            state = act.get_state()
            if state and not state.previous_state and state.state_name == 'NON_VALIDE':
                state = None
            ctx['last_rdvs'].append((act, state))
        ctx['last_rdv'] = get_last_rdv(ctx['object'])

        ctx['missing_policy'] = False
        if not self.object.policyholder or \
                not self.object.policyholder.health_center or \
                not self.object.policyholder.social_security_id:
            ctx['missing_policy'] = True
        ctx['missing_birthdate'] = False
        if not self.object.birthdate:
            ctx['missing_birthdate'] = True

        ctx['status'] = []
        if ctx['object'].service.name == "CMPP":
            ctx['can_rediag'] = self.object.create_diag_healthcare(self.request.user)
            status = self.object.get_healthcare_status()
            highlight = False
            if status[0] == -1:
                status = 'Indéterminé.'
                highlight = True
            elif status[0] == 0:
                status = "Prise en charge de diagnostic en cours."
            elif status[0] == 1:
                status = 'Patient jamais pris en charge.'
            elif status[0] == 2:
                status = "Prise en charge de diagnostic complète, faire une demande de prise en charge de traitement."
                highlight = True
            elif status[0] == 3:
                if ctx['can_rediag']:
                    status = "Prise en charge de traitement expirée. Patient élligible en rediagnostic."
                    highlight = True
                else:
                    status = "Prise en charge de traitement expirée. La demande d'un renouvellement est possible."
                    highlight = True
            elif status[0] == 4:
                status = "Il existe une prise en charge de traitement mais qui ne prendra effet que le %s." % str(status[1])
            elif status[0] == 5:
                status = "Prise en charge de traitement en cours."
            elif status[0] == 6:
                status = "Prise en charge de traitement complète mais qui peut être prolongée."
                highlight = True
            elif status[0] == 7:
                status = "Prise en charge de traitement déjà prolongée complète se terminant le %s." % str(status[2])
            else:
                status = 'Statut inconnu.'
            ctx['hc_status'] = (status, highlight)
            if ctx['object'].last_state.status.type == "ACCUEIL":
                # Inscription automatique au premier acte facturable valide
                ctx['status'] = [STATES_BTN_MAPPER['FIN_ACCUEIL'],
                        STATES_BTN_MAPPER['DIAGNOSTIC'],
                        STATES_BTN_MAPPER['TRAITEMENT']]
            elif ctx['object'].last_state.status.type == "FIN_ACCUEIL":
                # Passage automatique en diagnostic ou traitement
                ctx['status'] = [STATES_BTN_MAPPER['ACCUEIL'],
                        STATES_BTN_MAPPER['DIAGNOSTIC'],
                        STATES_BTN_MAPPER['TRAITEMENT']]
            elif ctx['object'].last_state.status.type == "DIAGNOSTIC":
                # Passage automatique en traitement
                ctx['status'] = [STATES_BTN_MAPPER['TRAITEMENT'],
                        STATES_BTN_MAPPER['CLOS'],
                        STATES_BTN_MAPPER['ACCUEIL']]
            elif ctx['object'].last_state.status.type == "TRAITEMENT":
                # Passage automatique en diagnostic si on ajoute une prise en charge diagnostic,
                # ce qui est faisable dans l'onglet prise en charge par un bouton visible sous conditions
                ctx['status'] = [STATES_BTN_MAPPER['DIAGNOSTIC'],
                        STATES_BTN_MAPPER['CLOS'],
                        STATES_BTN_MAPPER['ACCUEIL']]
            elif ctx['object'].last_state.status.type == "CLOS":
                # Passage automatique en diagnostic ou traitement
                ctx['status'] = [STATES_BTN_MAPPER['DIAGNOSTIC'],
                        STATES_BTN_MAPPER['TRAITEMENT'],
                        STATES_BTN_MAPPER['ACCUEIL']]
            (acts_not_locked, days_not_locked, acts_not_valide,
            acts_not_billable, acts_pause, acts_per_hc, acts_losts) = \
                list_acts_for_billing_CMPP_2_per_patient(self.object,
                    datetime.today(), self.service)
            ctx['acts_losts'] = acts_losts
            ctx['acts_pause'] = acts_pause
            hcs_used = acts_per_hc.keys()
            if not hcs_used:
                ctx['hcs'] = [(hc, None) for hc in HealthCare.objects.filter(patient=self.object).order_by('-start_date')]
            else:
                ctx['hcs'] = []
                for hc in HealthCare.objects.filter(patient=self.object).order_by('-start_date'):
                    acts = None
                    if hasattr(hc, 'cmpphealthcarediagnostic') and hc.cmpphealthcarediagnostic in hcs_used:
                        acts = acts_per_hc[hc.cmpphealthcarediagnostic]
                    elif hasattr(hc, 'cmpphealthcaretreatment') and hc.cmpphealthcaretreatment in hcs_used:
                        acts = acts_per_hc[hc.cmpphealthcaretreatment]
                    ctx['hcs'].append((hc, acts))
        elif ctx['object'].service.name == "CAMSP":
            if ctx['object'].last_state.status.type == "ACCUEIL":
                ctx['status'] = [STATES_BTN_MAPPER['FIN_ACCUEIL'],
                        STATES_BTN_MAPPER['BILAN']]
            elif ctx['object'].last_state.status.type == "FIN_ACCUEIL":
                ctx['status'] = [STATES_BTN_MAPPER['ACCUEIL'],
                        STATES_BTN_MAPPER['BILAN'],
                        STATES_BTN_MAPPER['SURVEILLANCE'],
                        STATES_BTN_MAPPER['SUIVI'],
                        STATES_BTN_MAPPER['CLOS']]
            elif ctx['object'].last_state.status.type == "BILAN":
                ctx['status'] = [STATES_BTN_MAPPER['SURVEILLANCE'],
                        STATES_BTN_MAPPER['SUIVI'],
                        STATES_BTN_MAPPER['CLOS'],
                        STATES_BTN_MAPPER['ACCUEIL']]
            elif ctx['object'].last_state.status.type == "SURVEILLANCE":
                ctx['status'] = [STATES_BTN_MAPPER['SUIVI'],
                        STATES_BTN_MAPPER['CLOS'],
                        STATES_BTN_MAPPER['ACCUEIL'],
                        STATES_BTN_MAPPER['BILAN']]
            elif ctx['object'].last_state.status.type == "SUIVI":
                ctx['status'] = [STATES_BTN_MAPPER['CLOS'],
                        STATES_BTN_MAPPER['ACCUEIL'],
                        STATES_BTN_MAPPER['BILAN'],
                        STATES_BTN_MAPPER['SURVEILLANCE']]
            elif ctx['object'].last_state.status.type == "CLOS":
                ctx['status'] = [STATES_BTN_MAPPER['ACCUEIL'],
                        STATES_BTN_MAPPER['BILAN'],
                        STATES_BTN_MAPPER['SURVEILLANCE'],
                        STATES_BTN_MAPPER['SUIVI']]
        elif ctx['object'].service.name == "SESSAD TED" or ctx['object'].service.name == "SESSAD DYS":
            if ctx['object'].last_state.status.type == "ACCUEIL":
                ctx['status'] = [STATES_BTN_MAPPER['FIN_ACCUEIL'],
                        STATES_BTN_MAPPER['TRAITEMENT']]
            elif ctx['object'].last_state.status.type == "FIN_ACCUEIL":
                ctx['status'] = [STATES_BTN_MAPPER['ACCUEIL'],
                        STATES_BTN_MAPPER['TRAITEMENT'],
                        STATES_BTN_MAPPER['CLOS']]
            elif ctx['object'].last_state.status.type == "TRAITEMENT":
                ctx['status'] = [STATES_BTN_MAPPER['CLOS'],
                        STATES_BTN_MAPPER['ACCUEIL']]
            elif ctx['object'].last_state.status.type == "CLOS":
                ctx['status'] = [STATES_BTN_MAPPER['ACCUEIL'],
                        STATES_BTN_MAPPER['TRAITEMENT']]
            ctx['hcs'] = HealthCare.objects.filter(patient=self.object).order_by('-start_date')
        try:
            ctx['last_prescription'] = TransportPrescriptionLog.objects.filter(patient=ctx['object']).latest('created')
        except:
            pass
        return ctx

    def form_valid(self, form):
        messages.add_message(self.request, messages.INFO, u'Modification enregistrée avec succès.')
        return super(PatientRecordView, self).form_valid(form)


patient_record = PatientRecordView.as_view()

class PatientRecordsHomepageView(cbv.ListView):
    model = PatientRecord
    template_name = 'dossiers/index.html'


    def _get_search_result(self, paginate_patient_records):
        patient_records = []
        for patient_record in paginate_patient_records:
            next_rdv = get_next_rdv(patient_record)
            last_rdv = get_last_rdv(patient_record)
            current_status = patient_record.last_state.status
            state = current_status.name
            state_class = current_status.type.lower()
            patient_records.append(
                    {
                        'object': patient_record,
                        'next_rdv': next_rdv,
                        'last_rdv': last_rdv,
                        'state': state,
                        'state_class': state_class
                        }
                    )
        return patient_records

    def get_queryset(self):
        first_name = self.request.GET.get('first_name')
        last_name = self.request.GET.get('last_name')
        paper_id = self.request.GET.get('paper_id')
        id = self.request.GET.get('id')
        social_security_id = self.request.GET.get('social_security_id')
        if not (first_name or last_name or paper_id or id or social_security_id):
            return None
        if (first_name and len(first_name) < 2) or (last_name and len(last_name) < 2):
            return None
        qs = super(PatientRecordsHomepageView, self).get_queryset()
        states = self.request.GET.getlist('states')
        if last_name:
            qs = qs.filter(last_name__istartswith=last_name)
        if first_name:
            qs = qs.filter(first_name__istartswith=first_name)
        if paper_id:
            qs = qs.filter(paper_id__startswith=paper_id)
        if id:
            qs = qs.filter(id__startswith=id)
        if social_security_id:
            qs = qs.filter(models.Q(social_security_id__startswith=social_security_id) | \
                models.Q(contacts__social_security_id__startswith=social_security_id))
        if states:
            qs = qs.filter(last_state__status__id__in=states)
        else:
            qs = qs.filter(last_state__status__type__in="")
        qs = qs.filter(service=self.service).order_by('last_name').\
                prefetch_related('last_state',
                        'patientcontact', 'last_state__status')
        return qs

    def get_context_data(self, **kwargs):
        ctx = super(PatientRecordsHomepageView, self).get_context_data(**kwargs)
        ctx['search_form'] = forms.SearchForm(service=self.service, data=self.request.GET or None)
        ctx['stats'] = [["Dossiers", 0]]
        for status in Status.objects.filter(services=self.service):
            ctx['stats'].append([status.name, 0])

        page = self.request.GET.get('page')
        if ctx['object_list']:
            patient_records = ctx['object_list'].filter()
        else:
            patient_records = []

        # TODO: use a sql query to do this
        for patient_record in patient_records:
            ctx['stats'][0][1] += 1
            for elem in ctx['stats']:
                if elem[0] == patient_record.last_state.status.name:
                    elem[1] += 1
        paginator = Paginator(patient_records, 50)
        try:
            paginate_patient_records = paginator.page(page)
        except PageNotAnInteger:
            paginate_patient_records = paginator.page(1)
        except EmptyPage:
            paginate_patient_records = paginator.page(paginator.num_pages)

        query = self.request.GET.copy()
        if 'page' in query:
            del query['page']
        ctx['query'] = query.urlencode()

        ctx['paginate_patient_records'] = paginate_patient_records
        ctx['patient_records'] = self._get_search_result(paginate_patient_records)
        return ctx

patientrecord_home = PatientRecordsHomepageView.as_view()

class PatientRecordDeleteView(DeleteView):
    model = PatientRecord
    success_url = ".."
    template_name = 'dossiers/patientrecord_confirm_delete.html'

patientrecord_delete = validator_only(PatientRecordDeleteView.as_view())


class PatientRecordPaperIDUpdateView(cbv.UpdateView):
    model = PatientRecord
    form_class = forms.PaperIDForm
    template_name = 'dossiers/generic_form.html'
    success_url = '../..'

update_paper_id = PatientRecordPaperIDUpdateView.as_view()


class NewSocialisationDurationView(cbv.CreateView):
    model = SocialisationDuration
    form_class = forms.SocialisationDurationForm
    template_name = 'dossiers/generic_form.html'
    success_url = '../view#tab=6'

    def get_success_url(self):
        return self.success_url

    def get(self, request, *args, **kwargs):
        if kwargs.has_key('patientrecord_id'):
            request.session['patientrecord_id'] = kwargs['patientrecord_id']
        return super(NewSocialisationDurationView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        duration = form.save()
        patientrecord = PatientRecord.objects.get(id=self.kwargs['patientrecord_id'])
        patientrecord.socialisation_durations.add(duration)
        return HttpResponseRedirect(self.get_success_url())

new_socialisation_duration = NewSocialisationDurationView.as_view()

class UpdateSocialisationDurationView(cbv.UpdateView):
    model = SocialisationDuration
    form_class = forms.SocialisationDurationForm
    template_name = 'dossiers/generic_form.html'
    success_url = '../../view#tab=6'

    def get(self, request, *args, **kwargs):
        if kwargs.has_key('patientrecord_id'):
            request.session['patientrecord_id'] = kwargs['patientrecord_id']
        return super(UpdateSocialisationDurationView, self).get(request, *args, **kwargs)

update_socialisation_duration = UpdateSocialisationDurationView.as_view()

class DeleteSocialisationDurationView(cbv.DeleteView):
    model = SocialisationDuration
    form_class = forms.SocialisationDurationForm
    template_name = 'dossiers/socialisationduration_confirm_delete.html'
    success_url = '../../view#tab=6'

delete_socialisation_duration = DeleteSocialisationDurationView.as_view()


class NewMDPHRequestView(cbv.CreateView):
    def get(self, request, *args, **kwargs):
        if kwargs.has_key('patientrecord_id'):
            request.session['patientrecord_id'] = kwargs['patientrecord_id']
        return super(NewMDPHRequestView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        request = form.save()
        patientrecord = PatientRecord.objects.get(id=self.kwargs['patientrecord_id'])
        patientrecord.mdph_requests.add(request)
        return HttpResponseRedirect(self.success_url)

class UpdateMDPHRequestView(cbv.UpdateView):
    def get(self, request, *args, **kwargs):
        if kwargs.has_key('patientrecord_id'):
            request.session['patientrecord_id'] = kwargs['patientrecord_id']
        return super(UpdateMDPHRequestView, self).get(request, *args, **kwargs)


new_mdph_request = \
    NewMDPHRequestView.as_view(model=MDPHRequest,
        template_name = 'dossiers/generic_form.html',
        success_url = '../view#tab=6',
        form_class=forms.MDPHRequestForm)
update_mdph_request = \
    UpdateMDPHRequestView.as_view(model=MDPHRequest,
        template_name = 'dossiers/generic_form.html',
        success_url = '../../view#tab=6',
        form_class=forms.MDPHRequestForm)
delete_mdph_request = \
    cbv.DeleteView.as_view(model=MDPHRequest,
        template_name = 'dossiers/generic_confirm_delete.html',
        success_url = '../../view#tab=6')

class NewMDPHResponseView(cbv.CreateView):
    def get(self, request, *args, **kwargs):
        if kwargs.has_key('patientrecord_id'):
            request.session['patientrecord_id'] = kwargs['patientrecord_id']
        return super(NewMDPHResponseView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        response = form.save()
        patientrecord = PatientRecord.objects.get(id=self.kwargs['patientrecord_id'])
        patientrecord.mdph_responses.add(response)
        return HttpResponseRedirect(self.success_url)

class UpdateMDPHResponseView(cbv.UpdateView):
    def get(self, request, *args, **kwargs):
        if kwargs.has_key('patientrecord_id'):
            request.session['patientrecord_id'] = kwargs['patientrecord_id']
        return super(UpdateMDPHResponseView, self).get(request, *args, **kwargs)


new_mdph_response = \
    NewMDPHResponseView.as_view(model=MDPHResponse,
        template_name = 'dossiers/generic_form.html',
        success_url = '../view#tab=6',
        form_class=forms.MDPHResponseForm)
update_mdph_response = \
    UpdateMDPHResponseView.as_view(model=MDPHResponse,
        template_name = 'dossiers/generic_form.html',
        success_url = '../../view#tab=6',
        form_class=forms.MDPHResponseForm)
delete_mdph_response = \
    cbv.DeleteView.as_view(model=MDPHResponse,
        template_name = 'dossiers/generic_confirm_delete.html',
        success_url = '../../view#tab=6')


class UpdatePatientStateView(cbv.ServiceFormMixin, cbv.UpdateView):

    def get_initial(self):
        initial = super(UpdatePatientStateView, self).get_initial()
        initial['date_selected'] = self.object.date_selected.date()
        return initial

    def get(self, request, *args, **kwargs):
        if kwargs.has_key('patientrecord_id'):
            request.session['patientrecord_id'] = kwargs['patientrecord_id']
        return super(UpdatePatientStateView, self).get(request, *args, **kwargs)

class DeletePatientView(cbv.DeleteView):

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object == self.object.patient.last_state:
            status = self.object.patient.filestate_set.all().order_by('-created')
            if len(status) > 1:
                self.object.patient.last_state = status[1]
                self.object.patient.save()
            else:
                # TODO return an error here
                return HttpResponseRedirect(self.get_success_url())
        self.object.delete()
        return HttpResponseRedirect(self.get_success_url())


update_patient_state = \
    UpdatePatientStateView.as_view(model=FileState,
        template_name = 'dossiers/generic_form.html',
        success_url = '../../view#tab=0',
        form_class=forms.PatientStateForm)
delete_patient_state = \
    DeletePatientView.as_view(model=FileState,
        template_name = 'dossiers/generic_confirm_delete.html',
        success_url = '../../view#tab=0')


class GenerateRtfFormView(cbv.FormView):
    template_name = 'dossiers/generate_rtf_form.html'
    form_class = forms.GenerateRtfForm
    success_url = './view#tab=0'

    def get_context_data(self, **kwargs):
        ctx = super(GenerateRtfFormView, self).get_context_data(**kwargs)
        ctx['object'] = PatientRecord.objects.get(id=self.kwargs['patientrecord_id'])
        ctx['service_id'] = self.service.id
        if self.request.GET.get('event-id'):
            date = self.request.GET.get('date')
            date = datetime.strptime(date, '%Y-%m-%d').date()
            appointment = Appointment()
            event = EventWithAct.objects.get(id=self.request.GET.get('event-id'))
            event = event.today_occurrence(date)
            appointment.init_from_event(event, self.service)
            ctx['appointment'] = appointment
        return ctx

    def form_valid(self, form, **kwargs):
        ctx = self.get_context_data(**kwargs)
        patient = ctx['object']
        appointment = ctx['appointment']
        template_filename = form.cleaned_data.get('template_filename')
        dest_filename = datetime.now().strftime('%Y-%m-%d--%H:%M:%S') + '--' + template_filename
        from_path = os.path.join(settings.RTF_TEMPLATES_DIRECTORY, template_filename)
        to_path = ''
        persistent = True
        if settings.USE_PATIENT_FILE_RTF_REPOSITORY_DIRECTORY \
                or settings.RTF_REPOSITORY_DIRECTORY:
            if settings.USE_PATIENT_FILE_RTF_REPOSITORY_DIRECTORY:
                to_path = patient.get_ondisk_directory(self.service.name)
            if settings.RTF_REPOSITORY_DIRECTORY:
                to_path = os.path.join(to_path,
                    settings.RTF_REPOSITORY_DIRECTORY)
            to_path = os.path.join(to_path, dest_filename)
        else:
            # else : use temporary files
            persistent = False
            to_path = dest_filename
        variables = {'AD11': '', 'AD12': '', 'AD13': '', 'AD14': '',
            'AD15': '', 'AD18': '',
            'JOU1': formats.date_format(datetime.today(), "DATE_FORMAT"),
            'VIL1': u'Saint-Étienne',
            'RDV1': '', 'HEU1': '', 'THE1': '', 'DPA1': '',
            'NOM1': '', 'PRE1': '', 'NAI1': '', 'NUM2': '',
            'NOM2': '', 'PRE2': '', 'TPA1': '', 'NSS1': '',
            'TR01': '', 'TR02': '', 'TR03': '', 'TR04': '', 'TR05': '',
            'AD16': '', 'AD17': '', 'AD19': '',
            'AD21': '', 'AD22': '', 'AD23': '', 'AD24': '', 'AD25': '',
            'AD26': '', 'AD27': '', 'AD28': '', 'AD29': '',
        }
        if appointment:
            variables['RDV1'] = appointment.date
            variables['HEU1'] = appointment.begin_hour
            variables['THE1'] = ' '.join([str(i) for i in appointment.workers])# ou DPA1?
            variables['DPA1'] = variables['THE1']
        if patient:
            variables['NOM1'] = patient.last_name
            variables['PRE1'] = patient.first_name
            if patient.birthdate :
                variables['NAI1'] = patient.birthdate.strftime('%d/%m/%Y')
            variables['NUM2'] = patient.paper_id
            if patient.policyholder:
                variables['NOM2'] = patient.policyholder.last_name
                variables['PRE2'] = patient.policyholder.first_name
                if patient.policyholder.health_center:
                    variables['TPA1'] = patient.policyholder.health_center.name
                if patient.policyholder.social_security_id:
                    key = str(patient.policyholder.get_control_key())
                    if len(key) == 1:
                        key = '0' + key
                    variables['NSS1'] = \
                        ' '.join([patient.policyholder.social_security_id,
                            key])
            if patient.transportcompany:
                variables['TR01'] = patient.transportcompany.name
                variables['TR02'] = patient.transportcompany.address
                variables['TR03'] = patient.transportcompany.address_complement
                variables['TR04'] = patient.transportcompany.zip_code
                variables['TR05'] = patient.transportcompany.city
        variables['AD18'] = form.cleaned_data.get('phone_address') or ''
        for i, line in enumerate(form.cleaned_data.get('address').splitlines()):
            variables['AD%d' % (11+i)] = line
            if i == 4:
                break

        filename = make_doc_from_template(from_path, to_path, variables,
            persistent)

        client_dir = patient.get_client_side_directory(self.service.name)
        if not client_dir:
            content = File(file(filename))
            response = HttpResponse(content,'text/rtf')
            response['Content-Length'] = content.size
            response['Content-Disposition'] = 'attachment; filename="%s"' \
                % dest_filename.encode('utf-8')
            return response
        else:
            class LocalFileHttpResponseRedirect(HttpResponseRedirect):
                allowed_schemes = ['file']
            client_filepath = os.path.join(client_dir, dest_filename)
            return LocalFileHttpResponseRedirect('file://' + client_filepath)

generate_rtf_form = GenerateRtfFormView.as_view()


class PatientRecordsQuotationsView(cbv.ListView):
    model = PatientRecord
    template_name = 'dossiers/quotations.html'

    def _get_search_result(self, paginate_patient_records):
        patient_records = []
        for patient_record in paginate_patient_records:
            current_state = patient_record.get_current_state()
            state = current_state.status.name
            state_class = current_state.status.type.lower()
            patient_records.append(
                    {
                        'object': patient_record,
                        'state': state,
                        'state_class': state_class
                        }
                    )
        return patient_records

    def get_queryset(self):
        form = forms.QuotationsForm(data=self.request.GET or None)
        qs = super(PatientRecordsQuotationsView, self).get_queryset()
        without_quotations = self.request.GET.get('without_quotations')
        if without_quotations:
            qs = qs.filter(mises_1=None).filter(mises_2=None).filter(mises_3=None)
        states = self.request.GET.getlist('states')
        qs = qs.filter(last_state__status__id__in=states)

        try:
            date_actes_start = datetime.strptime(form.data['date_actes_start'], "%d/%m/%Y")
            qs = qs.filter(act__date__gte=date_actes_start.date()).distinct()
        except (ValueError, KeyError):
            pass
        try:
            date_actes_end = datetime.strptime(form.data['date_actes_end'], "%d/%m/%Y")
            qs = qs.filter(act__date__lte=date_actes_end.date()).distinct()
        except (ValueError, KeyError):
            pass
        qs = qs.filter(service=self.service).order_by('last_name').prefetch_related()
        return qs

    def get_context_data(self, **kwargs):
        ctx = super(PatientRecordsQuotationsView, self).get_context_data(**kwargs)
        ctx['search_form'] = forms.QuotationsForm(data=self.request.GET or None,
                service=self.service)
        patient_records = []
        page = self.request.GET.get('page')
        paginator = Paginator(ctx['object_list'].filter(), 50)
        try:
            paginate_patient_records = paginator.page(page)
        except PageNotAnInteger:
            paginate_patient_records = paginator.page(1)
        except EmptyPage:
            paginate_patient_records = paginator.page(paginator.num_pages)

        ctx['patient_records'] = self._get_search_result(paginate_patient_records)
        ctx['paginate_patient_records'] = paginate_patient_records

        query = self.request.GET.copy()
        if 'page' in query:
            del query['page']
        ctx['query'] = query.urlencode()

        return ctx

patientrecord_quotations = PatientRecordsQuotationsView.as_view()


class CreateDirectoryView(View, cbv.ServiceViewMixin):
    def post(self, request, *args, **kwargs):
        patient = PatientRecord.objects.get(id=kwargs['patientrecord_id'])
        service = Service.objects.get(slug=kwargs['service'])
        patient.get_ondisk_directory(service.name)
        messages.add_message(self.request, messages.INFO, u'Répertoire patient créé.')
        return HttpResponseRedirect('view')

create_directory = CreateDirectoryView.as_view()

class GenerateTransportPrescriptionFormView(cbv.FormView):
    template_name = 'dossiers/generate_transport_prescription_form.html'
    form_class = Form
    success_url = './view#tab=1'

    def get_context_data(self, **kwargs):
        ctx = super(GenerateTransportPrescriptionFormView, self).get_context_data(**kwargs)
        ctx['lieu'] = 'Saint-Etienne'
        ctx['date'] = formats.date_format(datetime.today(), "SHORT_DATE_FORMAT")
        ctx['id_etab'] = '''%s SAINT ETIENNE
66/68, RUE MARENGO
42000 SAINT ETIENNE''' % ctx['service'].upper()
        try:
            patient = PatientRecord.objects.get(id=self.kwargs['patientrecord_id'])
            ctx['object'] = patient
            last_log = TransportPrescriptionLog.objects.filter(patient=patient).latest('created')
            if last_log:
                ctx['choices'] = last_log.get_choices()
                if 'lieu' in ctx['choices'] and ctx['choices']['lieu']:
                    ctx['lieu'] = ctx['choices']['lieu']
                if 'date' in ctx['choices'] and ctx['choices']['date']:
                    ctx['date'] = ctx['choices']['date']
                if 'id_etab' in ctx['choices'] and ctx['choices']['id_etab']:
                    ctx['id_etab'] = ctx['choices']['id_etab']
        except:
            pass
        return ctx

    def form_valid(self, form):
        patient = PatientRecord.objects.get(id=self.kwargs['patientrecord_id'])
        address = PatientAddress.objects.get(id=form.data['address_id'])
        path = render_transport(patient, address, form.data)
        content = File(file(path))
        log = TransportPrescriptionLog(patient=patient)
        log.set_choices(form.data)
        log.save()
        response = HttpResponse(content,'application/pdf')
        response['Content-Length'] = content.size
        dest_filename = "%s--prescription-transport-%s-%s.pdf" \
            % (datetime.now().strftime('%Y-%m-%d--%H:%M:%S'),
            patient.last_name.upper().encode('utf-8'),
            patient.first_name.encode('utf-8'))
        response['Content-Disposition'] = \
            'attachment; filename="%s"' % dest_filename
        return response

prescription_transport = GenerateTransportPrescriptionFormView.as_view()
