# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import calebasse.models


class Migration(migrations.Migration):

    dependencies = [
        ('ressources', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Holiday',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateField(help_text='format: jj/mm/aaaa', verbose_name='Date de d\xe9but')),
                ('end_date', models.DateField(help_text='format: jj/mm/aaaa', verbose_name='Date de fin')),
                ('start_time', models.TimeField(null=True, verbose_name='Horaire de d\xe9but', blank=True)),
                ('end_time', models.TimeField(null=True, verbose_name='Horaire de fin', blank=True)),
                ('comment', models.TextField(verbose_name='Commentaire', blank=True)),
                ('holiday_type', models.ForeignKey(verbose_name='Type de cong\xe9', to='ressources.HolidayType')),
                ('services', models.ManyToManyField(to='ressources.Service', verbose_name='Services')),
            ],
            options={
                'ordering': ('start_date', 'start_time'),
                'verbose_name': 'Cong\xe9',
                'verbose_name_plural': 'Cong\xe9s',
            },
            bases=(calebasse.models.BaseModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='People',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_name', models.CharField(max_length=128, verbose_name='Nom', db_index=True)),
                ('first_name', models.CharField(max_length=128, null=True, verbose_name='Pr\xe9nom(s)', blank=True)),
                ('display_name', models.CharField(verbose_name='Nom complet', max_length=256, editable=False, db_index=True)),
                ('gender', models.IntegerField(blank=True, max_length=1, null=True, verbose_name='Genre', choices=[(1, b'Masculin'), (2, b'F\xc3\xa9minin')])),
                ('email', models.EmailField(max_length=75, null=True, blank=True)),
                ('phone', calebasse.models.PhoneNumberField(max_length=20, null=True, verbose_name='T\xe9l\xe9phone', blank=True)),
            ],
            options={
                'ordering': ['last_name', 'first_name'],
            },
            bases=(calebasse.models.BaseModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ExternalWorker',
            fields=[
                ('people_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='personnes.People')),
                ('description', models.TextField(default=None, null=True, blank=True)),
                ('address', models.CharField(default=None, max_length=120, null=True, verbose_name='Adresse', blank=True)),
                ('address_complement', models.CharField(default=None, max_length=120, null=True, verbose_name="Compl\xe9ment d'adresse", blank=True)),
                ('zip_code', calebasse.models.ZipCodeField(default=None, max_length=5, null=True, verbose_name='Code postal', blank=True)),
                ('city', models.CharField(default=None, max_length=80, null=True, verbose_name='Ville', blank=True)),
                ('phone_work', calebasse.models.PhoneNumberField(default=None, max_length=20, null=True, verbose_name='T\xe9l\xe9phone du travail', blank=True)),
                ('fax', models.CharField(default=None, max_length=30, null=True, blank=True)),
                ('old_id', models.CharField(max_length=256, null=True, verbose_name='Ancien ID', blank=True)),
                ('old_service', models.CharField(max_length=256, null=True, verbose_name='Ancien Service', blank=True)),
                ('type', models.ForeignKey(default=18, verbose_name='Sp\xe9cialit\xe9', to='ressources.WorkerType')),
            ],
            options={
                'verbose_name': 'Intervenant ext\xe9rieur',
                'verbose_name_plural': 'Intervenants ext\xe9rieurs',
            },
            bases=('personnes.people',),
        ),
        migrations.CreateModel(
            name='ExternalTherapist',
            fields=[
                ('people_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='personnes.People')),
                ('description', models.TextField(default=None, null=True, blank=True)),
                ('address', models.CharField(default=None, max_length=120, null=True, verbose_name='Adresse', blank=True)),
                ('address_complement', models.CharField(default=None, max_length=120, null=True, verbose_name="Compl\xe9ment d'adresse", blank=True)),
                ('zip_code', calebasse.models.ZipCodeField(default=None, max_length=5, null=True, verbose_name='Code postal', blank=True)),
                ('city', models.CharField(default=None, max_length=80, null=True, verbose_name='Ville', blank=True)),
                ('phone_work', calebasse.models.PhoneNumberField(default=None, max_length=20, null=True, verbose_name='T\xe9l\xe9phone du travail', blank=True)),
                ('fax', models.CharField(default=None, max_length=30, null=True, blank=True)),
                ('old_id', models.CharField(max_length=256, null=True, verbose_name='Ancien ID', blank=True)),
                ('old_service', models.CharField(max_length=256, null=True, verbose_name='Ancien Service', blank=True)),
                ('type', models.ForeignKey(default=18, verbose_name='Sp\xe9cialit\xe9', to='ressources.WorkerType')),
            ],
            options={
                'verbose_name': 'M\xe9decin ext\xe9rieur',
                'verbose_name_plural': 'M\xe9decins ext\xe9rieurs',
            },
            bases=('personnes.people',),
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='Nom')),
                ('users', models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Utilisateurs', blank=True)),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SchoolTeacher',
            fields=[
                ('people_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='personnes.People')),
                ('role', models.ForeignKey(to='ressources.SchoolTeacherRole')),
                ('schools', models.ManyToManyField(to='ressources.School')),
            ],
            options={
            },
            bases=('personnes.people',),
        ),
        migrations.CreateModel(
            name='TimeTable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('weekday', models.PositiveIntegerField(verbose_name='Jour de la semaine', choices=[(0, b'lundi'), (1, b'mardi'), (2, b'mercredi'), (3, b'jeudi'), (4, b'vendredi'), (5, b'samedi'), (6, b'dimanche')])),
                ('start_time', models.TimeField(verbose_name='Heure de d\xe9but')),
                ('end_time', models.TimeField(verbose_name='Heure de fin')),
                ('start_date', models.DateField(help_text='format: jj/mm/aaaa', verbose_name='D\xe9but')),
                ('end_date', models.DateField(help_text='format: jj/mm/aaaa', null=True, verbose_name='Fin', blank=True)),
                ('periodicity', models.PositiveIntegerField(default=1, null=True, verbose_name='P\xe9riodicit\xe9', blank=True, choices=[(1, 'Toutes les semaines'), (2, 'Une semaine sur deux'), (3, 'Une semaine sur trois'), (4, 'Une semaine sur quatre'), (5, 'Une semaine sur cinq'), (6, 'La premi\xe8re semaine du mois'), (7, 'La deuxi\xe8me semaine du mois'), (8, 'La troisi\xe8me semaine du mois'), (9, 'La quatri\xe8me semaine du mois'), (10, 'La derni\xe8re semaine du mois'), (11, 'Les semaines paires'), (12, 'Les semaines impaires')])),
                ('week_offset', models.PositiveIntegerField(default=0, verbose_name='D\xe9calage en semaines par rapport au 1/1/1970 pour le calcul de p\xe9riode', choices=[(0, 0), (1, 1), (2, 2), (3, 3)])),
                ('week_period', models.PositiveIntegerField(blank=True, null=True, verbose_name='P\xe9riode en semaines', choices=[(1, 'Toutes les semaines'), (2, 'Une semaine sur deux'), (3, 'Une semaine sur trois'), (4, 'Une semaine sur quatre'), (5, 'Une semaine sur cinq')])),
                ('week_parity', models.PositiveIntegerField(blank=True, null=True, verbose_name='Parit\xe9 des semaines', choices=[(0, 'Les semaines paires'), (1, 'Les semaines impaires')])),
                ('week_rank', models.PositiveIntegerField(blank=True, null=True, verbose_name='Rang de la semaine dans le mois', choices=[(0, 'La premi\xe8re semaine du mois'), (1, 'La deuxi\xe8me semaine du mois'), (2, 'La troisi\xe8me semaine du mois'), (3, 'La quatri\xe8me semaine du mois'), (4, 'La derni\xe8re semaine du mois')])),
                ('services', models.ManyToManyField(to='ressources.Service')),
            ],
            options={
                'verbose_name': 'Emploi du temps',
                'verbose_name_plural': 'Emplois du temps',
            },
            bases=(calebasse.models.BaseModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='UserWorker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(calebasse.models.BaseModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Worker',
            fields=[
                ('people_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='personnes.People')),
                ('initials', models.CharField(default=b'', max_length=5, verbose_name='Initiales', blank=True)),
                ('enabled', models.BooleanField(default=True, verbose_name='Actif')),
                ('old_camsp_id', models.CharField(max_length=256, null=True, verbose_name='Ancien ID au CAMSP', blank=True)),
                ('old_cmpp_id', models.CharField(max_length=256, null=True, verbose_name='Ancien ID au CMPP', blank=True)),
                ('old_sessad_dys_id', models.CharField(max_length=256, null=True, verbose_name='Ancien ID au SESSAD TED', blank=True)),
                ('old_sessad_ted_id', models.CharField(max_length=256, null=True, verbose_name='Ancien ID au SESSAD DYS', blank=True)),
                ('services', models.ManyToManyField(to='ressources.Service', null=True, blank=True)),
                ('type', models.ForeignKey(verbose_name='Type de personnel', to='ressources.WorkerType')),
            ],
            options={
                'verbose_name': 'Personnel',
                'verbose_name_plural': 'Personnels',
            },
            bases=('personnes.people',),
        ),
        migrations.AddField(
            model_name='userworker',
            name='worker',
            field=models.ForeignKey(verbose_name='Personnel', to='personnes.Worker'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='timetable',
            name='worker',
            field=models.ForeignKey(verbose_name='Intervenant', to='personnes.Worker'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='holiday',
            name='worker',
            field=models.ForeignKey(verbose_name='Personnel', blank=True, to='personnes.Worker', null=True),
            preserve_default=True,
        ),
    ]
