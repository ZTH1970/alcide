# -*- coding: utf-8 -*-
"""
    Création du fichier d'importation d'ecritures comptables pour le logiciel
    prog'or

    Fichier texte format ANSI
    Lignes se terminent par un retour chariat et une fin de ligne (RC/LF soit
    13 et 10 en ACSII)

    Nom du fichier libre.
"""

def pad_str(chaine, len_pad):
    return chaine + ''.join([' ' for i in range(len_pad - len(chaine))])

def pad_str_0(chaine, len_pad):
    return '0'.join([' ' for i in range(len_pad - len(chaine))]) + chaine

def pad_int(montant, len_pad):
    montant = str(montant)
    return ''.join(['0' for i in range(len_pad - len(montant))]) + montant


class IdentificationJournal():

    def __init__(self):
        self.enregistrement = 'A'
        self.origine = '1' #Windows'
        self.code = 'FAC'
        self.intitule = pad_str('FACTURATION', 30)
        self.type = '1'
        self.type_pre = '0'
        self.centraliseur = ''
        self.centraliseur_intitule = ''
        self.ecritures = list()

    def add_ecriture(self, ecriture):
        self.ecritures.append(ecriture)

    def check_ecritures(self):
        '''
            Le total des écritures doit être égale à 0
        '''
        montant = 0
        for ecriture in self.ecritures:
            if not ecriture.check_echeances() or \
                    not ecriture.check_imputations():
                return False
            montant += ecriture.credit - ecriture.debit
        if montant:
            return False
        return True

    def render(self):
        if not self.check_ecritures():
            return None
        line = self.enregistrement + self.origine + self.code + \
            self.intitule + self.type + self.type_pre + self.centraliseur + \
            self.centraliseur_intitule
        line = pad_str(line, 255)
        lines = [line]
        lines.extend([ecriture.render() for ecriture in self.ecritures])
        line_sep = chr(10)
        res = line_sep.join(lines)
        return res + chr(13)

class EcritureComptable():

    def __init__(self, date, compte, intitule_compte, num_facturation,
            type_compte='2',
            compte_principale_defaut='41100000', compte_principale='41100000',
            intitule_compte_principal='Compte principal 411',
            credit=0, debit=0, quantite=0):
        if len(date) != 10 or len(compte) != 8:
            return None
        self.enregistrement = 'B'
        self.date = date
        self.monnaie = '1' #Euros
        self.compte = pad_str_0(compte, 8)
        self.intitule_compte = pad_str(intitule_compte, 30)
        self.type_compte = type_compte
        self.compte_principale_defaut = pad_str_0(compte_principale_defaut, 8)
        self.compte_principale = pad_str_0(compte_principale, 8)
        self.intitule_compte_principal = pad_str(intitule_compte_principal, 30)
        if self.type_compte == '0':
            self.compte_principale_defaut = pad_str('', 8)
            self.compte_principale = pad_str('', 8)
            self.intitule_compte_principal = pad_str('', 30)
        self.credit = credit
        self.debit = debit
        self.quantite = quantite
        self.nature_quantite = pad_str('', 20)
        libelle = 'FACTURATION CYCLE ' + num_facturation
        self.libelle_principale = pad_str(libelle, 30)
        self.libelle_secondaire = pad_str('', 30)
        self.lettrable = '0'
        self.piece = pad_str('', 10)
        self.rapprochement = '0'
        self.echeances = list()
        self.imputations = list()

    def add_echeance(self, echeance):
        self.echeances.append(echeance)

    def check_echeances(self):
        '''
            Le total des échéance doit être égale au montant de l'écriture
        '''
        return True

    def add_imputation(self, imputation):
        self.imputations.append(imputation)

    def check_imputations(self):
        '''
            Le total des imputations doit être égale au montant de l'écriture
        '''
        montant = 0
        for imputation in self.imputations:
            montant += imputation.credit - imputation.debit
        if montant >= 0 and montant == self.credit:
            return True
        if montant < 0 and abs(montant) == self.debit:
            return True
        return False

    def render(self):
        self.credit = pad_int(self.credit, 15)
        self.debit = pad_int(self.debit, 15)
        self.quantite = pad_int(self.quantite, 15)
        line = self.enregistrement + self.date + self.monnaie + self.compte + \
            self.intitule_compte + self.type_compte + \
            self.compte_principale_defaut + self.compte_principale + \
            self.intitule_compte_principal + self.debit + self.credit + \
            self.quantite + self.nature_quantite + self.libelle_principale + \
            self.libelle_secondaire + self.lettrable + self.piece + \
            self.rapprochement
        line = pad_str(line, 255)
        lines = [line]
        lines.extend([echeance.render() for echeance in self.echeances])
        lines.extend([imputation.render() for imputation in self.imputations])
        line_sep = chr(10)
        res = line_sep.join(lines)
        return res

class EcheancePaiement():

    def __init__(self):
        self.enregistrement = 'C'

    def render_to_ascii(self):
        return None

class ImputationAnalytique():

    def __init__(self, credit=0, debit=0, quantite=0):
        self.enregistrement = 'D'
        self.compte_ana = pad_str('CMPP', 8)
        self.intitule = pad_str('Compte analytique CMPP', 30)
        self.credit = credit
        self.debit = debit
        self.quantite = quantite
        self.nature_quantite = pad_str('', 20)

    def render(self):
        self.credit = pad_int(self.credit, 15)
        self.debit = pad_int(self.debit, 15)
        self.quantite = pad_int(self.quantite, 15)
        line = self.enregistrement + self.compte_ana + self.intitule + \
            self.debit + self.credit + \
            self.quantite + self.nature_quantite
        line = pad_str(line, 255)
        return line
