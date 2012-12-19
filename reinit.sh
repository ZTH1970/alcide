#!/bin/sh

rm -f calebasse/calebasse.sqlite3
./manage.py syncdb --migrate --noinput
./manage.py loaddata calebasse/fixtures/*.json
