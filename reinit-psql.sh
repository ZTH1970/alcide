#!/bin/bash

DUMP='calebasse-dump-'$(date +%Y%m%d%H%M)'.sql.bz2'

sudo -u postgres dropdb calebasse
sudo -u postgres createdb calebasse -O $USER

if [ $1 == 'dl' ]; then
    ssh calebasse.aps42.entrouvert.com ssh prod "sudo -u postgres pg_dump -O calebasse | bzip2 > $DUMP"
    scp calebasse.aps42.entrouvert.com:$DUMP .
    ssh calebasse.aps42.entrouvert.com "rm $DUMP"
fi

mv $DUMP last_dump.sql.bz2

bzip2 -dc ./last_dump.sql.bz2 | psql calebasse
