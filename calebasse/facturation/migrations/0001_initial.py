# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'Invoicing'
        db.create_table('facturation_invoicing', (
            ('status', self.gf('django.db.models.fields.CharField')(default='open', max_length=20)),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ressources.Service'])),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('seq_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('facturation', ['Invoicing'])

        # Adding unique constraint on 'Invoicing', fields ['seq_id', 'service']
        db.create_unique('facturation_invoicing', ['seq_id', 'service_id'])

        # Adding M2M table for field acts on 'Invoicing'
        db.create_table('facturation_invoicing_acts', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('invoicing', models.ForeignKey(orm['facturation.invoicing'], null=False)),
            ('act', models.ForeignKey(orm['actes.act'], null=False))
        ))
        db.create_unique('facturation_invoicing_acts', ['invoicing_id', 'act_id'])

        # Adding model 'Invoice'
        db.create_table('facturation_invoice', (
            ('ppa', self.gf('django.db.models.fields.IntegerField')()),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dossiers.PatientRecord'])),
            ('invoicing', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['facturation.Invoicing'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('number', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('amount', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('facturation', ['Invoice'])

        # Adding M2M table for field acts on 'Invoice'
        db.create_table('facturation_invoice_acts', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('invoice', models.ForeignKey(orm['facturation.invoice'], null=False)),
            ('act', models.ForeignKey(orm['actes.act'], null=False))
        ))
        db.create_unique('facturation_invoice_acts', ['invoice_id', 'act_id'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'Invoicing'
        db.delete_table('facturation_invoicing')

        # Removing unique constraint on 'Invoicing', fields ['seq_id', 'service']
        db.delete_unique('facturation_invoicing', ['seq_id', 'service_id'])

        # Removing M2M table for field acts on 'Invoicing'
        db.delete_table('facturation_invoicing_acts')

        # Deleting model 'Invoice'
        db.delete_table('facturation_invoice')

        # Removing M2M table for field acts on 'Invoice'
        db.delete_table('facturation_invoice_acts')
    
    
    models = {
        'actes.act': {
            'Meta': {'object_name': 'Act'},
            '_duration': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'act_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ressources.ActType']"}),
            'attendance': ('django.db.models.fields.CharField', [], {'default': "'absent'", 'max_length': '16'}),
            'comment': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'doctors': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['personnes.Worker']", 'symmetrical': 'False'}),
            'healthcare': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dossiers.HealthCare']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_billed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True', 'blank': 'True'}),
            'is_lost': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True', 'blank': 'True'}),
            'old_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'parent_event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['agenda.Event']", 'null': 'True', 'blank': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dossiers.PatientRecord']"}),
            'pause': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True', 'blank': 'True'}),
            'switch_billable': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'time': ('django.db.models.fields.TimeField', [], {'default': 'datetime.time(0, 0)', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'transport_company': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ressources.TransportCompany']", 'null': 'True', 'blank': 'True'}),
            'transport_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ressources.TransportType']", 'null': 'True', 'blank': 'True'}),
            'validation_locked': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True', 'blank': 'True'}),
            'valide': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True', 'blank': 'True'})
        },
        'agenda.event': {
            'Meta': {'unique_together': "(('exception_to', 'exception_date'),)", 'object_name': 'Event'},
            'canceled': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True', 'blank': 'True'}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'end_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'event_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['agenda.EventType']"}),
            'exception_date': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'exception_to': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'exceptions'", 'null': 'True', 'to': "orm['agenda.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'old_ev_id': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'old_rr_id': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'old_rs_id': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'participants': ('django.db.models.fields.related.ManyToManyField', [], {'default': 'None', 'to': "orm['personnes.People']", 'null': 'True', 'symmetrical': 'False', 'blank': 'True'}),
            'recurrence_end_date': ('django.db.models.fields.DateField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'recurrence_periodicity': ('django.db.models.fields.PositiveIntegerField', [], {'default': 'None', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'recurrence_week_day': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'recurrence_week_offset': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'recurrence_week_parity': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'recurrence_week_period': ('django.db.models.fields.PositiveIntegerField', [], {'default': 'None', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'recurrence_week_rank': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'room': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ressources.Room']", 'null': 'True', 'blank': 'True'}),
            'services': ('django.db.models.fields.related.ManyToManyField', [], {'default': 'None', 'to': "orm['ressources.Service']", 'null': 'True', 'symmetrical': 'False', 'blank': 'True'}),
            'start_datetime': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'})
        },
        'agenda.eventtype': {
            'Meta': {'object_name': 'EventType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'rank': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 2, 12, 14, 58, 59, 391945)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 2, 12, 14, 58, 59, 391791)'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'dossiers.filestate': {
            'Meta': {'object_name': 'FileState'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'comment': ('django.db.models.fields.TextField', [], {'max_length': '3000', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_selected': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dossiers.PatientRecord']"}),
            'previous_state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dossiers.FileState']", 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dossiers.Status']"})
        },
        'dossiers.healthcare': {
            'Meta': {'object_name': 'HealthCare'},
            'agree_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'max_length': '3000', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'insist_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dossiers.PatientRecord']"}),
            'request_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {})
        },
        'dossiers.patientaddress': {
            'Meta': {'object_name': 'PatientAddress'},
            'address_complement': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '276'}),
            'fax': ('calebasse.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'}),
            'phone': ('calebasse.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'place_of_life': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'zip_code': ('calebasse.models.ZipCodeField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'})
        },
        'dossiers.patientcontact': {
            'Meta': {'object_name': 'PatientContact', '_ormbases': ['personnes.People']},
            'addresses': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['dossiers.PatientAddress']", 'symmetrical': 'False'}),
            'begin_rights': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'birthdate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'birthplace': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'contact_comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'end_rights': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'health_center': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ressources.HealthCenter']", 'null': 'True', 'blank': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'job'", 'null': 'True', 'blank': 'True', 'to': "orm['ressources.Job']"}),
            'mobile': ('calebasse.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'old_contact_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'other_health_center': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'parente': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['ressources.PatientRelatedLink']", 'null': 'True', 'blank': 'True'}),
            'people_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['personnes.People']", 'unique': 'True', 'primary_key': 'True'}),
            'social_security_id': ('django.db.models.fields.CharField', [], {'max_length': '13', 'null': 'True', 'blank': 'True'}),
            'thirdparty_payer': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'twinning_rank': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'dossiers.patientrecord': {
            'Meta': {'object_name': 'PatientRecord', '_ormbases': ['dossiers.PatientContact']},
            'advicegiver': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['ressources.AdviceGiver']", 'null': 'True', 'blank': 'True'}),
            'analysemotive': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['ressources.AnalyseMotive']", 'null': 'True', 'blank': 'True'}),
            'apgar_score_one': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'apgar_score_two': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'chest_perimeter': ('django.db.models.fields.DecimalField', [], {'default': 'None', 'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'child_custody': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['ressources.ParentalCustodyType']", 'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'confidential': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'contacts': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'contact_of'", 'symmetrical': 'False', 'to': "orm['dossiers.PatientContact']"}),
            'coordinators': ('django.db.models.fields.related.ManyToManyField', [], {'default': 'None', 'to': "orm['personnes.Worker']", 'null': 'True', 'symmetrical': 'False', 'blank': 'True'}),
            'cranium_perimeter': ('django.db.models.fields.DecimalField', [], {'default': 'None', 'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'externaldoctor': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['personnes.ExternalTherapist']", 'null': 'True', 'blank': 'True'}),
            'externalintervener': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['personnes.ExternalWorker']", 'null': 'True', 'blank': 'True'}),
            'family_comment': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'family_situation': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['ressources.FamilySituationType']", 'null': 'True', 'blank': 'True'}),
            'familymotive': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['ressources.FamilyMotive']", 'null': 'True', 'blank': 'True'}),
            'job_father': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'job_father'", 'null': 'True', 'blank': 'True', 'to': "orm['ressources.Job']"}),
            'job_mother': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'job_mother'", 'null': 'True', 'blank': 'True', 'to': "orm['ressources.Job']"}),
            'last_state': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['dossiers.FileState']"}),
            'mdph_requests': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'mdph_requests_of'", 'symmetrical': 'False', 'to': "orm['ressources.MDPHRequest']"}),
            'mdph_responses': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'mdph_responses_of'", 'symmetrical': 'False', 'to': "orm['ressources.MDPHResponse']"}),
            'mises_1': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'mises1'", 'default': 'None', 'to': "orm['ressources.CodeCFTMEA']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'mises_2': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'mises2'", 'default': 'None', 'to': "orm['ressources.CodeCFTMEA']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'mises_3': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'mises3'", 'default': 'None', 'to': "orm['ressources.CodeCFTMEA']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'nationality': ('django.db.models.fields.CharField', [], {'max_length': '70', 'null': 'True', 'blank': 'True'}),
            'nb_children_family': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'old_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_old_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'outmotive': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['ressources.OutMotive']", 'null': 'True', 'blank': 'True'}),
            'outto': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['ressources.OutTo']", 'null': 'True', 'blank': 'True'}),
            'paper_id': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'parental_authority': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['ressources.ParentalAuthorityType']", 'null': 'True', 'blank': 'True'}),
            'patientcontact_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['dossiers.PatientContact']", 'unique': 'True', 'primary_key': 'True'}),
            'pause': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'policyholder': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['dossiers.PatientContact']"}),
            'pregnancy_term': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'provenance': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['ressources.Provenance']", 'null': 'True', 'blank': 'True'}),
            'rm_father': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'rm_father'", 'null': 'True', 'blank': 'True', 'to': "orm['ressources.MaritalStatusType']"}),
            'rm_mother': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'rm_mother'", 'null': 'True', 'blank': 'True', 'to': "orm['ressources.MaritalStatusType']"}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ressources.Service']", 'null': 'True', 'blank': 'True'}),
            'sibship_place': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'size': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'socialisation_durations': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'socialisation_duration_of'", 'symmetrical': 'False', 'to': "orm['ressources.SocialisationDuration']"}),
            'transportcompany': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['ressources.TransportCompany']", 'null': 'True', 'blank': 'True'}),
            'transporttype': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['ressources.TransportType']", 'null': 'True', 'blank': 'True'}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'})
        },
        'dossiers.status': {
            'Meta': {'object_name': 'Status'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'services': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ressources.Service']", 'symmetrical': 'False'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        'facturation.invoice': {
            'Meta': {'object_name': 'Invoice'},
            'acts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['actes.Act']", 'symmetrical': 'False'}),
            'amount': ('django.db.models.fields.IntegerField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoicing': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['facturation.Invoicing']"}),
            'number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dossiers.PatientRecord']"}),
            'ppa': ('django.db.models.fields.IntegerField', [], {})
        },
        'facturation.invoicing': {
            'Meta': {'unique_together': "(('seq_id', 'service'),)", 'object_name': 'Invoicing'},
            'acts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['actes.Act']", 'symmetrical': 'False'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'seq_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ressources.Service']"}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'open'", 'max_length': '20'})
        },
        'personnes.externaltherapist': {
            'Meta': {'object_name': 'ExternalTherapist', '_ormbases': ['personnes.People']},
            'address': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'address_complement': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'old_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_service': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'people_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['personnes.People']", 'unique': 'True', 'primary_key': 'True'}),
            'phone_work': ('calebasse.models.PhoneNumberField', [], {'default': 'None', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'default': '18', 'to': "orm['ressources.WorkerType']"}),
            'zip_code': ('calebasse.models.ZipCodeField', [], {'default': 'None', 'max_length': '5', 'null': 'True', 'blank': 'True'})
        },
        'personnes.externalworker': {
            'Meta': {'object_name': 'ExternalWorker', '_ormbases': ['personnes.People']},
            'address': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'address_complement': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'old_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_service': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'people_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['personnes.People']", 'unique': 'True', 'primary_key': 'True'}),
            'phone_work': ('calebasse.models.PhoneNumberField', [], {'default': 'None', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'default': '18', 'to': "orm['ressources.WorkerType']"}),
            'zip_code': ('calebasse.models.ZipCodeField', [], {'default': 'None', 'max_length': '5', 'null': 'True', 'blank': 'True'})
        },
        'personnes.people': {
            'Meta': {'object_name': 'People'},
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'db_index': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.IntegerField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'phone': ('calebasse.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        'personnes.worker': {
            'Meta': {'object_name': 'Worker', '_ormbases': ['personnes.People']},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'old_camsp_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_cmpp_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_sessad_dys_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_sessad_ted_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'people_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['personnes.People']", 'unique': 'True', 'primary_key': 'True'}),
            'services': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['ressources.Service']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ressources.WorkerType']"})
        },
        'ressources.acttype': {
            'Meta': {'object_name': 'ActType'},
            'billable': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'display_first': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'old_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ressources.Service']", 'null': 'True', 'blank': 'True'})
        },
        'ressources.advicegiver': {
            'Meta': {'object_name': 'AdviceGiver'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'ressources.analysemotive': {
            'Meta': {'object_name': 'AnalyseMotive'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'ressources.codecftmea': {
            'Meta': {'object_name': 'CodeCFTMEA'},
            'axe': ('django.db.models.fields.IntegerField', [], {'max_length': '1'}),
            'code': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'ressources.familymotive': {
            'Meta': {'object_name': 'FamilyMotive'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'ressources.familysituationtype': {
            'Meta': {'object_name': 'FamilySituationType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'ressources.healthcenter': {
            'Meta': {'object_name': 'HealthCenter'},
            'abbreviation': ('django.db.models.fields.CharField', [], {'default': 'True', 'max_length': '8', 'null': 'True'}),
            'accounting_number': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'address': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'address_complement': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'computer_center_code': ('django.db.models.fields.CharField', [], {'default': 'True', 'max_length': '8', 'null': 'True'}),
            'correspondant': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'dest_organism': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'health_fund': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'large_regime': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ressources.LargeRegime']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '8'})
        },
        'ressources.job': {
            'Meta': {'object_name': 'Job'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'ressources.largeregime': {
            'Meta': {'object_name': 'LargeRegime'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'ressources.maritalstatustype': {
            'Meta': {'object_name': 'MaritalStatusType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'ressources.mdph': {
            'Meta': {'object_name': 'MDPH'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'address_complement': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'department': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'fax': ('calebasse.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone': ('calebasse.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'zip_code': ('calebasse.models.ZipCodeField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'})
        },
        'ressources.mdphrequest': {
            'Meta': {'object_name': 'MDPHRequest'},
            'comment': ('django.db.models.fields.TextField', [], {'max_length': '3000', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mdph': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ressources.MDPH']"}),
            'start_date': ('django.db.models.fields.DateField', [], {})
        },
        'ressources.mdphresponse': {
            'Meta': {'object_name': 'MDPHResponse'},
            'comment': ('django.db.models.fields.TextField', [], {'max_length': '3000', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mdph': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ressources.MDPH']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'rate': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'type_aide': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1'})
        },
        'ressources.office': {
            'Meta': {'object_name': 'Office'},
            'address': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'address_complement': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'fax': ('calebasse.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'phone': ('calebasse.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'zip_code': ('calebasse.models.ZipCodeField', [], {'default': 'None', 'max_length': '5', 'null': 'True', 'blank': 'True'})
        },
        'ressources.outmotive': {
            'Meta': {'object_name': 'OutMotive'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'ressources.outto': {
            'Meta': {'object_name': 'OutTo'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'ressources.parentalauthoritytype': {
            'Meta': {'object_name': 'ParentalAuthorityType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'ressources.parentalcustodytype': {
            'Meta': {'object_name': 'ParentalCustodyType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'ressources.patientrelatedlink': {
            'Meta': {'object_name': 'PatientRelatedLink'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'old_camsp_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_cmpp_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_sessad_dys_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_sessad_ted_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'})
        },
        'ressources.provenance': {
            'Meta': {'object_name': 'Provenance'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'old_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_service': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'})
        },
        'ressources.room': {
            'Meta': {'object_name': 'Room'},
            'etablissement': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ressources.Office']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'ressources.school': {
            'Meta': {'object_name': 'School'},
            'address': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'address_complement': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'director_name': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '70', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'default': 'None', 'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'old_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_service': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'phone': ('calebasse.models.PhoneNumberField', [], {'default': 'None', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'school_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ressources.SchoolType']"}),
            'zip_code': ('calebasse.models.ZipCodeField', [], {'default': 'None', 'max_length': '5', 'null': 'True', 'blank': 'True'})
        },
        'ressources.schoollevel': {
            'Meta': {'object_name': 'SchoolLevel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'old_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_service': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'})
        },
        'ressources.schooltype': {
            'Meta': {'object_name': 'SchoolType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'services': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ressources.Service']", 'symmetrical': 'False'})
        },
        'ressources.service': {
            'Meta': {'object_name': 'Service'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'fax': ('calebasse.models.PhoneNumberField', [], {'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'phone': ('calebasse.models.PhoneNumberField', [], {'max_length': '20'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'ressources.socialisationduration': {
            'Meta': {'object_name': 'SocialisationDuration'},
            'comment': ('django.db.models.fields.TextField', [], {'max_length': '3000', 'null': 'True', 'blank': 'True'}),
            'contact': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ressources.SchoolLevel']", 'null': 'True', 'blank': 'True'}),
            'redoublement': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ressources.School']", 'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {})
        },
        'ressources.transportcompany': {
            'Meta': {'object_name': 'TransportCompany'},
            'address': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'address_complement': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'correspondant': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'old_camsp_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_cmpp_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_sessad_dys_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_sessad_ted_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'phone': ('calebasse.models.PhoneNumberField', [], {'default': 'None', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'zip_code': ('calebasse.models.ZipCodeField', [], {'default': 'None', 'max_length': '5', 'null': 'True', 'blank': 'True'})
        },
        'ressources.transporttype': {
            'Meta': {'object_name': 'TransportType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'ressources.workertype': {
            'Meta': {'object_name': 'WorkerType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intervene': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        }
    }
    
    complete_apps = ['facturation']
