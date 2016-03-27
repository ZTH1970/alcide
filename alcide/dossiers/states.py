# -*- coding: utf-8 -*-
'''
    The state name is for instance the string 'CMPP_STATE_ACCUEIL'
    The value given in the dictionnary can only be used for display.
'''

# Generic states name
STATE_CHOICES = (
        (0, 'En contact'),
        (1, "Fin d'accueil"),
        (2, 'En diagnostic'),
        (3, 'En traitement'),
        (4, 'Clos'),
)

STATE_CHOICES_TYPE = {
        '0': 'ACCUEIL',
        '1': 'FIN_ACCUEIL',
        '2': 'DIAGNOSTIC',
        '3': 'TRAITEMENT',
        '4': 'CLOS',
        }

# Map Status type with a generic state name
STATES_MAPPING = {
    'ACCUEIL': STATE_CHOICES[0][1],
    'FIN_ACCUEIL': STATE_CHOICES[1][1],
    'DIAGNOSTIC': STATE_CHOICES[2][1],
    'TRAITEMENT': STATE_CHOICES[3][1],
    'CLOS': STATE_CHOICES[4][1]
}

# Use to map status type with change state buttons
STATES_BTN_MAPPER = {
        'ACCUEIL': ('reopen-patientrecord', 'Ré-accueillir'),
        'FIN_ACCUEIL': ('finaccueil-patientrecord', "Fin d'accueil"),
        'DIAGNOSTIC': ('diagnostic-patientrecord', 'En diagnostic'),
        'TRAITEMENT': ('traitement-patientrecord', 'En traitement'),
        'CLOS': ('close-patientrecord', 'Clore'),
        'CLOS_RDV': ('close-rdv-patientrecord', 'Clore'),
        'BILAN': ('bilan-patientrecord', 'En bilan'),
        'SURVEILLANCE': ('surveillance-patientrecord', 'En surveillance'),
        'SUIVI': ('suivi-patientrecord', 'En suivi'),
}

# OLD MAPPERS now manage in databases with dossiers.Status table

# CMPP States
#CMPP_STATE_ACCUEIL = "En contact"
#CMPP_STATE_FIN_ACCUEIL = "Fin d'accueil"
#CMPP_STATE_DIAGNOSTIC = "Diagnostic"
#CMPP_STATE_TRAITEMENT = "Traitement"
#CMPP_STATE_CLOS = "Clos"
#CMPP_STATES = {'CMPP_STATE_ACCUEIL': CMPP_STATE_ACCUEIL,
#    'CMPP_STATE_FIN_ACCUEIL': CMPP_STATE_FIN_ACCUEIL,
#    'CMPP_STATE_DIAGNOSTIC': CMPP_STATE_DIAGNOSTIC,
#    'CMPP_STATE_TRAITEMENT': CMPP_STATE_TRAITEMENT,
#    'CMPP_STATE_CLOS': CMPP_STATE_CLOS}
#
## CAMSP States
#CAMSP_STATE_ACCUEIL = "En contact"
#CAMSP_STATE_FIN_ACCUEIL = "Fin d'accueil"
#CAMSP_STATE_BILAN = "Bilan"
#CAMSP_STATE_SURVEILLANCE = "Surveillance"
#CAMSP_STATE_SUIVI = "Suivi"
#CAMSP_STATE_CLOS = "Clos"
#CAMSP_STATES = {'CAMSP_STATE_ACCUEIL': CAMSP_STATE_ACCUEIL,
#    'CAMSP_STATE_FIN_ACCUEIL': CAMSP_STATE_FIN_ACCUEIL,
#    'CAMSP_STATE_BILAN': CAMSP_STATE_BILAN,
#    'CAMSP_STATE_SURVEILLANCE': CAMSP_STATE_SURVEILLANCE,
#    'CAMSP_STATE_SUIVI': CAMSP_STATE_SUIVI,
#    'CAMSP_STATE_CLOS': CAMSP_STATE_CLOS}
#
## SESSAD States
#SESSAD_STATE_ACCUEIL = "En contact"
#SESSAD_STATE_FIN_ACCUEIL = "Fin d'accueil"
#SESSAD_STATE_TRAITEMENT = "Traitement"
#SESSAD_STATE_CLOS = "Clos"
#SESSAD_STATES = {'SESSAD_STATE_ACCUEIL': SESSAD_STATE_ACCUEIL,
#    'SESSAD_STATE_FIN_ACCUEIL': SESSAD_STATE_FIN_ACCUEIL,
#    'SESSAD_STATE_TRAITEMENT': SESSAD_STATE_TRAITEMENT,
#    'SESSAD_STATE_CLOS': SESSAD_STATE_CLOS}
#
#STATES = {'CMPP' : CMPP_STATES,
#    'CAMSP': CAMSP_STATES,
#    'SESSAD': SESSAD_STATES}
#
#STATE_ACCUEIL = {'CMPP' : 'CMPP_STATE_ACCUEIL',
#    'CAMSP': 'CAMSP_STATE_ACCUEIL',
#    'SESSAD': 'SESSAD_STATE_ACCUEIL',
#    }

#STATES_MAPPING = dict(CMPP_STATES, **CAMSP_STATES)
#STATES_MAPPING = dict(STATES_MAPPING, **SESSAD_STATES)
