import os

from transport_template import TransportTemplate


def render_transport(patient, address, data={}):
    template_path = os.path.join(
            os.path.dirname(__file__),
            'static',
            'dossiers',
            'cerfa_50742_03_prescription_transport.pdf')
    tpl = TransportTemplate(
            template_path=template_path,
            prefix='transport_filled', suffix='.pdf')
    name = ''
    if patient.last_name:
        name = patient.last_name.upper()
    ctx = {'NOM_BENEFICIAIRE': name,
        'PRENOM_BENEFICIAIRE': patient.first_name or '',
        'DATE': data.get('date', ''),
        'LIEU': data.get('lieu', ''),
        'IDENTIFICATION_ETABLISSEMENT': data.get('id_etab', ''),
        'SITUATION_CHOICE_1': 'situation_choice_1' in data,
        'SITUATION_CHOICE_2': 'situation_choice_2' in data,
        'SITUATION_CHOICE_3': 'situation_choice_3' in data,
        'SITUATION_CHOICE_4': 'situation_choice_4' in data,
        'SITUATION_DATE': data.get('situation_date', ''),
        'TRAJET_TEXT': data.get('trajet_text', ''),
        'TRAJET_CHOICE_1': 'trajet_choice_1' in data,
        'TRAJET_CHOICE_2': 'trajet_choice_2' in data,
        'TRAJET_CHOICE_3': 'trajet_choice_3' in data,
        'TRAJET_CHOICE_4': 'trajet_choice_4' in data,
        'TRAJET_NUMBER': data.get('trajet_number', ''),
        'PC_CHOICE_1': 'pc_choice_1' in data,
        'PC_CHOICE_2': 'pc_choice_2' in data,
        'MODE_CHOICE_1': 'mode_choice_1' in data,
        'MODE_CHOICE_2': 'mode_choice_2' in data,
        'MODE_CHOICE_3': 'mode_choice_3' in data,
        'MODE_CHOICE_4': 'mode_choice_4' in data,
        'MODE_CHOICE_5': 'mode_choice_5' in data,
        'MODE_CHOICE_6': 'mode_choice_6' in data,
        'CDTS_CHOICE_1': 'cdts_choice_1' in data,
        'CDTS_CHOICE_2': 'cdts_choice_2' in data,
        }
    if patient.policyholder.id != patient.id:
        policy_holder_full_name = ''
        if patient.policyholder.last_name.upper:
            policy_holder_full_name = \
                patient.policyholder.last_name.upper() + ' '
        if patient.policyholder.first_name:
            policy_holder_full_name += patient.policyholder.first_name
        ctx['NOM_ASSURE'] = policy_holder_full_name
    if patient.policyholder.social_security_id:
        ctx['NIR_ASSURE'] = \
            u'  '.join(patient.policyholder.social_security_id)
        key = str(patient.policyholder.get_control_key())
        if len(key) == 1:
            key = '0' + key
        ctx['NIR_KEY_ASSURE'] = \
            u'  '.join(key)
    if patient.policyholder.health_center:
        ctx['CODE_ORGANISME_1'] = \
            u'  '.join(patient.policyholder.health_center.large_regime.code)
        ctx['CODE_ORGANISME_2'] = \
            u'  '.join(patient.policyholder.health_center.dest_organism)
        ctx['CODE_ORGANISME_3'] = \
            u'  '.join(patient.policyholder.other_health_center
                or patient.policyholder.health_center.code)
    if address:
        ctx['ADRESSE_BENEFICIAIRE'] = address.display_name
    return tpl.generate(ctx)
