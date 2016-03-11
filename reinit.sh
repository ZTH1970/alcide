#!/bin/sh

rm -f calebasse/calebasse.sqlite3
./manage.py migrate
./manage.py loaddata calebasse/fixtures/*.json
