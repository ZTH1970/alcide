# -*- coding: utf-8 -*-

import re
import os
import xlrd

from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand, CommandError

from calebasse.ressources.models import School, SchoolType, Service


class Command(BaseCommand):
    args = '<xls_folder>'
    help = 'Remove schools and import them from xls files'

    creche = SchoolType.objects.get(name=u'Crèche')
    maternelle = SchoolType.objects.get(name=u'Ecole maternelle')
    primaire = SchoolType.objects.get(name=u'Ecole primaire')
    college = SchoolType.objects.get(name=u'Collège')
    lycee = SchoolType.objects.get(name=u'Lycée')
    inconnu = SchoolType.objects.get(name=u'Inconnu')
    services = Service.objects.all()

    def clean_string(self, string):
        if isinstance(string, float):
            string = unicode("%d" % string)
        elif not isinstance(string, unicode):
            string = unicode(string)
        string = re.sub(r'\s+$', u'', string)
        string = re.sub(r'^\s+', u'', string)
        string = re.sub(r'\s+', u' ', string)
        string = re.sub(r'\(.*?\)', u'', string)
        return string

    def format_phone(self, number):
        num = unicode("%d" % number)
        num = unicode("0%s %s %s %s %s" % \
            (num[0], num[1:3], num[3:5], num[5:7], num[7:9]))
        return num

    def save_schools(self, schools):
        for school in schools:
            mschool = School.objects.create(**school)
            mschool.save()
            mschool.services = self.services

    def parse_xls(self, book, mapper, private=False, first_row=1):
        """ Parse an xlrd book and return a dictionnary mapped with
            ressources.models.School object
        """
        values = []
        sheet = book.sheet_by_index(0)
        for i in range(first_row, sheet.nrows - 1):
            value = {'school_type': None}
            row = sheet.row(i)
            # Name
            value['name'] = self.clean_string(row[mapper['name']].value)
            # School Type
            school_type = self.clean_string(row[mapper['school_type']].value)
            school_type = school_type.replace('.', '')
            if school_type.lower() in (u"primaire", u"elémentaire"):
                value['school_type'] = self.primaire
            elif school_type.lower() in u"maternelle":
                value['school_type'] = self.maternelle
            elif school_type.lower() in (u"lp", u"lycée", u"sep", u"lycée professionnel"):
                value['school_type'] = self.lycee
            elif school_type.lower() == u"collège":
                value['school_type'] = self.college
            else:
                print "! WARNING: school type %r unmapple" % school_type
                value['school_type'] = self.inconnu
            # Address
            value['address'] = self.clean_string(row[mapper['address']].value)
            value['address_complement'] = u""
            for j in mapper['address_complement']:
                value['address_complement'] += row[j].value + " "
            value['address_complement'] = self.clean_string(value['address_complement'])
            value['zip_code'] = self.clean_string(row[mapper['zip_code']].value)
            value['city'] = self.clean_string(row[mapper['city']].value)
            if isinstance(row[mapper['phone']].value, basestring):
                value['phone'] = self.clean_string(row[mapper['phone']].value)
                value['phone'] = value['phone'][:14]
            else:
                type(row[mapper['phone']].value)
                value['phone'] = self.format_phone(row[mapper['phone']].value)
            value['director_name'] = u""
            for j in mapper['director_name']:
                value['director_name'] += row[j].value + " "
            value['director_name'] = self.clean_string(value['director_name'])
            value['private'] = private
            if value['name']:
                values.append(value)
        return values

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError('xls_folder is mandatory')
        xls_folder = args[0]
        print "Removing all schools ..."
        School.objects.all().delete()
        # Premier degre publique
        mapper = {
                'school_type': 0,
                'city': 1,
                'name': 2,
                'address': 4,
                'zip_code': 5,
                'phone': 6,
                'director_name': [7],
                'address_complement': [],
                }
        ecoles_pub = os.path.join(xls_folder, '1d_pub_ecoles.xls')
        print "Parsing %r ..." % ecoles_pub
        book =  xlrd.open_workbook(ecoles_pub)
        schools = self.parse_xls(book, mapper)
        # Premier degre privee
        ecoles_priv = os.path.join(xls_folder, '1d_priv_ecoles.xls')
        print "Parsing %r ..." % ecoles_priv
        book = xlrd.open_workbook(ecoles_priv)
        book =  xlrd.open_workbook(ecoles_priv)
        schools += self.parse_xls(book, mapper, True, 4)

        # Second degre publique
        mapper = {
                'city': 2,
                'school_type': 3,
                'name': 4,
                'address': 5,
                'address_complement': [6, 7],
                'zip_code': 8,
                'director_name': [10, 9],
                'phone': 15,
                }
        xls = os.path.join(xls_folder, '2d_pub.xls')
        print "Parsing %r ..." % xls
        book = xlrd.open_workbook(xls)
        schools += self.parse_xls(book, mapper)
        # Second degre privee
        xls = os.path.join(xls_folder, '2d_priv.xls')
        print "Parsing %r ..." % xls
        book = xlrd.open_workbook(xls)
        schools += self.parse_xls(book, mapper, True)
    
        self.save_schools(schools)

