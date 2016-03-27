# -*- coding: utf-8 -*-
from datetime import datetime
from collections import defaultdict

from django.db.models import Q

from alcide.actes.models import Act
from alcide.dossiers.models import (CmppHealthCareDiagnostic,
    CmppHealthCareTreatment)


def list_acts_for_billing_first_round(end_day, service, start_day=None, acts=None, patient=None):
    """Used to sort acts and extract acts billable before specific service
        requirements.

    At first, all acts not billed are listed per patient.
    Then acts are sorted.
    Each sorting split the acts in two sets, one set for rejected acts,
        on set for selected sets.
    First sort rejects acts days where all acts are not locked:
        acts_not_locked
    Second sort rejects acts not in state 'VALIDE':
        acts_not_valide
    Third sort rejects acts not billable:
        acts_not_billable
    Acts billable in :
        acts_billable

    acts = acts_not_locked + \
        acts_not_valide + \
            acts_not_billable + \
                acts_billable

    :param end_day: formatted date that gives the last day when acts are taken
        in account.
    :type end_day: datetime
    :param service: service in which acts are dealt with.
    :type service: alcide.ressources.Service

    :returns: a list of dictionnaries where patients are the keys and values
        are lists of acts. The second element of this list in not a dict but
        a list of the days where are all days are not locked.
    :rtype: list
    """

    from alcide.actes.models import Act
    if isinstance(end_day, datetime):
        end_day = end_day.date()
    if start_day and isinstance(start_day, datetime):
        start_day = start_day.date()

    acts = Act.objects.filter(validation_locked=False,
        patient__service=service, date__lte=end_day)
    if start_day:
        acts = acts.filter(date__gte=start_day)
    days_not_locked = sorted(set(acts.values_list('date', flat=True)))

    acts = None
    if patient:
        acts = Act.objects.filter(patient=patient, validation_locked=True,
            is_billed=False, valide=True, is_lost=False,
            patient__service=service, date__lte=end_day)
    else:
        acts = Act.objects.filter(validation_locked=True,
            is_billed=False, valide=True, is_lost=False,
            patient__service=service, date__lte=end_day)
    if start_day:
        acts = acts.filter(date__gte=start_day)
    acts = acts.exclude(date__in=days_not_locked)
    acts = acts.order_by('date')

    # deprecated
    acts_not_locked = {}
    acts_not_valide = {}

    acts_pause = {}
    acts_not_billable = {}
    acts_billable = {}


    pause_query = Q(pause=True)
    billable_query = Q(act_type__billable=True, switch_billable=False) | \
            Q(act_type__billable=False, switch_billable=True)

    paused_acts = acts.filter(pause_query).select_related('patient', 'act_type')
    not_billable_acts = acts.filter(~pause_query & ~billable_query).select_related('patient', 'act_type')
    billable_acts = acts.filter(~pause_query & billable_query)
    billable_acts = billable_acts.select_related('act_type', 'patient__policyholder__health_center').prefetch_related('patient__act_set', 'patient__act_set__healthcare')

    for act in paused_acts:
        acts_pause.setdefault(act.patient, []).append(act)

    for act in not_billable_acts:
        acts_not_billable.setdefault(act.patient, []).append(act)

    for act in billable_acts:
        acts_billable.setdefault(act.patient, []).append(act)
    return (acts_not_locked, days_not_locked, acts_not_valide,
        acts_not_billable, acts_pause, acts_billable)


