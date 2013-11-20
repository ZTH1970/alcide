# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'FileState.previous_state'
        db.alter_column(u'dossiers_filestate', 'previous_state_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dossiers.FileState'], null=True, on_delete=models.SET_NULL))

        # Changing field 'PatientRecord.size'
        db.alter_column(u'dossiers_patientrecord', 'size', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=1))

        # Changing field 'PatientRecord.last_state'
        db.alter_column(u'dossiers_patientrecord', 'last_state_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['dossiers.FileState']))

        # Changing field 'PatientRecord.policyholder'
        db.alter_column(u'dossiers_patientrecord', 'policyholder_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['dossiers.PatientContact']))

    def backwards(self, orm):

        # Changing field 'FileState.previous_state'
        db.alter_column(u'dossiers_filestate', 'previous_state_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dossiers.FileState'], null=True))

        # Changing field 'PatientRecord.size'
        db.alter_column(u'dossiers_patientrecord', 'size', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'PatientRecord.last_state'
        db.alter_column(u'dossiers_patientrecord', 'last_state_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['dossiers.FileState']))

        # Changing field 'PatientRecord.policyholder'
        db.alter_column(u'dossiers_patientrecord', 'policyholder_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['dossiers.PatientContact']))

    models = {
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
        'dossiers.cmpphealthcarediagnostic': {
            'Meta': {'object_name': 'CmppHealthCareDiagnostic', '_ormbases': ['dossiers.HealthCare']},
            'act_number': ('django.db.models.fields.IntegerField', [], {'default': '6'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'healthcare_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['dossiers.HealthCare']", 'unique': 'True', 'primary_key': 'True'})
        },
        'dossiers.cmpphealthcaretreatment': {
            'Meta': {'object_name': 'CmppHealthCareTreatment', '_ormbases': ['dossiers.HealthCare']},
            'act_number': ('django.db.models.fields.IntegerField', [], {'default': '30'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'healthcare_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['dossiers.HealthCare']", 'unique': 'True', 'primary_key': 'True'}),
            'prolongation': ('django.db.models.fields.IntegerField', [], {'default': '0'})
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
            'street': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'zip_code': ('calebasse.models.ZipCodeField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'})
        },
        u'dossiers.patientcontact': {
            'Meta': {'ordering': "['last_name', 'first_name']", 'object_name': 'PatientContact', '_ormbases': [u'personnes.People']},
            'addresses': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['dossiers.PatientAddress']", 'symmetrical': 'False'}),
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
            'policyholder': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['dossiers.PatientContact']"}),
            'pregnancy_term': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'provenance': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['ressources.Provenance']", 'null': 'True', 'blank': 'True'}),
            'rm_father': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'rm_father'", 'null': 'True', 'blank': 'True', 'to': u"orm['ressources.MaritalStatusType']"}),
            'rm_mother': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'rm_mother'", 'null': 'True', 'blank': 'True', 'to': u"orm['ressources.MaritalStatusType']"}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ressources.Service']", 'null': 'True', 'blank': 'True'}),
            'sibship_place': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'size': ('django.db.models.fields.DecimalField', [], {'default': 'None', 'null': 'True', 'max_digits': '5', 'decimal_places': '1', 'blank': 'True'}),
            'socialisation_durations': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'socialisation_duration_of'", 'symmetrical': 'False', 'to': u"orm['ressources.SocialisationDuration']"}),
            'transportcompany': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['ressources.TransportCompany']", 'null': 'True', 'blank': 'True'}),
            'transporttype': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['ressources.TransportType']", 'null': 'True', 'blank': 'True'}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'})
        },
        'dossiers.sessadhealthcarenotification': {
            'Meta': {'object_name': 'SessadHealthCareNotification', '_ormbases': ['dossiers.HealthCare']},
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'healthcare_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['dossiers.HealthCare']", 'unique': 'True', 'primary_key': 'True'})
        },
        'dossiers.status': {
            'Meta': {'object_name': 'Status'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'services': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['ressources.Service']", 'symmetrical': 'False'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        u'dossiers.transportprescriptionlog': {
            'Meta': {'object_name': 'TransportPrescriptionLog'},
            'choices': ('django.db.models.fields.CharField', [], {'max_length': '4096', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dossiers.PatientRecord']"})
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
        u'ressources.school': {
            'Meta': {'object_name': 'School'},
            'address': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'address_complement': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'director_name': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '70', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'default': 'None', 'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '30', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'old_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_service': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'phone': ('calebasse.models.PhoneNumberField', [], {'default': 'None', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'school_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ressources.SchoolType']"}),
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

    complete_apps = ['dossiers']