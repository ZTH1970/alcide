# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

from calebasse.models import WeekdayField, BaseModelMixin

class People(BaseModelMixin, models.Model):
    last_name = models.CharField(max_length=128, verbose_name=u'Nom')
    first_name = models.CharField(max_length=128, verbose_name=u'Prénom(s)')
    display_name = models.CharField(max_length=256,
            verbose_name=u'Nom complet', editable=False)

    def save(self, **kwargs):
        self.display_name = self.first_name + ' ' + self.last_name
        super(People, self).save(**kwargs)

    def __unicode__(self):
        return self.display_name

class Worker(People):
    type = models.ForeignKey('ressources.WorkerType',
            verbose_name=u'Type de personnel')
    services = models.ManyToManyField('ressources.Service')

    class Meta:
        verbose_name = u'Personnel'
        verbose_name_plural = u'Personnels'

class UserWorker(BaseModelMixin, User):
    worker = models.ForeignKey('Worker',
            verbose_name=u'Personnel')

    def __unicode__(self):
        return u'Lien entre la personne %s et l\'utilisateur %s' % (
                self.people, super(UserPeople, self).__unicode__())

class SchoolTeacher(People):
    schools = models.ManyToManyField('ressources.School')
    role = models.ForeignKey('ressources.SchoolTeacherRole')

class TimeTable(BaseModelMixin, models.Model):
    worker = models.ForeignKey(Worker,
            verbose_name=u'Intervenant')
    service = models.ForeignKey('ressources.Service')
    weekday = WeekdayField(
            verbose_name=u'Jour')
    start_time = models.TimeField(
        verbose_name=u'Heure de début')
    end_time = models.TimeField(
        verbose_name=u'Heure de fin')
    start_date = models.DateField(
        verbose_name=u'Début')
    end_date = models.DateField(
        verbose_name=u'Fin', blank=True, null=True)

    def __unicode__(self):
        s = u'%s pour le %s le %s de %s à %s' % \
                (self.worker, self.service, self.weekday, self.start_time,
                        self.end_time)
        if self.end_time:
            s += u' à partir du %s' % self.start_date
        else:
            s += u' du %s au %s' % (self.start_data, self.end_date)
        return s

    class Meta:
        verbose_name = u'Emploi du temps'
        verbose_name_plural = u'Emplois du temps'
