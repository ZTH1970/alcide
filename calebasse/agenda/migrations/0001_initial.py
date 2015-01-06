# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('ressources', '0001_initial'),
        ('dossiers', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('personnes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(default=b'', max_length=60, verbose_name='Title', blank=True)),
                ('description', models.TextField(max_length=100, null=True, verbose_name='Description', blank=True)),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Date de cr\xe9ation')),
                ('start_datetime', models.DateTimeField(verbose_name='D\xe9but', db_index=True)),
                ('end_datetime', models.DateTimeField(null=True, verbose_name='Fin', blank=True)),
                ('old_ev_id', models.CharField(max_length=8, null=True, blank=True)),
                ('old_rr_id', models.CharField(max_length=8, null=True, blank=True)),
                ('old_rs_id', models.CharField(max_length=8, null=True, blank=True)),
                ('exception_date', models.DateField(db_index=True, null=True, verbose_name='Report\xe9 du', blank=True)),
                ('canceled', models.BooleanField(default=False, db_index=True, verbose_name='Annul\xe9')),
                ('recurrence_periodicity', models.PositiveIntegerField(default=None, choices=[(1, 'Toutes les semaines'), (2, 'Une semaine sur deux'), (3, 'Une semaine sur trois'), (4, 'Une semaine sur quatre'), (5, 'Une semaine sur cinq'), (6, 'La premi\xe8re semaine du mois'), (7, 'La deuxi\xe8me semaine du mois'), (8, 'La troisi\xe8me semaine du mois'), (9, 'La quatri\xe8me semaine du mois'), (13, 'La cinqui\xe8me semaine du mois'), (10, 'La derni\xe8re semaine du mois'), (11, 'Les semaines paires'), (12, 'Les semaines impaires')], blank=True, null=True, verbose_name='P\xe9riodicit\xe9', db_index=True)),
                ('recurrence_week_day', models.PositiveIntegerField(default=0, db_index=True)),
                ('recurrence_week_offset', models.PositiveIntegerField(default=0, db_index=True, verbose_name='D\xe9calage en semaines par rapport au 1/1/1970 pour le calcul de p\xe9riode', choices=[(0, 0), (1, 1), (2, 2), (3, 3)])),
                ('recurrence_week_period', models.PositiveIntegerField(default=None, choices=[(1, 'Toutes les semaines'), (2, 'Une semaine sur deux'), (3, 'Une semaine sur trois'), (4, 'Une semaine sur quatre'), (5, 'Une semaine sur cinq')], blank=True, null=True, verbose_name='P\xe9riode en semaines', db_index=True)),
                ('recurrence_week_rank', models.IntegerField(blank=True, null=True, verbose_name='Rang de la semaine dans le mois', db_index=True, choices=[(0, 'La premi\xe8re semaine du mois'), (1, 'La deuxi\xe8me semaine du mois'), (2, 'La troisi\xe8me semaine du mois'), (3, 'La quatri\xe8me semaine du mois'), (4, 'La cinqui\xe8me semaine du mois'), (-1, 'La derni\xe8re semaine du mois')])),
                ('recurrence_week_parity', models.PositiveIntegerField(blank=True, null=True, verbose_name='Parit\xe9 des semaines', db_index=True, choices=[(0, 'Les semaines paires'), (1, 'Les semaines impaires')])),
                ('recurrence_end_date', models.DateField(db_index=True, null=True, verbose_name='Fin de la r\xe9currence', blank=True)),
            ],
            options={
                'ordering': ('start_datetime', 'end_datetime', 'title'),
                'verbose_name': 'Ev\xe9nement',
                'verbose_name_plural': 'Ev\xe9nements',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=50, verbose_name='label')),
                ('rank', models.IntegerField(default=0, null=True, verbose_name='Sorting Rank', blank=True)),
            ],
            options={
                'verbose_name': "Type d'\xe9v\xe9nement",
                'verbose_name_plural': "Types d'\xe9v\xe9nement",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventWithAct',
            fields=[
                ('event_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='agenda.Event')),
                ('convocation_sent', models.BooleanField(default=False, db_index=True, verbose_name='Convoqu\xe9')),
                ('act_type', models.ForeignKey(verbose_name="Type d'acte", to='ressources.ActType')),
                ('patient', models.ForeignKey(to='dossiers.PatientRecord')),
            ],
            options={
            },
            bases=('agenda.event',),
        ),
        migrations.AddField(
            model_name='event',
            name='creator',
            field=models.ForeignKey(verbose_name='Cr\xe9ateur', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='event_type',
            field=models.ForeignKey(verbose_name="Type d'\xe9v\xe9nement", to='agenda.EventType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='exception_to',
            field=models.ForeignKey(related_name='exceptions', verbose_name='Exception \xe0', blank=True, to='agenda.Event', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='participants',
            field=models.ManyToManyField(default=None, to='personnes.People', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='ressource',
            field=models.ForeignKey(verbose_name='Ressource', blank=True, to='ressources.Ressource', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='services',
            field=models.ManyToManyField(default=None, to='ressources.Service', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='event',
            unique_together=set([('exception_to', 'exception_date')]),
        ),
    ]
