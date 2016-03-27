#!/bin/bash

USER=$1
PASSWD=$2
DB_NAME="alcide"
DUMP='mysql_dump.sql.bz2'


HELP="./`basename $0` [user] [password]"

if [ $# -ne 2 ]; then
    echo $HELP
    exit 1
fi



mysqladmin -u$USER -p$PASSWD drop $DB_NAME 2>/dev/null
mysqladmin -u$USER -p$PASSWD create $DB_NAME

mysql -u $USER --password=$PASSWD -e "source mysql.dump.sql" $DB_NAME