def list_acts_for_billing_CAMSP(start_day, end_day, service, acts=None):
    """Used to sort acts billable by specific service requirements.

    For the CAMSP, only the state of the patient record 'CAMSP_STATE_SUIVI'
        at the date of the act determine if the acte is billable.

    acts = acts_not_locked + \
        acts_not_valide + \
            acts_not_billable + \
                acts_bad_state + \
                    acts_accepted

    :param end_day: formatted date that gives the last day when acts are taken
        in account.
    :type end_day: datetime
    :param service: service in which acts are dealt with.
    :type service: alcide.ressources.Service

    :returns: a list of dictionnaries where patients are the keys and values
        are lists of acts. The second element of this list in not a dict but
        a list of the days where are all days are not locked.
    :rtype: list
    """

    acts_not_locked, days_not_locked, acts_not_valide, \
        acts_not_billable, acts_pause, acts_billable = \
            list_acts_for_billing_first_round(end_day, service,
                start_day, acts=acts)
    acts_bad_state = {}
    acts_accepted = {}
    patients_missing_policy = []
    for patient, acts in acts_billable.iteritems():
        for act in acts:
            if patient.was_in_state_at_day(act.date, 'SUIVI'):
                acts_accepted.setdefault(act.patient, []).append(act)
            else:
                acts_bad_state.setdefault(act.patient, []).\
                    append((act, 'NOT_ACCOUNTABLE_STATE'))
    for patient in acts_accepted.keys():
        if not patient.policyholder or \
                not patient.policyholder.health_center or \
                not patient.policyholder.management_code or \
                not patient.policyholder.social_security_id:
            patients_missing_policy.append(patient)
    return (acts_not_locked, days_not_locked, acts_not_valide,
        acts_not_billable, acts_pause, acts_bad_state,
        acts_accepted, patients_missing_policy)


def list_acts_for_billing_SESSAD(start_day, end_day, service, acts=None):
    """Used to sort acts billable by specific service requirements.

    For the SESSAD, acts are billable if the state of the patient record at
        the date of the act is 'SESSAD_STATE_TRAITEMENT' and there was also a
        valid notification at that date.

    acts = acts_not_locked + \
        acts_not_valide + \
            acts_not_billable + \
                acts_bad_state + \
                    acts_missing_valid_notification + \
                        acts_accepted

    :param end_day: formatted date that gives the last day when acts are taken
        in account.
    :type end_day: datetime
    :param service: service in which acts are dealt with.
    :type service: alcide.ressources.Service

    :returns: a list of dictionnaries where patients are the keys and values
        are lists of acts. The second element of this list in not a dict but
        a list of the days where are all days are not locked.
    :rtype: list
    """

    acts_not_locked, days_not_locked, acts_not_valide, \
        acts_not_billable, acts_pause, acts_billable = \
            list_acts_for_billing_first_round(end_day, service,
                start_day=start_day, acts=acts)
    acts_bad_state = {}
    acts_missing_valid_notification = {}
    acts_accepted = {}
    patients_missing_policy = []
    for patient, acts in acts_billable.iteritems():
        for act in acts:
            if patient.was_in_state_at_day(act.date,
                    'TRAITEMENT'):
                if not act.was_covered_by_notification():
                    acts_missing_valid_notification.\
                        setdefault(act.patient, []).append(act)
                else:
                    acts_accepted.setdefault(act.patient, []).append(act)
            else:
                acts_bad_state.setdefault(act.patient, []).\
                    append((act, 'NOT_ACCOUNTABLE_STATE'))
    for patient in acts_accepted.keys():
        if not patient.policyholder or \
                not patient.policyholder.health_center or \
                not patient.policyholder.management_code or \
                not patient.policyholder.social_security_id:
            patients_missing_policy.append(patient)
    return (acts_not_locked, days_not_locked, acts_not_valide,
        acts_not_billable, acts_pause, acts_bad_state,
        acts_missing_valid_notification, acts_accepted,
        patients_missing_policy)


