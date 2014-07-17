from django.db.models.signals import post_save, pre_delete
from ..middleware.request import get_request

from calebasse.agenda.models import Event, EventWithAct, EventType
from calebasse.actes.models import ActValidationState, Act
from calebasse.dossiers.models import FileState, PatientRecord, PatientAddress, PatientContact
from calebasse.personnes.models import People, Worker, ExternalWorker, ExternalTherapist, Holiday

def object_save(sender, **kwargs):
    model_name = sender.__name__.lower()
    if kwargs.get('created'):
        tag = 'new-%s' % model_name
        log = '{obj_id} created by {user} from {ip}'
    else:
        tag = '%s-save' % model_name
        log = '{obj_id} saved by {user} from {ip}'

    obj_id = kwargs['instance'].id
    get_request().record(tag, log, obj_id=obj_id)

def object_delete(sender, **kwargs):
    model_name = sender.__name__.lower()
    get_request().record('delete-%s' % model_name,
                         '{obj_id} deleted by {user} from {ip}',
                         obj_id=kwargs['instance'].id)

for model in (Event, EventWithAct, EventType, ActValidationState, Act,
              FileState, PatientRecord, PatientAddress, PatientContact,
              People, Worker, ExternalWorker, ExternalTherapist, Holiday):
    post_save.connect(object_save, sender=model)
    pre_delete.connect(object_delete, sender=model)

