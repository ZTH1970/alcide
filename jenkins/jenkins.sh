#!/bin/sh

pip install --upgrade pip pylint django-jux
pip install --upgrade -r requirements.txt
cp jenkins/local_settings.py.example local_settings.py
./manage.py syncdb --all --noinput
./manage.py migrate --fake
./manage.py validate
./manage.py test agenda dossiers actes facturation personnes ressources
(pylint -f parseable --rcfile /var/lib/jenkins/pylint.django.rc calebasse/ | tee pylint.out) || /bin/true
