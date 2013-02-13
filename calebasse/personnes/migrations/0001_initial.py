# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Role'
        db.create_table('personnes_role', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('personnes', ['Role'])

        # Adding M2M table for field users on 'Role'
        db.create_table('personnes_role_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('role', models.ForeignKey(orm['personnes.role'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('personnes_role_users', ['role_id', 'user_id'])

        # Adding model 'People'
        db.create_table('personnes_people', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=128, db_index=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=256, db_index=True)),
            ('gender', self.gf('django.db.models.fields.IntegerField')(max_length=1, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('phone', self.gf('calebasse.models.PhoneNumberField')(max_length=20, null=True, blank=True)),
        ))
        db.send_create_signal('personnes', ['People'])

        # Adding model 'Worker'
        db.create_table('personnes_worker', (
            ('people_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['personnes.People'], unique=True, primary_key=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ressources.WorkerType'])),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('old_camsp_id', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('old_cmpp_id', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('old_sessad_dys_id', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('old_sessad_ted_id', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
        ))
        db.send_create_signal('personnes', ['Worker'])

        # Adding M2M table for field services on 'Worker'
        db.create_table('personnes_worker_services', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('worker', models.ForeignKey(orm['personnes.worker'], null=False)),
            ('service', models.ForeignKey(orm['ressources.service'], null=False))
        ))
        db.create_unique('personnes_worker_services', ['worker_id', 'service_id'])

        # Adding model 'ExternalWorker'
        db.create_table('personnes_externalworker', (
            ('people_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['personnes.People'], unique=True, primary_key=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default=None, null=True, blank=True)),
            ('address', self.gf('django.db.models.fields.CharField')(default=None, max_length=120, null=True, blank=True)),
            ('address_complement', self.gf('django.db.models.fields.CharField')(default=None, max_length=120, null=True, blank=True)),
            ('zip_code', self.gf('calebasse.models.ZipCodeField')(default=None, max_length=5, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(default=None, max_length=80, null=True, blank=True)),
            ('phone_work', self.gf('calebasse.models.PhoneNumberField')(default=None, max_length=20, null=True, blank=True)),
            ('fax', self.gf('django.db.models.fields.CharField')(default=None, max_length=30, null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(default=18, to=orm['ressources.WorkerType'])),
            ('old_id', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('old_service', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
        ))
        db.send_create_signal('personnes', ['ExternalWorker'])

        # Adding model 'ExternalTherapist'
        db.create_table('personnes_externaltherapist', (
            ('people_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['personnes.People'], unique=True, primary_key=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default=None, null=True, blank=True)),
            ('address', self.gf('django.db.models.fields.CharField')(default=None, max_length=120, null=True, blank=True)),
            ('address_complement', self.gf('django.db.models.fields.CharField')(default=None, max_length=120, null=True, blank=True)),
            ('zip_code', self.gf('calebasse.models.ZipCodeField')(default=None, max_length=5, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(default=None, max_length=80, null=True, blank=True)),
            ('phone_work', self.gf('calebasse.models.PhoneNumberField')(default=None, max_length=20, null=True, blank=True)),
            ('fax', self.gf('django.db.models.fields.CharField')(default=None, max_length=30, null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(default=18, to=orm['ressources.WorkerType'])),
            ('old_id', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('old_service', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
        ))
        db.send_create_signal('personnes', ['ExternalTherapist'])

        # Adding model 'UserWorker'
        db.create_table('personnes_userworker', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('worker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['personnes.Worker'])),
        ))
        db.send_create_signal('personnes', ['UserWorker'])

        # Adding model 'SchoolTeacher'
        db.create_table('personnes_schoolteacher', (
            ('people_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['personnes.People'], unique=True, primary_key=True)),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ressources.SchoolTeacherRole'])),
        ))
        db.send_create_signal('personnes', ['SchoolTeacher'])

        # Adding M2M table for field schools on 'SchoolTeacher'
        db.create_table('personnes_schoolteacher_schools', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('schoolteacher', models.ForeignKey(orm['personnes.schoolteacher'], null=False)),
            ('school', models.ForeignKey(orm['ressources.school'], null=False))
        ))
        db.create_unique('personnes_schoolteacher_schools', ['schoolteacher_id', 'school_id'])

        # Adding model 'TimeTable'
        db.create_table('personnes_timetable', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('worker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['personnes.Worker'])),
            ('weekday', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('start_time', self.gf('django.db.models.fields.TimeField')()),
            ('end_time', self.gf('django.db.models.fields.TimeField')()),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('periodicity', self.gf('django.db.models.fields.PositiveIntegerField')(default=1, null=True, blank=True)),
            ('week_offset', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('week_period', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('week_parity', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('week_rank', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('personnes', ['TimeTable'])

        # Adding M2M table for field services on 'TimeTable'
        db.create_table('personnes_timetable_services', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('timetable', models.ForeignKey(orm['personnes.timetable'], null=False)),
            ('service', models.ForeignKey(orm['ressources.service'], null=False))
        ))
        db.create_unique('personnes_timetable_services', ['timetable_id', 'service_id'])

        # Adding model 'Holiday'
        db.create_table('personnes_holiday', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('holiday_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ressources.HolidayType'])),
            ('worker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['personnes.Worker'], null=True, blank=True)),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ressources.Service'], null=True, blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')()),
            ('start_time', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('end_time', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('personnes', ['Holiday'])


    def backwards(self, orm):
        # Deleting model 'Role'
        db.delete_table('personnes_role')

        # Removing M2M table for field users on 'Role'
        db.delete_table('personnes_role_users')

        # Deleting model 'People'
        db.delete_table('personnes_people')

        # Deleting model 'Worker'
        db.delete_table('personnes_worker')

        # Removing M2M table for field services on 'Worker'
        db.delete_table('personnes_worker_services')

        # Deleting model 'ExternalWorker'
        db.delete_table('personnes_externalworker')

        # Deleting model 'ExternalTherapist'
        db.delete_table('personnes_externaltherapist')

        # Deleting model 'UserWorker'
        db.delete_table('personnes_userworker')

        # Deleting model 'SchoolTeacher'
        db.delete_table('personnes_schoolteacher')

        # Removing M2M table for field schools on 'SchoolTeacher'
        db.delete_table('personnes_schoolteacher_schools')

        # Deleting model 'TimeTable'
        db.delete_table('personnes_timetable')

        # Removing M2M table for field services on 'TimeTable'
        db.delete_table('personnes_timetable_services')

        # Deleting model 'Holiday'
        db.delete_table('personnes_holiday')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'personnes.externaltherapist': {
            'Meta': {'ordering': "['last_name', 'first_name']", 'object_name': 'ExternalTherapist', '_ormbases': ['personnes.People']},
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
            'Meta': {'ordering': "['last_name', 'first_name']", 'object_name': 'ExternalWorker', '_ormbases': ['personnes.People']},
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
        'personnes.holiday': {
            'Meta': {'ordering': "('start_date', 'start_time')", 'object_name': 'Holiday'},
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'end_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'holiday_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ressources.HolidayType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ressources.Service']", 'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'start_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'worker': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['personnes.Worker']", 'null': 'True', 'blank': 'True'})
        },
        'personnes.people': {
            'Meta': {'ordering': "['last_name', 'first_name']", 'object_name': 'People'},
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'db_index': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.IntegerField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'phone': ('calebasse.models.PhoneNumberField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        'personnes.role': {
            'Meta': {'ordering': "['name']", 'object_name': 'Role'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'personnes.schoolteacher': {
            'Meta': {'ordering': "['last_name', 'first_name']", 'object_name': 'SchoolTeacher', '_ormbases': ['personnes.People']},
            'people_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['personnes.People']", 'unique': 'True', 'primary_key': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ressources.SchoolTeacherRole']"}),
            'schools': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ressources.School']", 'symmetrical': 'False'})
        },
        'personnes.timetable': {
            'Meta': {'object_name': 'TimeTable'},
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'end_time': ('django.db.models.fields.TimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'periodicity': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'services': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ressources.Service']", 'symmetrical': 'False'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'start_time': ('django.db.models.fields.TimeField', [], {}),
            'week_offset': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'week_parity': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'week_period': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'week_rank': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'weekday': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'worker': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['personnes.Worker']"})
        },
        'personnes.userworker': {
            'Meta': {'object_name': 'UserWorker'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'worker': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['personnes.Worker']"})
        },
        'personnes.worker': {
            'Meta': {'ordering': "['last_name', 'first_name']", 'object_name': 'Worker', '_ormbases': ['personnes.People']},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'old_camsp_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_cmpp_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_sessad_dys_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'old_sessad_ted_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'people_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['personnes.People']", 'unique': 'True', 'primary_key': 'True'}),
            'services': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['ressources.Service']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ressources.WorkerType']"})
        },
        'ressources.holidaytype': {
            'Meta': {'object_name': 'HolidayType'},
            'for_group': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        'ressources.workertype': {
            'Meta': {'object_name': 'WorkerType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intervene': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        }
    }

    complete_apps = ['personnes']