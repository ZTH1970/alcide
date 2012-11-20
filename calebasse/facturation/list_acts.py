# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from calebasse.actes.validation import are_all_acts_of_the_day_locked


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

    from calebasse.actes.models import EventAct
    if acts is None:
        acts = EventAct.objects.filter(is_billed=False,
            patient__service=service).order_by('-date')
    # Filter acts according to the date
    i = 0
    for act in acts:
        # On enlève tous les acts sup au jour de l'end_date
        if datetime(act.date.year, act.date.month, act.date.day) <= \
                datetime(end_day.year, end_day.month, end_day.day):
            acts = acts[i:]
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
    acts_billable = {}
    locked = False
    for act in acts:
        current_day = datetime(act.date.year, act.date.month, act.date.day)
        locked = are_all_acts_of_the_day_locked(current_day)
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
        else:
            if act.patient in acts_billable:
                acts_billable[act.patient].append(act)
            else:
                acts_billable[act.patient] = [act]
    return (acts_not_locked, days_not_locked, acts_not_valide,
        acts_not_billable, acts_billable)


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
        acts_not_billable, acts_billable = \
            list_acts_for_billing_first_round(end_day, service,
                start_day, acts=acts)
    acts_bad_state = {}
    acts_accepted = {}
    for patient, acts in acts_billable.items():
        for act in acts:
            if patient.was_in_state_at_day(act.date, 'CAMSP_STATE_SUIVI'):
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
        acts_not_billable, acts_bad_state,
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
        acts_not_billable, acts_billable = \
            list_acts_for_billing_first_round(end_day, service,
                start_day=start_day, acts=acts)
    acts_bad_state = {}
    acts_missing_valid_notification = {}
    acts_accepted = {}
    for patient, acts in acts_billable.items():
        for act in acts:
            if patient.was_in_state_at_day(act.date,
                    'SESSAD_STATE_TRAITEMENT'):
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
        acts_not_billable, acts_bad_state, acts_missing_valid_notification,
        acts_accepted)


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
        acts_not_billable, acts_billable = \
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
        acts_not_billable, acts_diagnostic, acts_treatment,
        acts_losts)
