# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'HealthCenter'
        db.create_table('ressources_healthcenter', (
            ('correspondant', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('fax', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=4, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('abbreviation', self.gf('django.db.models.fields.CharField')(default=True, max_length=8, null=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('dest_organism', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('computer_center_code', self.gf('django.db.models.fields.CharField')(default=True, max_length=8, null=True)),
            ('accounting_number', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('large_regime', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ressources.LargeRegime'])),
            ('health_fund', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('address_complement', self.gf('django.db.models.fields.CharField')(default=None, max_length=120, null=True, blank=True)),
        ))
        db.send_create_signal('ressources', ['HealthCenter'])

        # Adding model 'LargeRegime'
        db.create_table('ressources_largeregime', (
            ('code', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('ressources', ['LargeRegime'])

        # Adding model 'TransportCompany'
        db.create_table('ressources_transportcompany', (
            ('city', self.gf('django.db.models.fields.CharField')(default=None, max_length=80, null=True, blank=True)),
            ('fax', self.gf('django.db.models.fields.CharField')(default=None, max_length=30, null=True, blank=True)),
            ('old_sessad_dys_id', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('address_complement', self.gf('django.db.models.fields.CharField')(default=None, max_length=120, null=True, blank=True)),
            ('old_cmpp_id', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default=None, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('phone', self.gf('calebasse.models.PhoneNumberField')(default=None, max_length=20, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('old_camsp_id', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('address', self.gf('django.db.models.fields.CharField')(default=None, max_length=120, null=True, blank=True)),
            ('old_sessad_ted_id', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('correspondant', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('zip_code', self.gf('calebasse.models.ZipCodeField')(default=None, max_length=5, null=True, blank=True)),
        ))
        db.send_create_signal('ressources', ['TransportCompany'])

        # Adding model 'UninvoicableCode'
        db.create_table('ressources_uninvoicablecode', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('ressources', ['UninvoicableCode'])

        # Adding model 'Office'
        db.create_table('ressources_office', (
            ('city', self.gf('django.db.models.fields.CharField')(default=None, max_length=80, null=True, blank=True)),
            ('fax', self.gf('calebasse.models.PhoneNumberField')(max_length=20, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('address_complement', self.gf('django.db.models.fields.CharField')(default=None, max_length=120, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('phone', self.gf('calebasse.models.PhoneNumberField')(max_length=20, null=True, blank=True)),
            ('address', self.gf('django.db.models.fields.CharField')(default=None, max_length=120, null=True, blank=True)),
            ('zip_code', self.gf('calebasse.models.ZipCodeField')(default=None, max_length=5, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('ressources', ['Office'])

        # Adding model 'SchoolType'
        db.create_table('ressources_schooltype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('ressources', ['SchoolType'])

        # Adding M2M table for field services on 'SchoolType'
        db.create_table('ressources_schooltype_services', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('schooltype', models.ForeignKey(orm['ressources.schooltype'], null=False)),
            ('service', models.ForeignKey(orm['ressources.service'], null=False))
        ))
        db.create_unique('ressources_schooltype_services', ['schooltype_id', 'service_id'])

        # Adding model 'School'
        db.create_table('ressources_school', (
            ('director_name', self.gf('django.db.models.fields.CharField')(default=None, max_length=70, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(default=None, max_length=80, null=True, blank=True)),
            ('fax', self.gf('django.db.models.fields.CharField')(default=None, max_length=30, null=True, blank=True)),
            ('address_complement', self.gf('django.db.models.fields.CharField')(default=None, max_length=120, null=True, blank=True)),
            ('old_id', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('school_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ressources.SchoolType'])),
            ('phone', self.gf('calebasse.models.PhoneNumberField')(default=None, max_length=20, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(default=None, max_length=75, null=True, blank=True)),
            ('address', self.gf('django.db.models.fields.CharField')(default=None, max_length=120, null=True, blank=True)),
            ('zip_code', self.gf('calebasse.models.ZipCodeField')(default=None, max_length=5, null=True, blank=True)),
            ('old_service', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default=None, null=True, blank=True)),
        ))
        db.send_create_signal('ressources', ['School'])

        # Adding model 'SchoolTeacherRole'
        db.create_table('ressources_schoolteacherrole', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('ressources', ['SchoolTeacherRole'])

        # Adding model 'SchoolLevel'
        db.create_table('ressources_schoollevel', (
            ('old_id', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('old_service', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('ressources', ['SchoolLevel'])

        # Adding model 'SocialisationDuration'
        db.create_table('ressources_socialisationduration', (
            ('comment', self.gf('django.db.models.fields.TextField')(max_length=3000, null=True, blank=True)),
            ('school', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ressources.School'], null=True, blank=True)),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('level', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ressources.SchoolLevel'], null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('contact', self.gf('django.db.models.fields.CharField')(default=None, max_length=200, null=True, blank=True)),
            ('redoublement', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('ressources', ['SocialisationDuration'])

        # Adding model 'InscriptionMotive'
        db.create_table('ressources_inscriptionmotive', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('ressources', ['InscriptionMotive'])

        # Adding model 'Provenance'
        db.create_table('ressources_provenance', (
            ('old_id', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('old_service', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('ressources', ['Provenance'])

        # Adding model 'Nationality'
        db.create_table('ressources_nationality', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('ressources', ['Nationality'])

        # Adding model 'Job'
        db.create_table('ressources_job', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('ressources', ['Job'])

        # Adding model 'Room'
        db.create_table('ressources_room', (
            ('etablissement', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ressources.Office'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('ressources', ['Room'])

        # Adding model 'AnalyseMotive'
        db.create_table('ressources_analysemotive', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('ressources', ['AnalyseMotive'])

        # Adding model 'FamilyMotive'
        db.create_table('ressources_familymotive', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('ressources', ['FamilyMotive'])

        # Adding model 'OutMotive'
        db.create_table('ressources_outmotive', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('ressources', ['OutMotive'])

        # Adding model 'OutTo'
        db.create_table('ressources_outto', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('ressources', ['OutTo'])

        # Adding model 'AdviceGiver'
        db.create_table('ressources_advicegiver', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('ressources', ['AdviceGiver'])

        # Adding model 'Service'
        db.create_table('ressources_service', (
            ('fax', self.gf('calebasse.models.PhoneNumberField')(max_length=20)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('phone', self.gf('calebasse.models.PhoneNumberField')(max_length=20)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('ressources', ['Service'])

        # Adding model 'ActType'
        db.create_table('ressources_acttype', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ressources.Service'], null=True, blank=True)),
            ('old_id', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('display_first', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('billable', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('ressources', ['ActType'])

        # Adding model 'ParentalAuthorityType'
        db.create_table('ressources_parentalauthoritytype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('ressources', ['ParentalAuthorityType'])

        # Adding model 'ParentalCustodyType'
        db.create_table('ressources_parentalcustodytype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('ressources', ['ParentalCustodyType'])

        # Adding model 'SessionType'
        db.create_table('ressources_sessiontype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('ressources', ['SessionType'])

        # Adding model 'FamilySituationType'
        db.create_table('ressources_familysituationtype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('ressources', ['FamilySituationType'])

        # Adding model 'MaritalStatusType'
        db.create_table('ressources_maritalstatustype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('ressources', ['MaritalStatusType'])

        # Adding model 'TransportType'
        db.create_table('ressources_transporttype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('ressources', ['TransportType'])

        # Adding model 'WorkerType'
        db.create_table('ressources_workertype', (
            ('intervene', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('ressources', ['WorkerType'])

        # Adding model 'CodeCFTMEA'
        db.create_table('ressources_codecftmea', (
            ('code', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('axe', self.gf('django.db.models.fields.IntegerField')(max_length=1)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('ressources', ['CodeCFTMEA'])

        # Adding model 'MDPH'
        db.create_table('ressources_mdph', (
            ('website', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('fax', self.gf('calebasse.models.PhoneNumberField')(max_length=20, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('phone', self.gf('calebasse.models.PhoneNumberField')(max_length=20, null=True, blank=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=120, null=True, blank=True)),
            ('department', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('zip_code', self.gf('calebasse.models.ZipCodeField')(max_length=5, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('address_complement', self.gf('django.db.models.fields.CharField')(default=None, max_length=120, null=True, blank=True)),
        ))
        db.send_create_signal('ressources', ['MDPH'])

        # Adding model 'MDPHRequest'
        db.create_table('ressources_mdphrequest', (
            ('comment', self.gf('django.db.models.fields.TextField')(max_length=3000, null=True, blank=True)),
            ('mdph', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ressources.MDPH'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('ressources', ['MDPHRequest'])

        # Adding model 'MDPHResponse'
        db.create_table('ressources_mdphresponse', (
            ('comment', self.gf('django.db.models.fields.TextField')(max_length=3000, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('end_date', self.gf('django.db.models.fields.DateField')()),
            ('mdph', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ressources.MDPH'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('type_aide', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=1)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('rate', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('ressources', ['MDPHResponse'])

        # Adding model 'HolidayType'
        db.create_table('ressources_holidaytype', (
            ('for_group', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('ressources', ['HolidayType'])

        # Adding model 'PatientRelatedLink'
        db.create_table('ressources_patientrelatedlink', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('old_cmpp_id', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('old_camsp_id', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('old_sessad_ted_id', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('old_sessad_dys_id', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('ressources', ['PatientRelatedLink'])

        # Adding model 'PricePerAct'
        db.create_table('ressources_priceperact', (
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('ressources', ['PricePerAct'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'HealthCenter'
        db.delete_table('ressources_healthcenter')

        # Deleting model 'LargeRegime'
        db.delete_table('ressources_largeregime')

        # Deleting model 'TransportCompany'
        db.delete_table('ressources_transportcompany')

        # Deleting model 'UninvoicableCode'
        db.delete_table('ressources_uninvoicablecode')

        # Deleting model 'Office'
        db.delete_table('ressources_office')

        # Deleting model 'SchoolType'
        db.delete_table('ressources_schooltype')

        # Removing M2M table for field services on 'SchoolType'
        db.delete_table('ressources_schooltype_services')

        # Deleting model 'School'
        db.delete_table('ressources_school')

        # Deleting model 'SchoolTeacherRole'
        db.delete_table('ressources_schoolteacherrole')

        # Deleting model 'SchoolLevel'
        db.delete_table('ressources_schoollevel')

        # Deleting model 'SocialisationDuration'
        db.delete_table('ressources_socialisationduration')

        # Deleting model 'InscriptionMotive'
        db.delete_table('ressources_inscriptionmotive')

        # Deleting model 'Provenance'
        db.delete_table('ressources_provenance')

        # Deleting model 'Nationality'
        db.delete_table('ressources_nationality')

        # Deleting model 'Job'
        db.delete_table('ressources_job')

        # Deleting model 'Room'
        db.delete_table('ressources_room')

        # Deleting model 'AnalyseMotive'
        db.delete_table('ressources_analysemotive')

        # Deleting model 'FamilyMotive'
        db.delete_table('ressources_familymotive')

        # Deleting model 'OutMotive'
        db.delete_table('ressources_outmotive')

        # Deleting model 'OutTo'
        db.delete_table('ressources_outto')

        # Deleting model 'AdviceGiver'
        db.delete_table('ressources_advicegiver')

        # Deleting model 'Service'
        db.delete_table('ressources_service')

        # Deleting model 'ActType'
        db.delete_table('ressources_acttype')

        # Deleting model 'ParentalAuthorityType'
        db.delete_table('ressources_parentalauthoritytype')

        # Deleting model 'ParentalCustodyType'
        db.delete_table('ressources_parentalcustodytype')

        # Deleting model 'SessionType'
        db.delete_table('ressources_sessiontype')

        # Deleting model 'FamilySituationType'
        db.delete_table('ressources_familysituationtype')

        # Deleting model 'MaritalStatusType'
        db.delete_table('ressources_maritalstatustype')

        # Deleting model 'TransportType'
        db.delete_table('ressources_transporttype')

        # Deleting model 'WorkerType'
        db.delete_table('ressources_workertype')

        # Deleting model 'CodeCFTMEA'
        db.delete_table('ressources_codecftmea')

        # Deleting model 'MDPH'
        db.delete_table('ressources_mdph')

        # Deleting model 'MDPHRequest'
        db.delete_table('ressources_mdphrequest')

        # Deleting model 'MDPHResponse'
        db.delete_table('ressources_mdphresponse')

        # Deleting model 'HolidayType'
        db.delete_table('ressources_holidaytype')

        # Deleting model 'PatientRelatedLink'
        db.delete_table('ressources_patientrelatedlink')

        # Deleting model 'PricePerAct'
        db.delete_table('ressources_priceperact')
    
    
    models = {
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
        'ressources.holidaytype': {
            'Meta': {'object_name': 'HolidayType'},
            'for_group': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'ressources.inscriptionmotive': {
            'Meta': {'object_name': 'InscriptionMotive'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
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
        'ressources.nationality': {
            'Meta': {'object_name': 'Nationality'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
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
        'ressources.priceperact': {
            'Meta': {'object_name': 'PricePerAct'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'start_date': ('django.db.models.fields.DateField', [], {})
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
        'ressources.schoolteacherrole': {
            'Meta': {'object_name': 'SchoolTeacherRole'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
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
        'ressources.sessiontype': {
            'Meta': {'object_name': 'SessionType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
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
        'ressources.uninvoicablecode': {
            'Meta': {'object_name': 'UninvoicableCode'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'ressources.workertype': {
            'Meta': {'object_name': 'WorkerType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intervene': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        }
    }
    
    complete_apps = ['ressources']
