# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        for a in orm.Act.objects.filter(comment__isnull=False):
            if a.comment != "" and a.parent_event and not a.parent_event.recurrence_periodicity \
                    and (not a.parent_event.description or a.parent_event.description == ""):
                a.parent_event.description = a.comment
                a.parent_event.save()

    def backwards(self, orm):
        pass

    models = {
        u'actes.act': {
            'Meta': {'ordering': "['-date', 'patient']", 'object_name': 'Act'},
            '_duration': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'act_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ressources.ActType']"}),
            'attendance': ('django.db.models.fields.CharField', [], {'default': "'absent'", 'max_length': '16'}),
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'doctors': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['personnes.Worker']", 'symmetrical': 'False'}),
            'healthcare': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dossiers.HealthCare']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_billed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'is_lost': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'last_validation_state': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'+'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['actes.ActValidationState']"}),
            'old_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'parent_event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['agenda.Event']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dossiers.PatientRecord']"}),
            'pause': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'switch_billable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'time': ('django.db.models.fields.TimeField', [], {'default': 'datetime.time(0, 0)', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'transport_company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ressources.TransportCompany']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'transport_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ressources.TransportType']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'validation_locked': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'valide': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'})
        },
        'actes.actvalidationstate': {
            'Meta': {'ordering': "('-created',)", 'object_name': 'ActValidationState'},
            'act': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['actes.Act']"}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'auto': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'previous_state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['actes.ActValidationState']", 'null': 'True', 'blank': 'True'}),
            'state_name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'actes.validationmessage': {
            'Meta': {'object_name': 'ValidationMessage'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ressources.Service']", 'null': 'True', 'blank': 'True'}),
            'validation_date': ('django.db.models.fields.DateTimeField', [], {}),
            'what': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'who': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'agenda.event': {
            'Meta': {'ordering': "('start_datetime', 'end_datetime', 'title')", 'unique_together': "(('exception_to', 'exception_date'),)", 'object_name': 'Event'},
            'canceled': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'end_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'event_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['agenda.EventType']"}),
            'exception_date': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'exception_to': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'exceptions'", 'null': 'True', 'to': u"orm['agenda.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'old_ev_id': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'old_rr_id': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'old_rs_id': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'participants': ('django.db.models.fields.related.ManyToManyField', [], {'default': 'None', 'to': u"orm['personnes.People']", 'null': 'True', 'symmetrical': 'False', 'blank': 'True'}),
            'recurrence_end_date': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'recurrence_periodicity': ('django.db.models.fields.PositiveIntegerField', [], {'default': 'None', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'recurrence_week_day': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'recurrence_week_offset': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'recurrence_week_parity': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'recurrence_week_period': ('django.db.models.fields.PositiveIntegerField', [], {'default': 'None', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'recurrence_week_rank': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'ressource': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ressources.Ressource']", 'null': 'True', 'blank': 'True'}),
            'services': ('django.db.models.fields.related.ManyToManyField', [], {'default': 'None', 'to': u"orm['ressources.Service']", 'null': 'True', 'symmetrical': 'False', 'blank': 'True'}),
            'start_datetime': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '60', 'blank': 'True'})
        },
        u'agenda.eventtype': {
            'Meta': {'object_name': 'EventType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'rank': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'dossiers.filestate': {
            'Meta': {'object_name': 'FileState'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'comment': ('django.db.models.fields.TextField', [], {'max_length': '3000', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_selected': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dossiers.PatientRecord']"}),
            'previous_state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dossiers.FileState']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dossiers.Status']"})
        },
        'dossiers.healthcare': {
            'Meta': {'object_name': 'HealthCare'},
            'agree_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'max_length': '3000', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'insist_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dossiers.PatientRecord']"}),
            'request_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {})
        },
        u'dossiers.patientaddress': {
            'Meta': {'object_name': 'PatientAddress'},
            'address_complement': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '276'}),
            'fax': ('calebasse.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'}),
            'phone': ('calebasse.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'place_of_life': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'recipient': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'zip_code': ('calebasse.models.ZipCodeField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'})
        },
        u'dossiers.patientcontact': {
            'Meta': {'ordering': "['last_name', 'first_name']", 'object_name': 'PatientContact', '_ormbases': [u'personnes.People']},
            'addresses': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['dossiers.PatientAddress']", 'symmetrical': 'False'}),
            'ame': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'begin_rights': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'birthdate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'birthplace': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'contact_comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'end_rights': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'health_center': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ressources.HealthCenter']", 'null': 'True', 'blank': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'job'", 'null': 'True', 'blank': 'True', 'to': u"orm['ressources.Job']"}),
            'management_code': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ressources.ManagementCode']", 'null': 'True', 'blank': 'True'}),
            'mobile': ('calebasse.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'old_contact_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'other_health_center': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'parente': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['ressources.PatientRelatedLink']", 'null': 'True', 'blank': 'True'}),
            u'people_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['personnes.People']", 'unique': 'True', 'primary_key': 'True'}),
            'social_security_id': ('django.db.models.fields.CharField', [], {'max_length': '13', 'null': 'True', 'blank': 'True'}),
            'thirdparty_payer': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'twinning_rank': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'type_of_contract': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'})
        },
        u'dossiers.patientrecord': {
            'Meta': {'object_name': 'PatientRecord', '_ormbases': [u'dossiers.PatientContact']},
            'advicegiver': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['ressources.AdviceGiver']", 'null': 'True', 'blank': 'True'}),
            'analysemotive': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['ressources.AnalyseMotive']", 'null': 'True', 'blank': 'True'}),
            'apgar_score_one': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'apgar_score_two': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'chest_perimeter': ('django.db.models.fields.DecimalField', [], {'default': 'None', 'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'child_custody': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['ressources.ParentalCustodyType']", 'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'confidential': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'contacts': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'contact_of'", 'symmetrical': 'False', 'to': u"orm['dossiers.PatientContact']"}),
            'coordinators': ('django.db.models.fields.related.ManyToManyField', [], {'default': 'None', 'to': u"orm['personnes.Worker']", 'null': 'True', 'symmetrical': 'False', 'blank': 'True'}),
            'cranium_perimeter': ('django.db.models.fields.DecimalField', [], {'default': 'None', 'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'deficiency_auditory': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            'deficiency_autism_and_other_ted': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            'deficiency_behavioral_disorder': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            'deficiency_brain_damage': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            'deficiency_in_diagnostic': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'deficiency_intellectual': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            'deficiency_learning_disorder': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            'deficiency_mental_disorder': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            'deficiency_metabolic_disorder': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            'deficiency_motor': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            'deficiency_other_disorder': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            'deficiency_polyhandicap': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'deficiency_visual': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'}),
            'externaldoctor': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['personnes.ExternalTherapist']", 'null': 'True', 'blank': 'True'}),
            'externalintervener': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['personnes.ExternalWorker']", 'null': 'True', 'blank': 'True'}),
            'family_comment': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'family_situation': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['ressources.FamilySituationType']", 'null': 'True', 'blank': 'True'}),
            'familymotive': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['ressources.FamilyMotive']", 'null': 'True', 'blank': 'True'}),
            'job_father': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'job_father'", 'null': 'True', 'blank': 'True', 'to': u"orm['ressources.Job']"}),
            'job_mother': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'job_mother'", 'null': 'True', 'blank': 'True', 'to': u"orm['ressources.Job']"}),
            'last_state': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['dossiers.FileState']"}),
            'mdph_requests': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'mdph_requests_of'", 'symmetrical': 'False', 'to': u"orm['ressources.MDPHRequest']"}),
            'mdph_responses': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'mdph_responses_of'", 'symmetrical': 'False', 'to': u"orm['ressources.MDPHResponse']"}),
            'mises_1': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'mises1'", 'default': 'None', 'to': u"orm['ressources.CodeCFTMEA']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'mises_2': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'mises2'", 'default': 'None', 'to': u"orm['ressources.CodeCFTMEA']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'mises_3': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'mises3'", 'default': 'None', 'to': u"orm['ressources.CodeCFTMEA']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'nationality': ('django.db.models.fields.CharField', [], {'max_length': '70', 'null': 'True', 'blank': 'True'}),
            'nb_children_family': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'old_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_old_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'outmotive': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['ressources.OutMotive']", 'null': 'True', 'blank': 'True'}),
            'outto': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['ressources.OutTo']", 'null': 'True', 'blank': 'True'}),
            'paper_id': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'parental_authority': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['ressources.ParentalAuthorityType']", 'null': 'True', 'blank': 'True'}),
            u'patientcontact_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['dossiers.PatientContact']", 'unique': 'True', 'primary_key': 'True'}),
            'pause': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pause_comment': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'periodic_appointment_transport': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'policyholder': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['dossiers.PatientContact']"}),
            'pregnancy_term': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'provenance': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['ressources.Provenance']", 'null': 'True', 'blank': 'True'}),
            'provenanceplace': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['ressources.ProvenancePlace']", 'null': 'True', 'blank': 'True'}),
            'rm_father': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'rm_father'", 'null': 'True', 'blank': 'True', 'to': u"orm['ressources.MaritalStatusType']"}),
            'rm_mother': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'rm_mother'", 'null': 'True', 'blank': 'True', 'to': u"orm['ressources.MaritalStatusType']"}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ressources.Service']", 'null': 'True', 'blank': 'True'}),
            'sibship_place': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'simple_appointment_transport': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'size': ('django.db.models.fields.DecimalField', [], {'default': 'None', 'null': 'True', 'max_digits': '5', 'decimal_places': '1', 'blank': 'True'}),
            'socialisation_durations': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'socialisation_duration_of'", 'symmetrical': 'False', 'to': u"orm['ressources.SocialisationDuration']"}),
            'transportcompany': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['ressources.TransportCompany']", 'null': 'True', 'blank': 'True'}),
            'transporttype': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['ressources.TransportType']", 'null': 'True', 'blank': 'True'}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'})
        },
        'dossiers.status': {
            'Meta': {'object_name': 'Status'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'services': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['ressources.Service']", 'symmetrical': 'False'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        u'personnes.externaltherapist': {
            'Meta': {'ordering': "['last_name', 'first_name']", 'object_name': 'ExternalTherapist', '_ormbases': [u'personnes.People']},
            'address': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'address_complement': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'old_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_service': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            u'people_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['personnes.People']", 'unique': 'True', 'primary_key': 'True'}),
            'phone_work': ('calebasse.models.PhoneNumberField', [], {'default': 'None', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'default': '18', 'to': u"orm['ressources.WorkerType']"}),
            'zip_code': ('calebasse.models.ZipCodeField', [], {'default': 'None', 'max_length': '5', 'null': 'True', 'blank': 'True'})
        },
        u'personnes.externalworker': {
            'Meta': {'ordering': "['last_name', 'first_name']", 'object_name': 'ExternalWorker', '_ormbases': [u'personnes.People']},
            'address': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'address_complement': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'old_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_service': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            u'people_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['personnes.People']", 'unique': 'True', 'primary_key': 'True'}),
            'phone_work': ('calebasse.models.PhoneNumberField', [], {'default': 'None', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'default': '18', 'to': u"orm['ressources.WorkerType']"}),
            'zip_code': ('calebasse.models.ZipCodeField', [], {'default': 'None', 'max_length': '5', 'null': 'True', 'blank': 'True'})
        },
        u'personnes.people': {
            'Meta': {'ordering': "['last_name', 'first_name']", 'object_name': 'People'},
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'db_index': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.IntegerField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'phone': ('calebasse.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'personnes.worker': {
            'Meta': {'ordering': "['last_name', 'first_name']", 'object_name': 'Worker', '_ormbases': [u'personnes.People']},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'initials': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '5', 'blank': 'True'}),
            'old_camsp_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_cmpp_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_sessad_dys_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_sessad_ted_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            u'people_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['personnes.People']", 'unique': 'True', 'primary_key': 'True'}),
            'services': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['ressources.Service']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ressources.WorkerType']"})
        },
        u'ressources.acttype': {
            'Meta': {'ordering': "('-display_first', 'name')", 'object_name': 'ActType'},
            'billable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'display_first': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'group': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'old_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ressources.Service']", 'null': 'True', 'blank': 'True'})
        },
        u'ressources.advicegiver': {
            'Meta': {'object_name': 'AdviceGiver'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'ressources.analysemotive': {
            'Meta': {'object_name': 'AnalyseMotive'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'ressources.codecftmea': {
            'Meta': {'ordering': "['ordering_code']", 'object_name': 'CodeCFTMEA'},
            'axe': ('django.db.models.fields.IntegerField', [], {'max_length': '1'}),
            'code': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'ordering_code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'ressources.familymotive': {
            'Meta': {'object_name': 'FamilyMotive'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'ressources.familysituationtype': {
            'Meta': {'object_name': 'FamilySituationType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'ressources.healthcenter': {
            'Meta': {'object_name': 'HealthCenter'},
            'abbreviation': ('django.db.models.fields.CharField', [], {'default': 'True', 'max_length': '8', 'null': 'True'}),
            'accounting_number': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'address': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'address_complement': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'computer_center_code': ('django.db.models.fields.CharField', [], {'default': 'True', 'max_length': '8', 'null': 'True'}),
            'correspondant': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'dest_organism': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'hc_invoice': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['ressources.HealthCenter']", 'null': 'True', 'blank': 'True'}),
            'health_fund': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'large_regime': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ressources.LargeRegime']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '8'})
        },
        u'ressources.job': {
            'Meta': {'object_name': 'Job'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'ressources.largeregime': {
            'Meta': {'object_name': 'LargeRegime'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'ressources.managementcode': {
            'Meta': {'object_name': 'ManagementCode'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'old_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'})
        },
        u'ressources.maritalstatustype': {
            'Meta': {'object_name': 'MaritalStatusType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'ressources.mdph': {
            'Meta': {'object_name': 'MDPH'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'address_complement': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'department': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'fax': ('calebasse.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone': ('calebasse.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'zip_code': ('calebasse.models.ZipCodeField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'})
        },
        u'ressources.mdphrequest': {
            'Meta': {'object_name': 'MDPHRequest'},
            'comment': ('django.db.models.fields.TextField', [], {'max_length': '3000', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mdph': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ressources.MDPH']"}),
            'start_date': ('django.db.models.fields.DateField', [], {})
        },
        u'ressources.mdphresponse': {
            'Meta': {'object_name': 'MDPHResponse'},
            'comment': ('django.db.models.fields.TextField', [], {'max_length': '3000', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mdph': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ressources.MDPH']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'rate': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'type_aide': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'})
        },
        u'ressources.office': {
            'Meta': {'object_name': 'Office'},
            'address': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'address_complement': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'fax': ('calebasse.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'phone': ('calebasse.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'zip_code': ('calebasse.models.ZipCodeField', [], {'default': 'None', 'max_length': '5', 'null': 'True', 'blank': 'True'})
        },
        u'ressources.outmotive': {
            'Meta': {'object_name': 'OutMotive'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'ressources.outto': {
            'Meta': {'object_name': 'OutTo'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'ressources.parentalauthoritytype': {
            'Meta': {'object_name': 'ParentalAuthorityType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'ressources.parentalcustodytype': {
            'Meta': {'object_name': 'ParentalCustodyType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'ressources.patientrelatedlink': {
            'Meta': {'object_name': 'PatientRelatedLink'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'old_camsp_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_cmpp_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_sessad_dys_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_sessad_ted_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'})
        },
        u'ressources.provenance': {
            'Meta': {'object_name': 'Provenance'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'old_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_service': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'})
        },
        u'ressources.provenanceplace': {
            'Meta': {'object_name': 'ProvenancePlace'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'ressources.ressource': {
            'Meta': {'object_name': 'Ressource'},
            'etablissement': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ressources.Office']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'ressources.school': {
            'Meta': {'object_name': 'School'},
            'address': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'address_complement': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'director_name': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '70', 'null': 'True', 'blank': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'default': 'None', 'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '30', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'old_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_service': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'phone': ('calebasse.models.PhoneNumberField', [], {'default': 'None', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'private': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'school_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ressources.SchoolType']"}),
            'services': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['ressources.Service']", 'null': 'True', 'blank': 'True'}),
            'zip_code': ('calebasse.models.ZipCodeField', [], {'default': 'None', 'max_length': '5', 'null': 'True', 'blank': 'True'})
        },
        u'ressources.schoollevel': {
            'Meta': {'object_name': 'SchoolLevel'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'old_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_service': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'})
        },
        u'ressources.schooltype': {
            'Meta': {'object_name': 'SchoolType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'services': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['ressources.Service']", 'symmetrical': 'False'})
        },
        u'ressources.service': {
            'Meta': {'object_name': 'Service'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'fax': ('calebasse.models.PhoneNumberField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'phone': ('calebasse.models.PhoneNumberField', [], {'max_length': '20'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        u'ressources.socialisationduration': {
            'Meta': {'object_name': 'SocialisationDuration'},
            'comment': ('django.db.models.fields.TextField', [], {'max_length': '3000', 'null': 'True', 'blank': 'True'}),
            'contact': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ressources.SchoolLevel']", 'null': 'True', 'blank': 'True'}),
            'redoublement': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ressources.School']", 'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {})
        },
        u'ressources.transportcompany': {
            'Meta': {'object_name': 'TransportCompany'},
            'address': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'address_complement': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'correspondant': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '30', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'old_camsp_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_cmpp_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_sessad_dys_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_sessad_ted_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'phone': ('calebasse.models.PhoneNumberField', [], {'default': 'None', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'zip_code': ('calebasse.models.ZipCodeField', [], {'default': 'None', 'max_length': '5', 'null': 'True', 'blank': 'True'})
        },
        u'ressources.transporttype': {
            'Meta': {'object_name': 'TransportType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'ressources.workertype': {
            'Meta': {'object_name': 'WorkerType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intervene': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        }
    }

    complete_apps = ['actes']
    symmetrical = True
