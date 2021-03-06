# -*- coding: utf-8 -*-

import datetime
import models
from django.db import transaction

def get_acts_of_the_day(date, service=None):
    if not isinstance(date, datetime.date):
        date = date.date()
    qs = models.Act.objects.filter(date=date)
    if service:
        qs = qs.filter(patient__service=service)
    return qs.order_by('date')


def unlock_all_acts_of_the_day(date, service=None):
    get_acts_of_the_day(date, service).update(validation_locked=False)


def get_acts_not_locked_of_the_day(date, service=None):
    return get_acts_of_the_day(date, service) \
            .filter(validation_locked=False)


def are_all_acts_of_the_day_locked(date, service=None):
    return not get_acts_not_locked_of_the_day(date, service).exists()


def get_days_with_acts_not_locked(start_day, end_day, service=None):
    qs = models.Act.objects.filter(date__gte=start_day,
            date__lte=end_day, validation_locked=False)
    if service:
        qs = qs.filter(patient__service=service)
    return sorted(set(qs.values_list('date', flat=True)))


def date_generator(from_date, to_date):
    while from_date < to_date:
        yield from_date
        from_date += datetime.timedelta(days=1)


def get_days_with_all_acts_locked(start_day, end_day, service=None):
    locked_days = get_days_with_acts_not_locked(start_day, end_day,
            service)
    return sorted(set(date_generator(start_day, end_day)) - set(locked_days))


@transaction.commit_manually
def automated_validation(date, service, user, commit=True):
    nb_acts_double = 0
    nb_acts_validated = 0
    nb_acts_abs_non_exc = 0
    nb_acts_abs_exc = 0
    nb_acts_abs_inter = 0
    nb_acts_annul_nous = 0
    nb_acts_annul_famille = 0
    nb_acts_reporte = 0
    nb_acts_abs_ess_pps = 0
    nb_acts_enf_hosp = 0
    nb_acts_losts = 0
    acts_of_the_day = get_acts_of_the_day(date, service)
    for act in acts_of_the_day:
        if act.is_state('ABS_NON_EXC'):
            nb_acts_abs_non_exc = nb_acts_abs_non_exc + 1
        if act.is_state('ABS_EXC'):
            nb_acts_abs_exc = nb_acts_abs_exc + 1
        if act.is_state('ABS_INTER'):
            nb_acts_abs_inter = nb_acts_abs_inter + 1
        if act.is_state('ANNUL_NOUS'):
            nb_acts_annul_nous = nb_acts_annul_nous + 1
        if act.is_state('ANNUL_FAMILLE'):
            nb_acts_annul_famille = nb_acts_annul_famille + 1
        if act.is_state('REPORTE'):
            nb_acts_reporte = nb_acts_reporte + 1
        if act.is_state('ABS_ESS_PPS'):
            nb_acts_abs_ess_pps = nb_acts_abs_ess_pps + 1
        if act.is_state('ENF_HOSP'):
            nb_acts_enf_hosp = nb_acts_enf_hosp + 1
        if act.is_state('ACT_LOST') or act.is_lost:
            nb_acts_losts = nb_acts_losts + 1
        if not act.get_state():
            act.set_state('VALIDE', author=user, auto=True)

    nb_acts_total = len(acts_of_the_day)
    patients = {}
    if service.name == 'CMPP':
        # Verification des actes en doubles
        acts = [act for act in acts_of_the_day \
            if not act.is_lost and (act.is_state('VALIDE') or
                act.is_state('NON_VALIDE') or act.is_state('ACT_DOUBLE'))]
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
                acts_t = []
                for act in acts:
                    if act.is_billed:
                        found_one = True
                        nb_acts_validated = nb_acts_validated + 1
                    else:
                        acts_t.append(act)
                for act in acts_t:
                    if not found_one or not act.is_billable():
                        if not act.is_state('VALIDE') and commit:
                            act.set_state('VALIDE', author=user, auto=True)
                        if act.is_billable():
                            found_one = True
                        nb_acts_validated = nb_acts_validated + 1
                    else:
                        if commit:
                            act.set_state('ACT_DOUBLE', author=user, auto=True)
                        nb_acts_double = nb_acts_double + 1
            else:
                if not acts[0].is_state('VALIDE') and commit:
                    acts[0].set_state('VALIDE', author=user, auto=True)
                nb_acts_validated = nb_acts_validated + 1
    else:
        acts = [act for act in acts_of_the_day if act.is_state('NON_VALIDE') or act.is_state('ACT_DOUBLE')]
        for act in acts:
            if commit:
                act.set_state('VALIDE', author=user, auto=True)
            nb_acts_validated = nb_acts_validated + 1

    for act in acts_of_the_day:
        if commit and (act.is_lost or act.is_billed):
            state = act.get_state()
            if not state or state.state_name == 'NON_VALIDE':
                act.set_state('VALIDE', author=user, auto=True)

    # Acts locking
    for act in acts_of_the_day:
        if commit:
            act.validation_locked = True
            act.save()
    if service.name == 'CMPP' and commit:
        for patient, _ in patients.items():
            patient.create_diag_healthcare(user)
            patient.automated_switch_state(user)
    transaction.commit()
    return (nb_acts_total, nb_acts_validated, nb_acts_double,
        nb_acts_abs_non_exc, nb_acts_abs_exc, nb_acts_abs_inter, nb_acts_annul_nous,
        nb_acts_annul_famille, nb_acts_reporte, nb_acts_abs_ess_pps,
        nb_acts_enf_hosp, nb_acts_losts)
