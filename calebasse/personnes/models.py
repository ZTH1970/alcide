# -*- coding: utf-8 -*-

from datetime import datetime, date

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.template.defaultfilters import date as date_filter

from calebasse.ressources.models import WorkerType, Service
from calebasse.models import WeekdayField, BaseModelMixin

from interval import Interval

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

    class Meta:
        ordering = ['last_name', 'first_name']

class WorkerManager(models.Manager):

    def for_service(self, service, type=None):
        if type:
            return self.filter(services__in=[service]).filter(type=type)
        else:
            return self.filter(services__in=[service])

class Worker(People):
    objects = WorkerManager()
    # TODO : use manytomany here ?
    type = models.ForeignKey('ressources.WorkerType',
            verbose_name=u'Type de personnel')
    services = models.ManyToManyField('ressources.Service')

    def is_away(self):
        day = WeekdayField.WEEKDAYS[date.today().weekday()]
        if self.timetable_set.filter(weekday=day).exists():
            return False
        return True

    class Meta:
        verbose_name = u'Personnel'
        verbose_name_plural = u'Personnels'


class UserWorker(BaseModelMixin, User):
    worker = models.ForeignKey('Worker',
            verbose_name=u'Personnel')

    def __unicode__(self):
        return u'Lien entre la personne %s et l\'utilisateur %s' % (
                self.people, super(UserWorker, self).__unicode__())

class SchoolTeacher(People):
    schools = models.ManyToManyField('ressources.School')
    role = models.ForeignKey('ressources.SchoolTeacherRole')

class TimeTableManager(models.Manager):
    def current(self):
        today = date.today()
        return self.filter(start_date__lte=today, end_date__gte=today)

class TimeTable(BaseModelMixin, models.Model):
    objects = TimeTableManager()
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

    def to_interval(self, date):
        return Interval(datetime.combine(date, self.start_time),
                datetime.combine(date, self.end_time))

class HolidayManager(models.Manager):
    def for_worker(self, worker):
        query = models.Q(worker=worker) \
              | models.Q(worker__isnull=True,
                           service=worker.services.all())
        return self.filter(query) \
                   .filter(end_date__gte=date.today())

    def for_service(self, service):
        return self.filter(worker__isnull=True) \
                   .filter(models.Q(service=service)
                          |models.Q(service__isnull=True)) \
                   .filter(end_date__gte=date.today())

    def for_service_workers(self, service):
        return self.filter(worker__services=service,
                end_date__gte=date.today())

def time2french(time):
    if time.minute:
        return '{0}h{1}'.format(time.hour, time.minute)
    return '{0}h'.format(time.hour)

class Holiday(BaseModelMixin, models.Model):
    objects = HolidayManager()

    worker = models.ForeignKey(Worker, blank=True, null=True,
            verbose_name=u"Personnel")
    service = models.ForeignKey(Service, blank=True, null=True,
            verbose_name=u"Service")
    start_date = models.DateField(verbose_name=u"Date de début")
    end_date = models.DateField(verbose_name=u"Date de fin")
    start_time = models.TimeField(verbose_name=u"Horaire de début", blank=True,
            null=True)
    end_time = models.TimeField(verbose_name=u"Horaire de fin", blank=True,
            null=True)

    class Meta:
        verbose_name = u'Congé'
        verbose_name_plural = u'Congés'
        ordering = ('start_date', 'start_time')

    def is_current(self):
        return self.start_date <= date.today() <= self.end_date

    def __unicode__(self):
        ret = ''
        if self.start_date == self.end_date:
            ret = u'le {0}'.format(date_filter(self.start_date, 'j F Y'))
            if self.start_time and self.end_time:
                ret += u', de {0} à {1}'.format(time2french(self.start_time),
                time2french(self.end_time))
        else:
            ret = u'du {0} au {1}'.format(
                    date_filter(self.start_date, 'j F'),
                    date_filter(self.end_date, 'j F Y'))
        return ret

