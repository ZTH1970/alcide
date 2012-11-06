# -*- coding: utf-8 -*-
import datetime

from django.db import transaction


def get_acts_of_the_day(date):
    from models import EventAct
    return EventAct.objects.filter(date__year=date.year,
        date__month=date.month, date__day=date.day).order_by('date')


def unlock_all_acts_of_the_day(date):
    for act in get_acts_of_the_day(date):
        act.validation_locked = False


def are_all_acts_of_the_day_locked(date):
    for act in get_acts_of_the_day(date):
        if not act.validation_locked:
            return False
    return True


def get_acts_not_locked_of_the_day(date):
    acts = []
    for act in get_acts_of_the_day(date):
        if not act.validation_locked:
            acts.append(act)
    return acts


def get_days_with_acts_not_locked(start_day, end_day):
    num_days = abs((start_day - end_day).days) + 1
    days_list = [start_day + datetime.timedelta(days=x) \
        for x in range(0, num_days)]
    result = []
    for day in days_list:
        if not are_all_acts_of_the_day_locked(day):
            result.append(day)
    return result


def get_days_with_all_acts_locked(start_day, end_day):
    num_days = abs((start_day - end_day).days) + 1
    days_list = [start_day + datetime.timedelta(days=x) \
        for x in range(0, num_days)]
    result = []
    for day in days_list:
        if are_all_acts_of_the_day_locked(day):
            result.append(day)
    return result


def automated_validation(date, service, user, commit=True):
    nb_acts_double = 0
    nb_acts_validated = 0
    nb_acts_abs_non_exc = 0
    nb_acts_abs_exc = 0
    nb_acts_annul_nous = 0
    nb_acts_annul_famille = 0
    nb_acts_abs_ess_pps = 0
    nb_acts_enf_hosp = 0
    acts_of_the_day = get_acts_of_the_day(date)
    for act in acts_of_the_day:
        if act.is_state('ABS_NON_EXC'):
            nb_acts_abs_non_exc = nb_acts_abs_non_exc + 1
        if act.is_state('ABS_EXC'):
            nb_acts_abs_exc = nb_acts_abs_exc + 1
        if act.is_state('ANNUL_NOUS'):
            nb_acts_annul_nous = nb_acts_annul_nous + 1
        if act.is_state('ANNUL_FAMILLE'):
            nb_acts_annul_famille = nb_acts_annul_famille + 1
        if act.is_state('ABS_ESS_PPS'):
            nb_acts_abs_ess_pps = nb_acts_abs_ess_pps + 1
        if act.is_state('ENF_HOSP'):
            nb_acts_enf_hosp = nb_acts_enf_hosp + 1

    nb_acts_total = len(acts_of_the_day)
    patients = {}
    if service.name == 'CMPP':
        # Verification des actes en doubles
        acts = [act for act in acts_of_the_day \
            if act.get_state().state_name in ('VALIDE', 'NON_VALIDE',
                'ACT_DOUBLE')]
        for act in acts:
            if act.patient not in patients:
                patients[act.patient] = []
            patients[act.patient].append(act)
        for patient, acts in patients.items():
            if len(acts) > 1:
                # Si plusieurs actes pour un même patient le même jour
                # On valide le premier, s'il n'est pas déja validé.
                # Les autres sont marqués actes en double
                found_one = False
                for act in acts:
                    if not found_one:
                        if not act.is_state('VALIDE') and commit:
                            act.set_state('VALIDE', author=user, auto=True)
                        found_one = True
                        nb_acts_validated = nb_acts_validated + 1
                    else:
                        if commit:
                            act.set_state('ACT_DOUBLE', author=user, auto=True)
                        nb_acts_double = nb_acts_double + 1
            else:
                if acts[0].is_state('NON_VALIDE') and commit:
                    acts[0].set_state('VALIDE', author=user, auto=True)
                nb_acts_validated = nb_acts_validated + 1
    else:
        acts = [act for act in acts_of_the_day if act.is_state('NON_VALIDE')]
        for act in acts:
            if commit:
                act.set_state('VALIDE', author=user, auto=True)
            nb_acts_validated = nb_acts_validated + 1

    # Acts locking
    for act in acts_of_the_day:
        if commit:
            act.validation_locked = True
            act.save()
    if service.name == 'CMPP' and commit:
        for patient, _ in patients.items():
            patient.create_diag_healthcare(user)
            patient.automated_switch_state(user)
    return (nb_acts_total, nb_acts_validated, nb_acts_double,
        nb_acts_abs_non_exc, nb_acts_abs_exc, nb_acts_annul_nous,
        nb_acts_annul_famille, nb_acts_abs_ess_pps,
        nb_acts_enf_hosp)
