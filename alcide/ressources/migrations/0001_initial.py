# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import alcide.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ActType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='Nom')),
                ('billable', models.BooleanField(default=True, verbose_name='Facturable')),
                ('old_id', models.CharField(max_length=256, null=True, verbose_name='Ancien ID', blank=True)),
                ('display_first', models.BooleanField(default=False, verbose_name='Acte principalement utilis\xe9')),
                ('group', models.BooleanField(default=False, verbose_name='En groupe')),
            ],
            options={
                'ordering': ('-display_first', 'name'),
                'abstract': False,
                'verbose_name': "Type d'actes",
                'verbose_name_plural': "Types d'actes",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AdviceGiver',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='Nom')),
            ],
            options={
                'verbose_name': 'Demandeur',
                'verbose_name_plural': 'Demandeurs',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AnalyseMotive',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='Nom')),
            ],
            options={
                'verbose_name': 'Motif analys\xe9',
                'verbose_name_plural': 'Motifs analys\xe9s',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CodeCFTMEA',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='Nom')),
                ('code', models.IntegerField(verbose_name='Code')),
                ('axe', models.IntegerField(max_length=1, verbose_name='Axe', choices=[(1, b'Axe I : cat\xc3\xa9gories cliniques'), (2, b'Axe II : facteurs organiques'), (3, b'Axe II : facteurs environnementaux')])),
                ('ordering_code', models.CharField(max_length=20, null=True, verbose_name='Classification', blank=True)),
            ],
            options={
                'ordering': ['ordering_code'],
                'verbose_name': 'Code CFTMEA',
                'verbose_name_plural': 'Codes CFTMEA',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FamilyMotive',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='Nom')),
            ],
            options={
                'verbose_name': 'Motif familiale',
                'verbose_name_plural': 'Motifs familiaux',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FamilySituationType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='Nom')),
            ],
            options={
                'verbose_name': 'Type de situation familiale',
                'verbose_name_plural': 'Types de situations familiales',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HealthCenter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='Nom')),
                ('code', models.CharField(max_length=4, null=True, verbose_name='Code du centre', blank=True)),
                ('dest_organism', models.CharField(max_length=8, verbose_name='Organisme destinataire')),
                ('computer_center_code', models.CharField(default=True, max_length=8, null=True, verbose_name='Code centre informatique')),
                ('abbreviation', models.CharField(default=True, max_length=8, null=True, verbose_name='Abbr\xe9vation')),
                ('health_fund', models.CharField(max_length=3, verbose_name='Num\xe9ro de la caisse')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
                ('address', models.CharField(max_length=120, verbose_name='Adresse')),
                ('address_complement', models.CharField(default=None, max_length=120, null=True, verbose_name='Adresse compl\xe9mentaire', blank=True)),
                ('zip_code', models.CharField(max_length=8, verbose_name='Code postal')),
                ('city', models.CharField(max_length=80, verbose_name='Ville')),
                ('phone', models.CharField(max_length=30, verbose_name='T\xe9l\xe9phone')),
                ('fax', models.CharField(max_length=30, null=True, verbose_name='Fax', blank=True)),
                ('email', models.EmailField(max_length=75, null=True, verbose_name='Courriel', blank=True)),
                ('accounting_number', models.CharField(max_length=30, null=True, verbose_name='Num\xe9ro de compte', blank=True)),
                ('correspondant', models.CharField(max_length=80, verbose_name='Correspondant')),
                ('hc_invoice', models.ForeignKey(default=None, blank=True, to='ressources.HealthCenter', null=True, verbose_name='Centre pour facturation (optionnel)')),
            ],
            options={
                'verbose_name': "Centre d'assurance maladie",
                'verbose_name_plural': "Centres d'assurances maladie",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HolidayType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='Nom')),
                ('for_group', models.BooleanField(default=True, verbose_name='Absence de groupe')),
            ],
            options={
                'verbose_name': "Type d'absence",
                'verbose_name_plural': "Types d'absence",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InscriptionMotive',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='Nom')),
            ],
            options={
                'verbose_name': "Motif d'inscription",
                'verbose_name_plural': "Motifs d'inscription",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='Nom')),
            ],
            options={
                'verbose_name': 'Profession',
                'verbose_name_plural': 'Professions',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LargeRegime',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='Nom')),
                ('code', models.CharField(max_length=2, verbose_name='Code grand r\xe9gime')),
            ],
            options={
                'verbose_name': 'Grand r\xe9gime',
                'verbose_name_plural': 'Grands r\xe9gimes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ManagementCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='Nom')),
                ('code', models.CharField(max_length=10, verbose_name='Code')),
                ('old_id', models.CharField(max_length=256, null=True, verbose_name='Ancien ID', blank=True)),
            ],
            options={
                'verbose_name': 'Code de gestion',
                'verbose_name_plural': 'Codes de gestion',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MaritalStatusType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='Nom')),
            ],
            options={
                'verbose_name': 'R\xe9gime matrimonial',
                'verbose_name_plural': 'R\xe9gimes matrimoniaux',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MDPH',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('department', models.CharField(max_length=200, verbose_name='D\xe9partement')),
                ('description', models.TextField(null=True, blank=True)),
                ('phone', alcide.models.PhoneNumberField(max_length=20, null=True, verbose_name='T\xe9l\xe9phone', blank=True)),
                ('fax', alcide.models.PhoneNumberField(max_length=20, null=True, verbose_name='Fax', blank=True)),
                ('email', models.EmailField(max_length=75, null=True, blank=True)),
                ('website', models.CharField(max_length=200, null=True, verbose_name='Site Web', blank=True)),
                ('address', models.CharField(max_length=120, null=True, verbose_name='Adresse', blank=True)),
                ('address_complement', models.CharField(default=None, max_length=120, null=True, verbose_name="Compl\xe9ment d'addresse", blank=True)),
                ('zip_code', alcide.models.ZipCodeField(max_length=5, null=True, verbose_name='Code postal', blank=True)),
                ('city', models.CharField(max_length=80, null=True, verbose_name='Ville', blank=True)),
            ],
            options={
                'verbose_name': 'Etablissement MDPH',
                'verbose_name_plural': 'Etablissements MDPH',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MDPHRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateField(verbose_name='Date de la demande')),
                ('comment', models.TextField(max_length=3000, null=True, verbose_name='Commentaire', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Cr\xe9ation')),
                ('mdph', models.ForeignKey(verbose_name='MDPH', to='ressources.MDPH')),
            ],
            options={
                'verbose_name': 'Demande MDPH',
                'verbose_name_plural': 'Demandes MDPH',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MDPHResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateField(verbose_name='Date de d\xe9but')),
                ('end_date', models.DateField(verbose_name='Date de fin')),
                ('comment', models.TextField(max_length=3000, null=True, verbose_name='Commentaire', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Cr\xe9ation')),
                ('type_aide', models.IntegerField(default=0, max_length=1, verbose_name="Type d'aide", choices=[(0, b'Non d\xc3\xa9fini'), (1, b"AEEH (Allocation d'\xc3\xa9ducation de l'enfant handicap\xc3\xa9)"), (2, b'AVS (Assistant de vie scolaire)'), (3, b'EVS (Emplois de vie scolaire)')])),
                ('name', models.CharField(max_length=200, null=True, verbose_name='Nom', blank=True)),
                ('rate', models.CharField(max_length=10, null=True, verbose_name='Taux', blank=True)),
                ('mdph', models.ForeignKey(verbose_name='MDPH', to='ressources.MDPH')),
            ],
            options={
                'verbose_name': 'R\xe9ponse MDPH',
                'verbose_name_plural': 'R\xe9ponses MDPH',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Nationality',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='Nom')),
            ],
            options={
                'verbose_name': 'Nationalit\xe9',
                'verbose_name_plural': 'Nationalit\xe9s',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Office',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='Nom')),
                ('description', models.TextField(null=True, blank=True)),
                ('phone', alcide.models.PhoneNumberField(max_length=20, null=True, verbose_name='T\xe9l\xe9phone', blank=True)),
                ('fax', alcide.models.PhoneNumberField(max_length=20, null=True, verbose_name='Fax', blank=True)),
                ('email', models.EmailField(max_length=75, null=True, blank=True)),
                ('address', models.CharField(default=None, max_length=120, null=True, verbose_name='Adresse', blank=True)),
                ('address_complement', models.CharField(default=None, max_length=120, null=True, verbose_name="Compl\xe9ment d'adresse", blank=True)),
                ('zip_code', alcide.models.ZipCodeField(default=None, max_length=5, null=True, verbose_name='Code postal', blank=True)),
                ('city', models.CharField(default=None, max_length=80, null=True, verbose_name='Ville', blank=True)),
            ],
            options={
                'verbose_name': '\xc9tablissement',
                'verbose_name_plural': '\xc9tablissements',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OutMotive',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='Nom')),
            ],
            options={
                'verbose_name': 'Motif de sortie',
                'verbose_name_plural': 'Motifs de sortie',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OutTo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='Nom')),
            ],
            options={
                'verbose_name': 'Orientation de sortie',
                'verbose_name_plural': 'Orientations de sortie',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ParentalAuthorityType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='Nom')),
            ],
            options={
                'verbose_name': "Type d'autorit\xe9 parentale",
                'verbose_name_plural': "Types d'autorit\xe9s parentales",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ParentalCustodyType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='Nom')),
            ],
            options={
                'verbose_name': 'Type de gardes parentales',
                'verbose_name_plural': 'Types de gardes parentales',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PatientRelatedLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='Nom')),
                ('old_camsp_id', models.CharField(max_length=256, null=True, verbose_name='Ancien ID au CAMSP', blank=True)),
                ('old_cmpp_id', models.CharField(max_length=256, null=True, verbose_name='Ancien ID au CMPP', blank=True)),
                ('old_sessad_dys_id', models.CharField(max_length=256, null=True, verbose_name='Ancien ID au SESSAD TED', blank=True)),
                ('old_sessad_ted_id', models.CharField(max_length=256, null=True, verbose_name='Ancien ID au SESSAD DYS', blank=True)),
            ],
            options={
                'verbose_name': 'Type de lien avec le patient (parent\xe9)',
                'verbose_name_plural': 'Types de lien avec le patient (parent\xe9)',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PricePerAct',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('price', models.DecimalField(verbose_name='Tarif', max_digits=5, decimal_places=2)),
                ('start_date', models.DateField(verbose_name="Prise d'effet")),
            ],
            options={
                'verbose_name': "Tarif horaire de l'acte",
                'verbose_name_plural': "Tarifs horaires de l'acte",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Provenance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='Nom')),
                ('old_id', models.CharField(max_length=256, null=True, verbose_name='Ancien ID', blank=True)),
                ('old_service', models.CharField(max_length=256, null=True, verbose_name='Ancien Service', blank=True)),
            ],
            options={
                'verbose_name': 'Conseilleur',
                'verbose_name_plural': 'Conseilleurs',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProvenancePlace',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='Nom')),
            ],
            options={
                'verbose_name': 'Lieu de provenance',
                'verbose_name_plural': 'Lieux de provenance',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Ressource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='Nom')),
                ('etablissement', models.ForeignKey(to='ressources.Office')),
            ],
            options={
                'verbose_name': 'Ressource',
                'verbose_name_plural': 'Ressources',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='Nom')),
                ('display_name', models.CharField(default=b'', max_length=256, null=True, blank=True)),
                ('description', models.TextField(default=None, null=True, blank=True)),
                ('address', models.CharField(default=None, max_length=120, null=True, verbose_name='Adresse', blank=True)),
                ('address_complement', models.CharField(default=None, max_length=120, null=True, verbose_name="Compl\xe9ment d'adresse", blank=True)),
                ('zip_code', alcide.models.ZipCodeField(default=None, max_length=5, null=True, verbose_name='Code postal', blank=True)),
                ('city', models.CharField(default=None, max_length=80, null=True, verbose_name='Ville', blank=True)),
                ('phone', alcide.models.PhoneNumberField(default=None, max_length=20, null=True, verbose_name='T\xe9l\xe9phone', blank=True)),
                ('fax', models.CharField(default=None, max_length=30, null=True, blank=True)),
                ('email', models.EmailField(default=None, max_length=75, null=True, blank=True)),
                ('director_name', models.CharField(default=None, max_length=70, null=True, verbose_name='Nom du directeur', blank=True)),
                ('old_id', models.CharField(max_length=256, null=True, verbose_name='Ancien ID', blank=True)),
                ('old_service', models.CharField(max_length=256, null=True, verbose_name='Ancien Service', blank=True)),
                ('private', models.BooleanField(default=False, verbose_name='Priv\xe9')),
            ],
            options={
                'verbose_name': 'Lieu de socialisation',
                'verbose_name_plural': 'Lieux de socialisation',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SchoolLevel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='Nom')),
                ('old_id', models.CharField(max_length=256, null=True, verbose_name='Ancien ID', blank=True)),
                ('old_service', models.CharField(max_length=256, null=True, verbose_name='Ancien Service', blank=True)),
            ],
            options={
                'verbose_name': 'Classe',
                'verbose_name_plural': 'Classes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SchoolTeacherRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='Nom')),
            ],
            options={
                'verbose_name': 'Type de r\xf4le des professeurs',
                'verbose_name_plural': 'Types de r\xf4le des professeurs',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SchoolType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='Nom')),
            ],
            options={
                'verbose_name': 'Type du lieu de socialisation',
                'verbose_name_plural': 'Types du lieu de socialisation',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='Nom')),
                ('slug', models.SlugField()),
                ('description', models.TextField()),
                ('phone', alcide.models.PhoneNumberField(max_length=20, verbose_name='T\xe9l\xe9phone')),
                ('fax', alcide.models.PhoneNumberField(max_length=20, verbose_name='Fax')),
                ('email', models.EmailField(max_length=75)),
            ],
            options={
                'verbose_name': 'Service',
                'verbose_name_plural': 'Services',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SessionType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='Nom')),
            ],
            options={
                'verbose_name': 'Type de s\xe9ance',
                'verbose_name_plural': 'Types de s\xe9ances',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SocialisationDuration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('redoublement', models.BooleanField(default=False, verbose_name='Redoublement')),
                ('start_date', models.DateField(verbose_name="Date d'arriv\xe9e")),
                ('contact', models.CharField(default=None, max_length=200, null=True, verbose_name='Contact', blank=True)),
                ('end_date', models.DateField(null=True, verbose_name='Date de d\xe9part', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Cr\xe9ation')),
                ('comment', models.TextField(max_length=3000, null=True, verbose_name='Commentaire', blank=True)),
                ('level', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='Classe', blank=True, to='ressources.SchoolLevel', null=True)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='Lieu de socialisation', blank=True, to='ressources.School', null=True)),
            ],
            options={
                'verbose_name': 'P\xe9riode de socialisation',
                'verbose_name_plural': 'P\xe9riodes de socialisation',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TransportCompany',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='Nom')),
                ('description', models.TextField(default=None, null=True, blank=True)),
                ('address', models.CharField(default=None, max_length=120, null=True, verbose_name='Adresse', blank=True)),
                ('address_complement', models.CharField(default=None, max_length=120, null=True, verbose_name="Compl\xe9ment d'adresse", blank=True)),
                ('zip_code', alcide.models.ZipCodeField(default=None, max_length=5, null=True, verbose_name='Code postal', blank=True)),
                ('city', models.CharField(default=None, max_length=80, null=True, verbose_name='Ville', blank=True)),
                ('phone', alcide.models.PhoneNumberField(default=None, max_length=20, null=True, verbose_name='T\xe9l\xe9phone', blank=True)),
                ('fax', models.CharField(default=None, max_length=30, null=True, blank=True)),
                ('email', models.EmailField(max_length=75, null=True, blank=True)),
                ('correspondant', models.CharField(max_length=80, null=True, blank=True)),
                ('old_camsp_id', models.CharField(max_length=256, null=True, verbose_name='Ancien ID au CAMSP', blank=True)),
                ('old_cmpp_id', models.CharField(max_length=256, null=True, verbose_name='Ancien ID au CMPP', blank=True)),
                ('old_sessad_dys_id', models.CharField(max_length=256, null=True, verbose_name='Ancien ID au SESSAD TED', blank=True)),
                ('old_sessad_ted_id', models.CharField(max_length=256, null=True, verbose_name='Ancien ID au SESSAD DYS', blank=True)),
            ],
            options={
                'verbose_name': 'Compagnie de transport',
                'verbose_name_plural': 'Compagnies de transport',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TransportType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='Nom')),
            ],
            options={
                'verbose_name': 'Type de transport',
                'verbose_name_plural': 'Types de transports',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UninvoicableCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'Code de non-facturation',
                'verbose_name_plural': 'Codes de non-facturation',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WorkerType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='Nom')),
                ('intervene', models.BooleanField(default=True, verbose_name='Intervenant')),
            ],
            options={
                'verbose_name': 'Type de personnel',
                'verbose_name_plural': 'Types de personnel',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='schooltype',
            name='services',
            field=models.ManyToManyField(to='ressources.Service'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='school',
            name='school_type',
            field=models.ForeignKey(verbose_name="Type d'\xe9tablissement", to='ressources.SchoolType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='school',
            name='services',
            field=models.ManyToManyField(to='ressources.Service', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='healthcenter',
            name='large_regime',
            field=models.ForeignKey(verbose_name='Grand r\xe9gime', to='ressources.LargeRegime'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='acttype',
            name='service',
            field=models.ForeignKey(blank=True, to='ressources.Service', null=True),
            preserve_default=True,
        ),
    ]