def list_acts_for_billing_CMPP(end_day, service, acts=None):
    """Used to sort acts billable by specific service requirements.

    For the CMPP, acts are billable if

    acts = acts_not_locked + \
        acts_not_valide + \
            acts_not_billable + \
                acts_diagnostic + \
                    acts_treatment + \
                        acts_losts

    :param end_day: formatted date that gives the last day when acts are taken
        in account.
    :type end_day: datetime
    :param service: service in which acts are dealt with.
    :type service: alcide.ressources.Service

    :returns: a list of dictionnaries where patients are the keys and values
        are lists of acts. The second element of this list in not a dict but
        a list of the days where are all days are not locked.
    :rtype: list
    """

    acts_not_locked, days_not_locked, acts_not_valide, \
        acts_not_billable, acts_pause, acts_billable = \
            list_acts_for_billing_first_round(end_day, service, acts=acts)

    acts_diagnostic = {}
    acts_treatment = {}
    acts_losts = {}
    acts_losts_missing_policy = {}
    acts_losts_missing_birthdate = {}
    patient_ids = [p.id for p in acts_billable]
    # compute latest hcds using one query
    latest_hcd = {}
    hcds = CmppHealthCareDiagnostic.objects.filter(patient_id__in=patient_ids).order_by('-start_date').select_related().prefetch_related('act_set')
    for hcd in hcds:
        if hcd.patient not in latest_hcd:
            latest_hcd[hcd.patient] = hcd
    # compute two latest hcts using one query
    latest_hcts = defaultdict(lambda:[])
    hcts = CmppHealthCareTreatment.objects.filter(patient_id__in=patient_ids).order_by('-start_date').select_related().prefetch_related('act_set')
    for hct in hcts:
        if hct.patient not in latest_hcts or len(latest_hcts[hct.patient]) < 2:
            latest_hcts[hct.patient].append(hct)

    for patient, acts in acts_billable.items():
        if not patient.policyholder or \
                not patient.policyholder.health_center or \
                not patient.policyholder.social_security_id:
            acts_losts_missing_policy[patient] = acts
            continue
        if not patient.birthdate:
            acts_losts_missing_birthdate[patient] = acts
            continue
        # Date de début de la prise en charge ayant servis au dernier acte facturé
        lasts_billed = sorted(filter(lambda a: a.is_billed and a.healthcare is not None, patient.act_set.all()), key=lambda a: a.date, reverse=True)
        last_hc_date = None
        if lasts_billed:
            last_hc_date = lasts_billed[0].healthcare.start_date
        hcd = None
        len_acts_cared_diag = 0
        try:
            hcd = latest_hcd.get(patient)
            if not last_hc_date or last_hc_date <= hcd.start_date:
                # actes prise en charge par ce hc
                len_acts_cared_diag = len(hcd.act_set.all())
            else:
                # Comme un PC diag n'a pas de date de fin, on considère qu'elle ne sert plus si un acte a été couvert par une prise en charge plus récente.
                hcd = None
        except:
            pass
        '''
            We take in account the two last treatment healthcare
        '''
        hcts = latest_hcts.get(patient, [])
        # acts are all billable and chronologically ordered
        count_hcd = 0
        count_hct_1 = 0
        count_hct_2 = 0
        for act in acts:
            cared = False
            # If there is overlapping between hc period the more recent must
            # be used ! That should not happen with hct but might between
            # hcd and hct.
            if len(hcts) > 0 and hcts[0] and hcts[0].start_date <= act.date and hcts[0].end_date >= act.date:
                if count_hct_2 < hcts[0].get_act_number() - hcts[0].get_nb_acts_cared():
                    acts_treatment.setdefault(patient, []).append((act, hcts[0]))
                    count_hct_2 = count_hct_2 + 1
                    cared = True
            if not cared and len(hcts) > 1 and hcts[1] and hcts[1].start_date <= act.date and hcts[1].end_date >= act.date:
                # Ce qui seraient prise en charge
                # ne doit pas dépasser la limite de prise en charge du hc
                if count_hct_1 < hcts[1].get_act_number() - hcts[1].get_nb_acts_cared():
                    acts_treatment.setdefault(patient, []).append((act, hcts[1]))
                    count_hct_1 = count_hct_1 + 1
                    cared = True
            if not cared and hcd and hcd.start_date <= act.date and \
                    (not hcd.end_date or hcd.end_date >= act.date):
                # Ce qui seraient prise en charge
                nb_acts_cared = len_acts_cared_diag + count_hcd
                # Ne doit pas dépasser la limite de prise en charge du hc
                if nb_acts_cared < hcd.get_act_number() :
                    acts_diagnostic.setdefault(patient, []).append((act, hcd))
                    count_hcd = count_hcd + 1
                    cared = True
            if not cared:
                acts_losts.setdefault(patient, []).append(act)
    return (acts_not_locked, days_not_locked, acts_not_valide,
        acts_not_billable, acts_pause, acts_diagnostic,
        acts_treatment, acts_losts, acts_losts_missing_policy,
        acts_losts_missing_birthdate)

