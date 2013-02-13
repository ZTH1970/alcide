# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'HealthCare'
        db.create_table('dossiers_healthcare', (
            ('comment', self.gf('django.db.models.fields.TextField')(max_length=3000, null=True, blank=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dossiers.PatientRecord'])),
            ('request_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('insist_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('agree_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('dossiers', ['HealthCare'])

        # Adding model 'CmppHealthCareDiagnostic'
        db.create_table('dossiers_cmpphealthcarediagnostic', (
            ('healthcare_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['dossiers.HealthCare'], unique=True, primary_key=True)),
            ('act_number', self.gf('django.db.models.fields.IntegerField')(default=6)),
        ))
        db.send_create_signal('dossiers', ['CmppHealthCareDiagnostic'])

        # Adding model 'CmppHealthCareTreatment'
        db.create_table('dossiers_cmpphealthcaretreatment', (
            ('healthcare_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['dossiers.HealthCare'], unique=True, primary_key=True)),
            ('prolongation', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('end_date', self.gf('django.db.models.fields.DateField')()),
            ('act_number', self.gf('django.db.models.fields.IntegerField')(default=30)),
        ))
        db.send_create_signal('dossiers', ['CmppHealthCareTreatment'])

        # Adding model 'SessadHealthCareNotification'
        db.create_table('dossiers_sessadhealthcarenotification', (
            ('healthcare_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['dossiers.HealthCare'], unique=True, primary_key=True)),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal('dossiers', ['SessadHealthCareNotification'])

        # Adding model 'Status'
        db.create_table('dossiers_status', (
            ('type', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('dossiers', ['Status'])

        # Adding M2M table for field services on 'Status'
        db.create_table('dossiers_status_services', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('status', models.ForeignKey(orm['dossiers.status'], null=False)),
            ('service', models.ForeignKey(orm['ressources.service'], null=False))
        ))
        db.create_unique('dossiers_status_services', ['status_id', 'service_id'])

        # Adding model 'FileState'
        db.create_table('dossiers_filestate', (
            ('status', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dossiers.Status'])),
            ('comment', self.gf('django.db.models.fields.TextField')(max_length=3000, null=True, blank=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dossiers.PatientRecord'])),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_selected', self.gf('django.db.models.fields.DateTimeField')()),
            ('previous_state', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dossiers.FileState'], null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('dossiers', ['FileState'])

        # Adding model 'PatientAddress'
        db.create_table('dossiers_patientaddress', (
            ('comment', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
            ('fax', self.gf('calebasse.models.PhoneNumberField')(max_length=20, null=True, blank=True)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=276)),
            ('address_complement', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=12, null=True, blank=True)),
            ('phone', self.gf('calebasse.models.PhoneNumberField')(max_length=20, null=True, blank=True)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('place_of_life', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('zip_code', self.gf('calebasse.models.ZipCodeField')(max_length=5, null=True, blank=True)),
        ))
        db.send_create_signal('dossiers', ['PatientAddress'])

        # Adding model 'PatientContact'
        db.create_table('dossiers_patientcontact', (
            ('birthplace', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('old_contact_id', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('thirdparty_payer', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('mobile', self.gf('calebasse.models.PhoneNumberField')(max_length=20, null=True, blank=True)),
            ('health_center', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ressources.HealthCenter'], null=True, blank=True)),
            ('social_security_id', self.gf('django.db.models.fields.CharField')(max_length=13, null=True, blank=True)),
            ('parente', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['ressources.PatientRelatedLink'], null=True, blank=True)),
            ('birthdate', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('people_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['personnes.People'], unique=True, primary_key=True)),
            ('contact_comment', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('job', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='job', null=True, blank=True, to=orm['ressources.Job'])),
            ('twinning_rank', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('other_health_center', self.gf('django.db.models.fields.CharField')(max_length=4, null=True, blank=True)),
            ('begin_rights', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('end_rights', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal('dossiers', ['PatientContact'])

        # Adding M2M table for field addresses on 'PatientContact'
        db.create_table('dossiers_patientcontact_addresses', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('patientcontact', models.ForeignKey(orm['dossiers.patientcontact'], null=False)),
            ('patientaddress', models.ForeignKey(orm['dossiers.patientaddress'], null=False))
        ))
        db.create_unique('dossiers_patientcontact_addresses', ['patientcontact_id', 'patientaddress_id'])

        # Adding model 'PatientRecord'
        db.create_table('dossiers_patientrecord', (
            ('comment', self.gf('django.db.models.fields.TextField')(default=None, null=True, blank=True)),
            ('transporttype', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['ressources.TransportType'], null=True, blank=True)),
            ('weight', self.gf('django.db.models.fields.IntegerField')(default=None, null=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('outto', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['ressources.OutTo'], null=True, blank=True)),
            ('paper_id', self.gf('django.db.models.fields.CharField')(max_length=6, null=True, blank=True)),
            ('familymotive', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['ressources.FamilyMotive'], null=True, blank=True)),
            ('externalintervener', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['personnes.ExternalWorker'], null=True, blank=True)),
            ('apgar_score_two', self.gf('django.db.models.fields.IntegerField')(default=None, null=True, blank=True)),
            ('rm_mother', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='rm_mother', null=True, blank=True, to=orm['ressources.MaritalStatusType'])),
            ('size', self.gf('django.db.models.fields.IntegerField')(default=None, null=True, blank=True)),
            ('last_state', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['dossiers.FileState'])),
            ('externaldoctor', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['personnes.ExternalTherapist'], null=True, blank=True)),
            ('pause', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('pregnancy_term', self.gf('django.db.models.fields.IntegerField')(default=None, null=True, blank=True)),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ressources.Service'], null=True, blank=True)),
            ('job_mother', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='job_mother', null=True, blank=True, to=orm['ressources.Job'])),
            ('apgar_score_one', self.gf('django.db.models.fields.IntegerField')(default=None, null=True, blank=True)),
            ('provenance', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['ressources.Provenance'], null=True, blank=True)),
            ('cranium_perimeter', self.gf('django.db.models.fields.DecimalField')(default=None, null=True, max_digits=5, decimal_places=2, blank=True)),
            ('outmotive', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['ressources.OutMotive'], null=True, blank=True)),
            ('job_father', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='job_father', null=True, blank=True, to=orm['ressources.Job'])),
            ('nb_children_family', self.gf('django.db.models.fields.IntegerField')(default=None, null=True, blank=True)),
            ('transportcompany', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['ressources.TransportCompany'], null=True, blank=True)),
            ('policyholder', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['dossiers.PatientContact'])),
            ('confidential', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('old_id', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('advicegiver', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['ressources.AdviceGiver'], null=True, blank=True)),
            ('rm_father', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='rm_father', null=True, blank=True, to=orm['ressources.MaritalStatusType'])),
            ('nationality', self.gf('django.db.models.fields.CharField')(max_length=70, null=True, blank=True)),
            ('old_old_id', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('parental_authority', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['ressources.ParentalAuthorityType'], null=True, blank=True)),
            ('sibship_place', self.gf('django.db.models.fields.IntegerField')(default=None, null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('child_custody', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['ressources.ParentalCustodyType'], null=True, blank=True)),
            ('family_comment', self.gf('django.db.models.fields.TextField')(default=None, null=True, blank=True)),
            ('family_situation', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['ressources.FamilySituationType'], null=True, blank=True)),
            ('analysemotive', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['ressources.AnalyseMotive'], null=True, blank=True)),
            ('chest_perimeter', self.gf('django.db.models.fields.DecimalField')(default=None, null=True, max_digits=5, decimal_places=2, blank=True)),
            ('patientcontact_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['dossiers.PatientContact'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('dossiers', ['PatientRecord'])

        # Adding M2M table for field coordinators on 'PatientRecord'
        db.create_table('dossiers_patientrecord_coordinators', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('patientrecord', models.ForeignKey(orm['dossiers.patientrecord'], null=False)),
            ('worker', models.ForeignKey(orm['personnes.worker'], null=False))
        ))
        db.create_unique('dossiers_patientrecord_coordinators', ['patientrecord_id', 'worker_id'])

        # Adding M2M table for field contacts on 'PatientRecord'
        db.create_table('dossiers_patientrecord_contacts', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('patientrecord', models.ForeignKey(orm['dossiers.patientrecord'], null=False)),
            ('patientcontact', models.ForeignKey(orm['dossiers.patientcontact'], null=False))
        ))
        db.create_unique('dossiers_patientrecord_contacts', ['patientrecord_id', 'patientcontact_id'])

        # Adding M2M table for field mdph_responses on 'PatientRecord'
        db.create_table('dossiers_patientrecord_mdph_responses', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('patientrecord', models.ForeignKey(orm['dossiers.patientrecord'], null=False)),
            ('mdphresponse', models.ForeignKey(orm['ressources.mdphresponse'], null=False))
        ))
        db.create_unique('dossiers_patientrecord_mdph_responses', ['patientrecord_id', 'mdphresponse_id'])

        # Adding M2M table for field mises_2 on 'PatientRecord'
        db.create_table('dossiers_patientrecord_mises_2', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('patientrecord', models.ForeignKey(orm['dossiers.patientrecord'], null=False)),
            ('codecftmea', models.ForeignKey(orm['ressources.codecftmea'], null=False))
        ))
        db.create_unique('dossiers_patientrecord_mises_2', ['patientrecord_id', 'codecftmea_id'])

        # Adding M2M table for field mises_1 on 'PatientRecord'
        db.create_table('dossiers_patientrecord_mises_1', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('patientrecord', models.ForeignKey(orm['dossiers.patientrecord'], null=False)),
            ('codecftmea', models.ForeignKey(orm['ressources.codecftmea'], null=False))
        ))
        db.create_unique('dossiers_patientrecord_mises_1', ['patientrecord_id', 'codecftmea_id'])

        # Adding M2M table for field socialisation_durations on 'PatientRecord'
        db.create_table('dossiers_patientrecord_socialisation_durations', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('patientrecord', models.ForeignKey(orm['dossiers.patientrecord'], null=False)),
            ('socialisationduration', models.ForeignKey(orm['ressources.socialisationduration'], null=False))
        ))
        db.create_unique('dossiers_patientrecord_socialisation_durations', ['patientrecord_id', 'socialisationduration_id'])

        # Adding M2M table for field mdph_requests on 'PatientRecord'
        db.create_table('dossiers_patientrecord_mdph_requests', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('patientrecord', models.ForeignKey(orm['dossiers.patientrecord'], null=False)),
            ('mdphrequest', models.ForeignKey(orm['ressources.mdphrequest'], null=False))
        ))
        db.create_unique('dossiers_patientrecord_mdph_requests', ['patientrecord_id', 'mdphrequest_id'])

        # Adding M2M table for field mises_3 on 'PatientRecord'
        db.create_table('dossiers_patientrecord_mises_3', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('patientrecord', models.ForeignKey(orm['dossiers.patientrecord'], null=False)),
            ('codecftmea', models.ForeignKey(orm['ressources.codecftmea'], null=False))
        ))
        db.create_unique('dossiers_patientrecord_mises_3', ['patientrecord_id', 'codecftmea_id'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'HealthCare'
        db.delete_table('dossiers_healthcare')

        # Deleting model 'CmppHealthCareDiagnostic'
        db.delete_table('dossiers_cmpphealthcarediagnostic')

        # Deleting model 'CmppHealthCareTreatment'
        db.delete_table('dossiers_cmpphealthcaretreatment')

        # Deleting model 'SessadHealthCareNotification'
        db.delete_table('dossiers_sessadhealthcarenotification')

        # Deleting model 'Status'
        db.delete_table('dossiers_status')

        # Removing M2M table for field services on 'Status'
        db.delete_table('dossiers_status_services')

        # Deleting model 'FileState'
        db.delete_table('dossiers_filestate')

        # Deleting model 'PatientAddress'
        db.delete_table('dossiers_patientaddress')

        # Deleting model 'PatientContact'
        db.delete_table('dossiers_patientcontact')

        # Removing M2M table for field addresses on 'PatientContact'
        db.delete_table('dossiers_patientcontact_addresses')

        # Deleting model 'PatientRecord'
        db.delete_table('dossiers_patientrecord')

        # Removing M2M table for field coordinators on 'PatientRecord'
        db.delete_table('dossiers_patientrecord_coordinators')

        # Removing M2M table for field contacts on 'PatientRecord'
        db.delete_table('dossiers_patientrecord_contacts')

        # Removing M2M table for field mdph_responses on 'PatientRecord'
        db.delete_table('dossiers_patientrecord_mdph_responses')

        # Removing M2M table for field mises_2 on 'PatientRecord'
        db.delete_table('dossiers_patientrecord_mises_2')

        # Removing M2M table for field mises_1 on 'PatientRecord'
        db.delete_table('dossiers_patientrecord_mises_1')

        # Removing M2M table for field socialisation_durations on 'PatientRecord'
        db.delete_table('dossiers_patientrecord_socialisation_durations')

        # Removing M2M table for field mdph_requests on 'PatientRecord'
        db.delete_table('dossiers_patientrecord_mdph_requests')

        # Removing M2M table for field mises_3 on 'PatientRecord'
        db.delete_table('dossiers_patientrecord_mises_3')
    
    
    models = {
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
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 2, 13, 16, 37, 34, 720049)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 2, 13, 16, 37, 34, 719965)'}),
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
        'dossiers.cmpphealthcarediagnostic': {
            'Meta': {'object_name': 'CmppHealthCareDiagnostic', '_ormbases': ['dossiers.HealthCare']},
            'act_number': ('django.db.models.fields.IntegerField', [], {'default': '6'}),
            'healthcare_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['dossiers.HealthCare']", 'unique': 'True', 'primary_key': 'True'})
        },
        'dossiers.cmpphealthcaretreatment': {
            'Meta': {'object_name': 'CmppHealthCareTreatment', '_ormbases': ['dossiers.HealthCare']},
            'act_number': ('django.db.models.fields.IntegerField', [], {'default': '30'}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'healthcare_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['dossiers.HealthCare']", 'unique': 'True', 'primary_key': 'True'}),
            'prolongation': ('django.db.models.fields.IntegerField', [], {'default': '0'})
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
        'dossiers.sessadhealthcarenotification': {
            'Meta': {'object_name': 'SessadHealthCareNotification', '_ormbases': ['dossiers.HealthCare']},
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'healthcare_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['dossiers.HealthCare']", 'unique': 'True', 'primary_key': 'True'})
        },
        'dossiers.status': {
            'Meta': {'object_name': 'Status'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'services': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ressources.Service']", 'symmetrical': 'False'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '80'})
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
            'initials': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '5'}),
            'old_camsp_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_cmpp_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_sessad_dys_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_sessad_ted_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'people_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['personnes.People']", 'unique': 'True', 'primary_key': 'True'}),
            'services': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['ressources.Service']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ressources.WorkerType']"})
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
    
    complete_apps = ['dossiers']
