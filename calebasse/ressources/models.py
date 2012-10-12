# -*- coding: utf-8 -*-

from django.db import models

class AnnexeEtablissement(models.Model):
    class Meta:
        verbose_name = u'Annexe d\'établissement'
        verbose_name_plural = u'Annexes d\'établissement'


class CaisseAssuranceMaladie(models.Model):
    class Meta:
        verbose_name = u'Caisse d\'assurances maladie'
        verbose_name_plural = u'Caisses d\'assurances maladie'


class CompagnieDeTransport(models.Model):
    class Meta:
        verbose_name = u'Compagnie de transport'
        verbose_name_plural = u'Compagnies de transport'


class CodeCFTMEA(models.Model):
    class Meta:
        verbose_name = u'Code CFTMEA'
        verbose_name_plural = u'Codes CFTMEA'


class CodeDeNonFacturation(models.Model):
    class Meta:
        verbose_name = u'Code de non-facturation'
        verbose_name_plural = u'Codes de non-facturation'


class Etablissement(models.Model):
    class Meta:
        verbose_name = u'Établissement'
        verbose_name_plural = u'Établissements'


class LieuDeScolarisation(models.Model):
    class Meta:
        verbose_name = u'Lieu de scolarisation'
        verbose_name_plural = u'Lieux de scolarisation'


class MotifInscription(models.Model):
    class Meta:
        verbose_name = u'Motif d\'inscription'
        verbose_name_plural = u'Motifs d\'inscription'


class Nationalite(models.Model):
    class Meta:
        verbose_name = u'Nationalité'
        verbose_name_plural = u'Nationalités'


class Profession(models.Model):
    class Meta:
        verbose_name = u'Profession'
        verbose_name_plural = u'Professions'


class Salle(models.Model):
    class Meta:
        verbose_name = u'Salles'
        verbose_name_plural = u'Salles'


class TarifDesSeance(models.Model):
    class Meta:
        verbose_name = u'Tarif des séances'
        verbose_name_plural = u'Tarifs des séances'


class Typesctes(models.Model):
    class Meta:
        verbose_name = u'Type d\'actes'
        verbose_name_plural = u'Types d\'actes'


class TypeAutoriteParentale(models.Model):
    class Meta:
        verbose_name = u'Type d\'autorité parentale'
        verbose_name_plural = u'Types d\'autorités parentales'


class TypeDeConseilleur(models.Model):
    class Meta:
        verbose_name = u'Types de conseilleurs'
        verbose_name_plural = u'Types de conseilleurs'


class TypeDeGardesParentales(models.Model):
    class Meta:
        verbose_name = u'Type de gardes parentales'
        verbose_name_plural = u'Types de gardes parentales'


class TypeDeSeances(models.Model):
    class Meta:
        verbose_name = u'Type de séance'
        verbose_name_plural = u'Types de séances'


class TypeDeSituationFamiliale(models.Model):
    class Meta:
        verbose_name = u'Type de situation familiale'
        verbose_name_plural = u'Types de situations familiales'


class TypeDeTransport(models.Model):
    class Meta:
        verbose_name = u'Type de transport'
        verbose_name_plural = u'Types de transports'


