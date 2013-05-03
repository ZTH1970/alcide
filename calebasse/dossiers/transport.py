import os
import datetime

from transport_template import TransportTemplate


def render_transport(patient, address):
    template_path = os.path.join(
            os.path.dirname(__file__),
            'static',
            'dossiers',
            'cerfa_50742_03_prescription_transport.pdf')
    tpl = TransportTemplate(
            template_path=template_path,
            prefix='transport_filled', suffix='.pdf')
    ctx = {
            'NOM_BENEFICIAIRE': u' '.join(patient.last_name.upper()),
            'PRENOM_BENEFICIAIRE': u' '.join(patient.first_name),
            'DATE': datetime.datetime.now().strftime('%d%m%Y'),
            'LIEU': 'Saint-Etienne',
            'IDENTIFICATION_ETABLISSEMENT': '''%s SAINT ETIENNE
66/68, RUE MARENGO
42000 SAINT ETIENNE''' % patient.service.name,
        }
    if patient.policyholder.id != patient.id:
        policy_holder_full_name = ''
        if patient.policyholder.last_name.upper:
            policy_holder_full_name = \
                patient.policyholder.last_name.upper() + ' '
        if patient.policyholder.first_name:
            policy_holder_full_name += patient.policyholder.first_name
        ctx['NOM_ASSURE'] = u' '.join(policy_holder_full_name)
    if patient.policyholder.social_security_id:
        ctx['NIR_ASSURE'] = \
            u'  '.join(patient.policyholder.social_security_id)
        ctx['NIR_KEY_ASSURE'] = \
            u'  '.join(str(patient.policyholder.get_control_key()))
    if patient.policyholder.health_center:
        ctx['CODE_ORGANISME_1'] = \
            u'  '.join(patient.policyholder.health_center.large_regime.code)
        ctx['CODE_ORGANISME_2'] = \
            u'  '.join(patient.policyholder.health_center.dest_organism)
        ctx['CODE_ORGANISME_3'] = \
            u'  '.join(patient.policyholder.other_health_center
                or patient.policyholder.health_center.code)
    if address:
        ctx['ADRESSE_BENEFICIAIRE'] = u' '.join(address.display_name)
    return tpl.generate(ctx)
