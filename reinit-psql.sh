#!/bin/bash

DUMP='last_dump.sql.bz2'
HELP="./`basename $0` [new|dl]"

if [ $# -gt 1 ]; then
    echo $HELP
    exit 1
fi

if [ $# ]; then
    if [ "$1" != "new" -a "$1" != "dl" ]; then
        echo $HELP
        exit 1
    fi
fi

sudo -u postgres dropdb calebasse
sudo -u postgres createdb calebasse -O $USER

if [ $# ]; then
    if [ $1 = "new" ]; then
        ssh calebasse.aps42.entrouvert.com ssh prod "/etc/cron.daily/calebasse_dumpdb"
    fi
    ssh calebasse.aps42.entrouvert.com scp prod:/tmp/$DUMP .
    scp calebasse.aps42.entrouvert.com:$DUMP .
    ssh calebasse.aps42.entrouvert.com "rm /tmp/$DUMP"
fi

bzip2 -dc ./last_dump.sql.bz2 | psql calebasse
