from django.db.models.signals import post_save, pre_delete
from ..middleware.request import get_request

import django_journal

from alcide.agenda.models import Event, EventWithAct, EventType
from alcide.actes.models import ActValidationState, Act
from alcide.dossiers.models import FileState, PatientRecord, PatientAddress, PatientContact
from alcide.personnes.models import People, Worker, ExternalWorker, ExternalTherapist, Holiday

def object_save(sender, **kwargs):
    model_name = sender.__name__.lower()
    if kwargs.get('created'):
        tag = 'new-%s' % model_name
        log = '{obj} created'
    else:
        tag = '%s-save' % model_name
        log = '{obj} saved'

    obj = kwargs['instance']
    try:
        get_request().record(tag, log, obj=obj)
    except AttributeError:
        django_journal.record(tag, '{obj} from shell', obj=obj)

def object_delete(sender, **kwargs):
    model_name = sender.__name__.lower()
    try:
        get_request().record('delete-%s' % model_name,
                             '{obj}',
                             obj=kwargs['instance'])
    except AttributeError:
        django_journal.record('delete-%s' % model_name,
                              '{obj} from shell', obj=kwargs['instance'])

for model in (Event, EventWithAct, EventType, ActValidationState, Act,
              FileState, PatientRecord, PatientAddress, PatientContact,
              People, Worker, ExternalWorker, ExternalTherapist, Holiday):
    post_save.connect(object_save, sender=model)
    pre_delete.connect(object_delete, sender=model)