def list_acts_for_billing_CMPP_per_patient(patient, end_day, service, acts=None):

    acts_not_locked, days_not_locked, acts_not_valide, \
        acts_not_billable, acts_pause, acts_billable = \
            list_acts_for_billing_first_round(end_day, service, acts=acts, patient=patient)

    acts_per_hc = {}
    acts_losts = []
    if len(acts_billable.keys()) > 1:
        raise "Should not find more than one patient"
    elif len(acts_billable.keys()) == 1:
        # Date de début de la prise en charge ayant servis au dernier acte facturé
        lasts_billed = Act.objects.filter(patient=patient, is_billed = True, healthcare__isnull=False).order_by('-date')
        last_hc_date = None
        if lasts_billed:
            last_hc_date = lasts_billed[0].healthcare.start_date
        patient, acts = acts_billable.items()[0]
        hcd = None
        len_acts_cared_diag = 0
        try:
            hcd = CmppHealthCareDiagnostic.objects.\
                filter(patient=patient).latest('start_date')
            if not last_hc_date or last_hc_date <= hcd.start_date:
                # actes prise en charge par ce hc
                len_acts_cared_diag = len(hcd.act_set.all())
            else:
                # Comme un PC diag n'a pas de date de fin, on considère qu'elle ne sert plus si un acte a été couvert par une prise en charge plus récente.
                hcd = None
        except:
            pass
        '''
            We take in account the two last treatment healthcare
        '''
        hcts = None
        len_acts_cared_trait = 0
        try:
            hcts = CmppHealthCareTreatment.objects.\
                filter(patient=patient).order_by('-start_date')
        except:
            pass
        # acts are all billable and chronologically ordered
        count_hcd = 0
        count_hct_1 = 0
        count_hct_2 = 0
        if hcd:
            acts_per_hc[hcd] = []
        if len(hcts) > 0:
            acts_per_hc[hcts[0]] = []
        if len(hcts) > 1:
            acts_per_hc[hcts[1]] = []
        for act in acts:
            cared = False
            # If there is overlapping between hc period the more recent must
            # be used ! That should not happen with hct but might between
            # hcd and hct.
            if len(hcts) > 0 and hcts[0] and hcts[0].start_date <= act.date and hcts[0].end_date >= act.date:
                if count_hct_2 < hcts[0].get_act_number() - hcts[0].get_nb_acts_cared():
                    acts_per_hc[hcts[0]].append(act)
                    count_hct_2 = count_hct_2 + 1
                    cared = True
            if not cared and len(hcts) > 1 and hcts[1] and hcts[1].start_date <= act.date and hcts[1].end_date >= act.date:
                # Ce qui seraient prise en charge
                # ne doit pas dépasser la limite de prise en charge du hc
                if count_hct_1 < hcts[1].get_act_number() - hcts[1].get_nb_acts_cared():
                    acts_per_hc[hcts[1]].append(act)
                    count_hct_1 = count_hct_1 + 1
                    cared = True
            if not cared and hcd and hcd.start_date <= act.date and \
                    (not hcd.end_date or hcd.end_date >= act.date):
                # Ce qui seraient prise en charge
                nb_acts_cared = len_acts_cared_diag + count_hcd
                # Ne doit pas dépasser la limite de prise en charge du hc
                if nb_acts_cared < hcd.get_act_number() :
                    acts_per_hc[hcd].append(act)
                    count_hcd = count_hcd + 1
                    cared = True
            if not cared:
                acts_losts.append(act)
    if len(acts_pause.keys()) == 1:
        acts_pause = acts_pause.values()[0]
    else:
        acts_pause = []
    return (acts_not_locked, days_not_locked, acts_not_valide,
        acts_not_billable, acts_pause, acts_per_hc, acts_losts)
