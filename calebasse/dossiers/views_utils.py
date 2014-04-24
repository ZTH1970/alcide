# -*- coding: utf-8 -*-

from datetime import date

from django.db import models
from django.utils import formats

from calebasse.agenda.models import Event, EventWithAct
from calebasse.dossiers.states import STATES_BTN_MAPPER

def get_status(ctx, user):
    """
    Return status and hc_status
    """
    status = []
    close_btn = STATES_BTN_MAPPER['CLOS']
    if ctx.get('next_rdv'):
        close_btn = STATES_BTN_MAPPER['CLOS_RDV']
    if ctx['object'].service.slug == "cmpp":
        ctx['can_rediag'] = ctx['object'].create_diag_healthcare(user)
        status = ctx['object'].get_healthcare_status()
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
            status = "Prise en charge de traitement complète et déjà prolongée, se terminant le %s." % \
                formats.date_format(status[2], "SHORT_DATE_FORMAT")
        else:
            status = 'Statut inconnu.'
        hc_status = (status, highlight)
        if ctx['object'].last_state.status.type == "ACCUEIL":
            # Inscription automatique au premier acte facturable valide
            status = [STATES_BTN_MAPPER['FIN_ACCUEIL'],
                    STATES_BTN_MAPPER['DIAGNOSTIC'],
                    STATES_BTN_MAPPER['TRAITEMENT']]
        elif ctx['object'].last_state.status.type == "FIN_ACCUEIL":
            # Passage automatique en diagnostic ou traitement
            status = [STATES_BTN_MAPPER['ACCUEIL'],
                    STATES_BTN_MAPPER['DIAGNOSTIC'],
                    STATES_BTN_MAPPER['TRAITEMENT']]
        elif ctx['object'].last_state.status.type == "DIAGNOSTIC":
            # Passage automatique en traitement
            status = [STATES_BTN_MAPPER['TRAITEMENT'],
                    close_btn,
                    STATES_BTN_MAPPER['ACCUEIL']]
        elif ctx['object'].last_state.status.type == "TRAITEMENT":
            # Passage automatique en diagnostic si on ajoute une prise en charge diagnostic,
            # ce qui est faisable dans l'onglet prise en charge par un bouton visible sous conditions
            status = [STATES_BTN_MAPPER['DIAGNOSTIC'],
                    close_btn,
                    STATES_BTN_MAPPER['ACCUEIL']]
        elif ctx['object'].last_state.status.type == "CLOS":
            # Passage automatique en diagnostic ou traitement
            status = [STATES_BTN_MAPPER['DIAGNOSTIC'],
                    STATES_BTN_MAPPER['TRAITEMENT'],
                    STATES_BTN_MAPPER['ACCUEIL']]
    elif ctx['object'].service.slug == "camsp":
        hc_status = None
        if ctx['object'].last_state.status.type == "ACCUEIL":
            status = [STATES_BTN_MAPPER['FIN_ACCUEIL'],
                    STATES_BTN_MAPPER['BILAN']]
        elif ctx['object'].last_state.status.type == "FIN_ACCUEIL":
            status = [STATES_BTN_MAPPER['ACCUEIL'],
                    STATES_BTN_MAPPER['BILAN'],
                    STATES_BTN_MAPPER['SURVEILLANCE'],
                    STATES_BTN_MAPPER['SUIVI'],
                    close_btn]
        elif ctx['object'].last_state.status.type == "BILAN":
            status = [STATES_BTN_MAPPER['SURVEILLANCE'],
                    STATES_BTN_MAPPER['SUIVI'],
                    close_btn,
                    STATES_BTN_MAPPER['ACCUEIL']]
        elif ctx['object'].last_state.status.type == "SURVEILLANCE":
            status = [STATES_BTN_MAPPER['SUIVI'],
                    close_btn,
                    STATES_BTN_MAPPER['ACCUEIL'],
                    STATES_BTN_MAPPER['BILAN']]
        elif ctx['object'].last_state.status.type == "SUIVI":
            status = [close_btn,
                    STATES_BTN_MAPPER['ACCUEIL'],
                    STATES_BTN_MAPPER['BILAN'],
                    STATES_BTN_MAPPER['SURVEILLANCE']]
        elif ctx['object'].last_state.status.type == "CLOS":
            status = [STATES_BTN_MAPPER['ACCUEIL'],
                    STATES_BTN_MAPPER['BILAN'],
                    STATES_BTN_MAPPER['SURVEILLANCE'],
                    STATES_BTN_MAPPER['SUIVI']]
    elif ctx['object'].service.slug == "sessad-ted" or ctx['object'].service.slug == "sessad-dys":
        hc_status = None
        if ctx['object'].last_state.status.type == "ACCUEIL":
            status = [STATES_BTN_MAPPER['FIN_ACCUEIL'],
                    STATES_BTN_MAPPER['TRAITEMENT']]
        elif ctx['object'].last_state.status.type == "FIN_ACCUEIL":
            status = [STATES_BTN_MAPPER['ACCUEIL'],
                    STATES_BTN_MAPPER['TRAITEMENT'],
                    close_btn]
        elif ctx['object'].last_state.status.type == "TRAITEMENT":
            status = [close_btn,
                    STATES_BTN_MAPPER['ACCUEIL']]
        elif ctx['object'].last_state.status.type == "CLOS":
            status = [STATES_BTN_MAPPER['ACCUEIL'],
                    STATES_BTN_MAPPER['TRAITEMENT']]
    return (status, hc_status)

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
