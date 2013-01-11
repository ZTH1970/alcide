# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from calebasse.actes.validation import are_all_acts_of_the_day_locked
from calebasse.dossiers.models import (CmppHealthCareDiagnostic,
    CmppHealthCareTreatment)


def list_acts_for_billing_first_round(end_day, service, start_day=None, acts=None):
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
    :type service: calebasse.ressources.Service

    :returns: a list of dictionnaries where patients are the keys and values
        are lists of acts. The second element of this list in not a dict but
        a list of the days where are all days are not locked.
    :rtype: list
    """

    from calebasse.actes.models import Act
    if isinstance(end_day, datetime):
        end_day = end_day.date()
    if acts is None:
        acts = Act.objects.filter(is_billed=False, is_lost=False,
            patient__service=service).order_by('date')
    # Filter acts according to the date
    i = 0
    for act in acts:
        # On enlève tous les acts sup au jour de l'end_date
        if act.date > end_day:
            acts = acts[:i]
            break
        i = i + 1
    if start_day:
        i = 0
        for act in acts:
            # On enlève tous les acts inf au jour de la start_date
            if datetime(act.date.year, act.date.month, act.date.day) < \
                    datetime(start_day.year, start_day.month, start_day.day):
                break
            i = i + 1
        acts = acts[:i]
    acts_not_locked = {}
    days_not_locked = []
    acts_not_valide = {}
    acts_not_billable = {}
    acts_pause = {}
    acts_billable = {}
    locked = False
    for act in acts:
        current_day = datetime(act.date.year, act.date.month, act.date.day)
        locked = are_all_acts_of_the_day_locked(current_day, service)
        if not locked:
            if not current_day in days_not_locked:
                days_not_locked.append(current_day)
            if act.patient in acts_not_locked:
                acts_not_locked[act.patient].append((act, act.date))
            else:
                acts_not_locked[act.patient] = [(act, act.date)]
        elif not act.is_state('VALIDE'):
            if act.patient in acts_not_valide:
                acts_not_valide[act.patient].append((act, act.get_state()))
            else:
                acts_not_valide[act.patient] = [(act, act.get_state())]
        elif not act.is_billable():
            if act.patient in acts_not_billable:
                acts_not_billable[act.patient].append(act)
            else:
                acts_not_billable[act.patient] = [act]
        elif act.pause:
            if act.patient in acts_pause:
                acts_pause[act.patient].append(act)
            else:
                acts_pause[act.patient] = [act]
        else:
            if act.patient in acts_billable:
                acts_billable[act.patient].append(act)
            else:
                acts_billable[act.patient] = [act]
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
    :type service: calebasse.ressources.Service

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
    for patient, acts in acts_billable.items():
        for act in acts:
            if patient.was_in_state_at_day(act.date, 'SUIVI'):
                if act.patient in acts_accepted:
                    acts_accepted[act.patient].append(act)
                else:
                    acts_accepted[act.patient] = [act]
            else:
                if act.patient in acts_bad_state:
                    acts_bad_state[act.patient]. \
                        append((act, 'NOT_ACCOUNTABLE_STATE'))
                else:
                    acts_bad_state[act.patient] = \
                        [(act, 'NOT_ACCOUNTABLE_STATE')]
    return (acts_not_locked, days_not_locked, acts_not_valide,
        acts_not_billable, acts_pause, acts_bad_state,
        acts_accepted)


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
    :type service: calebasse.ressources.Service

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
    for patient, acts in acts_billable.items():
        for act in acts:
            if patient.was_in_state_at_day(act.date,
                    'TRAITEMENT'):
                if not act.was_covered_by_notification():
                    if act.patient in acts_missing_valid_notification:
                        acts_missing_valid_notification[act.patient]. \
                            append(act)
                    else:
                        acts_missing_valid_notification[act.patient] = [act]
                else:
                    if act.patient in acts_accepted:
                        acts_accepted[act.patient].append(act)
                    else:
                        acts_accepted[act.patient] = [act]
            else:
                if act.patient in acts_bad_state:
                    acts_bad_state[act.patient]. \
                        append((act, 'NOT_ACCOUNTABLE_STATE'))
                else:
                    acts_bad_state[act.patient] = \
                        [(act, 'NOT_ACCOUNTABLE_STATE')]
    return (acts_not_locked, days_not_locked, acts_not_valide,
        acts_not_billable, acts_pause, acts_bad_state,
        acts_missing_valid_notification, acts_accepted)


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
    :type service: calebasse.ressources.Service

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
    for patient, acts in acts_billable.items():
        for act in acts:
            cared, hc = act.is_act_covered_by_diagnostic_healthcare()
            if cared:
                if act.patient in acts_diagnostic:
                    acts_diagnostic[act.patient]. \
                        append((act, hc))
                else:
                    acts_diagnostic[act.patient] = [(act, hc)]
            else:
                cared, hc = act.is_act_covered_by_treatment_healthcare()
                if cared:
                    if act.patient in acts_treatment:
                        acts_treatment[act.patient]. \
                            append((act, hc))
                    else:
                        acts_treatment[act.patient] = [(act, hc)]
                else:
                    if act.patient in acts_losts:
                        acts_losts[act.patient]. \
                            append(act)
                    else:
                        acts_losts[act.patient] = [act]
    return (acts_not_locked, days_not_locked, acts_not_valide,
        acts_not_billable, acts_pause, acts_diagnostic,
        acts_treatment, acts_losts)

def list_acts_for_billing_CMPP_2(end_day, service, acts=None):
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
    :type service: calebasse.ressources.Service

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
    for patient, acts in acts_billable.items():
        hcd = None
        len_acts_cared_diag = 0
        try:
            hcd = CmppHealthCareDiagnostic.objects.\
                filter(patient=patient).latest('start_date')
            # actes prise en charge par ce hc
            len_acts_cared_diag = len(hcd.act_set.all())
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
        for act in acts:
            cared = False
            if hcd and hcd.start_date <= act.date:
                # Ce qui seraient prise en charge
                nb_acts_cared = len_acts_cared_diag + count_hcd
                # Ne doit pas dépasser la limite de prise en charge du hc
                if nb_acts_cared < hcd.get_act_number() :
                    if nb_acts_cared < hcd.get_act_number():
                        if act.patient in acts_diagnostic:
                            acts_diagnostic[act.patient]. \
                                append((act, hcd))
                        else:
                            acts_diagnostic[act.patient] = [(act, hcd)]
                        count_hcd = count_hcd + 1
                        cared = True
            # The one before the last may be not full.
            if not cared and len(hcts) > 1 and hcts[1] and hcts[1].start_date <= act.date and hcts[1].end_date >= act.date:
                # Ce qui seraient prise en charge
                # ne doit pas dépasser la limite de prise en charge du hc
                if count_hct_1 < hcts[1].get_act_number() - hcts[1].get_nb_acts_cared():
                    if act.patient in acts_treatment:
                        acts_treatment[act.patient]. \
                            append((act, hcts[1]))
                    else:
                        acts_treatment[act.patient] = [(act, hcts[1])]
                    count_hct_1 = count_hct_1 + 1
                    cared = True
            if not cared and len(hcts) > 0 and hcts[0] and hcts[0].start_date <= act.date and hcts[0].end_date >= act.date:
                if count_hct_2 < hcts[0].get_act_number() - hcts[0].get_nb_acts_cared():
                    if act.patient in acts_treatment:
                        acts_treatment[act.patient]. \
                            append((act, hcts[0]))
                    else:
                        acts_treatment[act.patient] = [(act, hcts[0])]
                    count_hct_2 = count_hct_2 + 1
                    cared = True
            if not cared:
                if act.patient in acts_losts:
                    acts_losts[act.patient]. \
                        append(act)
                else:
                    # TODO: give details about rejection
                    acts_losts[act.patient] = [act]
    return (acts_not_locked, days_not_locked, acts_not_valide,
        acts_not_billable, acts_pause, acts_diagnostic,
        acts_treatment, acts_losts)
