# -*- coding: utf-8 -*-

LARGE_REGIME_CHOICES=(
        ('01', '01 REGIME GENERAL'),
        ('02', '02 REGIME AGRICOLE'),
        ('03', '03 ASSURANCE MALADIE DES PROFESSIONS INDEPENDANTES (AMPI)'),
        ('04', '04 S.N.C.F'),
        ('05', '05 R.A.T.P'),
        ('06', '06 ETABLISSEMENT NATIONAL DES INVALIDES DE LA MARINE (ENIM)'),
        ('07', '07 MINEURS ET ASSIMILES'),
        ('08', '08 MILITAIRES DE CARRIERE'),
        ('09', '09 PERSONNEL DE LA BANQUE DE FRANCE'),
        ('10', '10 CLERS ET EMPLOYES DE NOTAIRES'),
        ('12', "12 CHAMBRE DE COMMERCE ET D'INDUSTRIE DE PARIS"),
        ('14', '14 ASSEMBLEE NATIONALE'),
        ('15', '15 SENAT'),
        ('16', '16 PORT AUTONOME DE BORDEAUX'),
        ('17', "17 CAISSE DES FRANCAIS A L'ETRANGER"),
        ('80', '80 MINISTERE DES ANCIENS COMBATTANTS'),
        ('90', "90 CAISSE D'ASSURANCE VIEILLESSE, INVALIDITE ET MALADIE DES CULTES"),
        ('91', "91 MUTUELLE GENERALE DE L'EDUCATION NATIONALE - M.G.E.N -"),
        ('92', "92 MUTUELLE GENERALE - M.G - (ex PTT)"),
        ('93', "93 MUTUELLE GENERALE DE LA POLICE"),
        ('94', "94 MUTUELLES DES FONCTIONNAIRES - SLI -"),
        ('95', '95 M.N. HOSPITALIERS'),
        ('96', "96 MUTUELLE NATIONALE DE L'AVIATION ET DE LA MARINE"),
        ('99', '99 AUTRES MUTUELLES'),
)

TYPE_OF_CONTRACT_CHOICES = (
        # Codification dans B2, nom
        ('89', 'CMU - Couverture maladie universelle'),
        ('04', 'AME - Aide médicale d\'État'),
        #('XX', 'ACS - Aide pour une complémentaire santé'),
)

DEFICIENCY_CHOICES = (
    (0, 'Non'),
    (1, 'A titre principal'),
    (2, 'A titre associé'),
)
