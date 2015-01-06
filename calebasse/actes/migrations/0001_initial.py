# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('ressources', '0001_initial'),
        ('agenda', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('personnes', '0001_initial'),
        ('dossiers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Act',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(verbose_name='Date', db_index=True)),
                ('time', models.TimeField(default=datetime.time(0, 0), null=True, verbose_name='Heure', db_index=True, blank=True)),
                ('_duration', models.IntegerField(default=0, null=True, verbose_name='Dur\xe9e en minutes', blank=True)),
                ('validation_locked', models.BooleanField(default=False, db_index=True, verbose_name='V\xe9rouillage')),
                ('is_billed', models.BooleanField(default=False, db_index=True, verbose_name='Factur\xe9')),
                ('already_billed', models.BooleanField(default=False, db_index=True, verbose_name='A d\xe9j\xe0 \xe9t\xe9 factur\xe9')),
                ('is_lost', models.BooleanField(default=False, db_index=True, verbose_name='Acte perdu')),
                ('valide', models.BooleanField(default=False, db_index=True, verbose_name='Valid\xe9')),
                ('switch_billable', models.BooleanField(default=False, verbose_name='Inverser type facturable')),
                ('pause', models.BooleanField(default=False, db_index=True, verbose_name='Pause facturation')),
                ('attendance', models.CharField(default=b'absent', max_length=16, verbose_name='Pr\xe9sence', choices=[(b'absent', 'Absent'), (b'present', 'Pr\xe9sent')])),
                ('old_id', models.CharField(max_length=256, null=True, verbose_name='Ancien ID', blank=True)),
                ('act_type', models.ForeignKey(verbose_name="Type d'acte", to='ressources.ActType')),
                ('doctors', models.ManyToManyField(to='personnes.Worker', verbose_name='Intervenants')),
                ('healthcare', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='Prise en charge utilis\xe9e pour facturer (CMPP)', blank=True, to='dossiers.HealthCare', null=True)),
            ],
            options={
                'ordering': ['-date', 'patient'],
                'verbose_name': 'Acte',
                'verbose_name_plural': 'Actes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ActValidationState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state_name', models.CharField(max_length=150)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Cr\xe9ation')),
                ('auto', models.BooleanField(default=False, verbose_name='Validat\xe9 automatiquement')),
                ('act', models.ForeignKey(editable=False, to='actes.Act', verbose_name='Acte')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, verbose_name='Auteur')),
                ('previous_state', models.ForeignKey(blank=True, editable=False, to='actes.ActValidationState', null=True, verbose_name='Etat pr\xe9c\xe9dent')),
            ],
            options={
                'ordering': ('-created',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ValidationMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('validation_date', models.DateTimeField()),
                ('what', models.CharField(max_length=256)),
                ('when', models.DateTimeField(auto_now_add=True)),
                ('service', models.ForeignKey(blank=True, to='ressources.Service', null=True)),
                ('who', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='act',
            name='last_validation_state',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, default=None, to='actes.ActValidationState', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='act',
            name='parent_event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='Rendez-vous li\xe9', blank=True, to='agenda.Event', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='act',
            name='patient',
            field=models.ForeignKey(to='dossiers.PatientRecord'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='act',
            name='transport_company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='Compagnie de transport', blank=True, to='ressources.TransportCompany', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='act',
            name='transport_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='Type de transport', blank=True, to='ressources.TransportType', null=True),
            preserve_default=True,
        ),
    ]
