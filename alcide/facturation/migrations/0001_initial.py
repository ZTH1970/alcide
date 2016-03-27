# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ressources', '0001_initial'),
        ('actes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.IntegerField(null=True, blank=True)),
                ('batch', models.IntegerField(null=True, blank=True)),
                ('patient_id', models.IntegerField(null=True, blank=True)),
                ('patient_last_name', models.CharField(default=b'', max_length=128, verbose_name='Nom du patient', blank=True)),
                ('patient_first_name', models.CharField(default=b'', max_length=128, verbose_name='Pr\xe9nom(s) du patient', blank=True)),
                ('patient_social_security_id', models.CharField(default=b'', max_length=13, verbose_name='NIR', blank=True)),
                ('patient_birthdate', models.DateField(null=True, verbose_name='Date de naissance', blank=True)),
                ('patient_twinning_rank', models.IntegerField(null=True, verbose_name='Rang (g\xe9mellit\xe9)', blank=True)),
                ('patient_entry_date', models.DateField(null=True, verbose_name="Date d'entr\xe9e du patient", blank=True)),
                ('patient_exit_date', models.DateField(null=True, verbose_name='Date de sortie du patient', blank=True)),
                ('patient_other_health_center', models.CharField(default=b'', max_length=4, verbose_name='Centre sp\xe9cifique', blank=True)),
                ('policy_holder_id', models.IntegerField(null=True, blank=True)),
                ('policy_holder_last_name', models.CharField(default=b'', max_length=128, verbose_name="Nom de l'assur\xe9", blank=True)),
                ('policy_holder_first_name', models.CharField(default=b'', max_length=128, verbose_name="Pr\xe9nom(s) de l' assur\xe9", blank=True)),
                ('policy_holder_social_security_id', models.CharField(default=b'', max_length=13, verbose_name="NIR de l'assur\xe9", blank=True)),
                ('policy_holder_other_health_center', models.CharField(default=b'', max_length=4, verbose_name="Centre sp\xe9cifique de l'assur\xe9", blank=True)),
                ('policy_holder_address', models.CharField(default=b'', max_length=128, verbose_name="Adresse de l'assur\xe9", blank=True)),
                ('policy_holder_management_code', models.CharField(default=b'', max_length=10, verbose_name='Code de gestion', blank=True)),
                ('policy_holder_management_code_name', models.CharField(default=b'', max_length=256, verbose_name='Libell\xe9 du code de gestion', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Cr\xe9ation')),
                ('list_dates', models.CharField(max_length=2048, null=True, blank=True)),
                ('first_tag', models.CharField(max_length=128, null=True, blank=True)),
                ('amount', models.IntegerField()),
                ('ppa', models.IntegerField()),
                ('rejected', models.BooleanField(default=False, verbose_name='Rejet\xe9')),
                ('acts', models.ManyToManyField(to='actes.Act')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Invoicing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('seq_id', models.IntegerField(null=True, blank=True)),
                ('start_date', models.DateField(verbose_name='Ouverture de la facturation')),
                ('end_date', models.DateField(null=True, verbose_name='Cl\xf4turation de la facturation', blank=True)),
                ('status', models.CharField(default=b'open', max_length=20, verbose_name='Statut', choices=[(b'open', b'open'), (b'closed', b'closed'), (b'validated', b'validated'), (b'sent', b'sent')])),
                ('acts', models.ManyToManyField(to='actes.Act')),
                ('service', models.ForeignKey(to='ressources.Service', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='invoicing',
            unique_together=set([('seq_id', 'service')]),
        ),
        migrations.AddField(
            model_name='invoice',
            name='invoicing',
            field=models.ForeignKey(to='facturation.Invoicing', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='invoice',
            name='patient_healthcenter',
            field=models.ForeignKey(related_name='related_by_patient_invoices', verbose_name="Centre d'assurance maladie", blank=True, to='ressources.HealthCenter', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='invoice',
            name='policy_holder_healthcenter',
            field=models.ForeignKey(related_name='related_by_policy_holder_invoices', verbose_name="Centre d'assurance maladie de l'assur\xe9", blank=True, to='ressources.HealthCenter', null=True),
            preserve_default=True,
        ),
    ]
