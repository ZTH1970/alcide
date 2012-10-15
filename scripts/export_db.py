#!/usr/bin/env python

import re
import os

from datetime import datetime

# Config
dbs = ["F_ST_ETIENNE_CMPP", "F_ST_ETIENNE_CAMSP", "F_ST_ETIENNE_SESSAD", "F_ST_ETIENNE_SESSAD_TED"]
tables = ["actes", "actes_non_factures", "annexes", "dossiers", "ev", "notes", "users"]
export_path = os.path.join("C:\\", "export", datetime.now().strftime("%Y%m%d-%H%M%S"))


os.mkdir(export_path)

for db in dbs:
    db_dir = os.path.join(export_path, db)
    os.mkdir(db_dir)
    for table in tables:
        os.system('sqlcmd -S SRVAPS -E -h-1 -s, -Q"SET NOCOUNT ON;' + \
                'DECLARE @colnames VARCHAR(max); ' + \
                "SELECT @colnames = COALESCE(@colnames + ',', '') " + \
                '+ column_name from %s.INFORMATION_SCHEMA.COLUMNS ' % db + \
                " where TABLE_NAME='%s'; select @colnames;\" " % table + \
                '-o "%s-title.csv"' % os.path.join(db_dir, table))
        os.system('bcp %s.dbo.%s out %s-data.csv -c -t"\\",\\"" -r "\\"\\n\\"" -T -SSRVAPS' % (db, table, os.path.join(db_dir, table)))
        title = open("%s-title.csv" % os.path.join(db_dir, table), 'r')
        data = open("%s-data.csv" % os.path.join(db_dir, table), 'r')
        res = open("%s.csv" % os.path.join(db_dir, table), "a+")
        title_content = re.sub(r'\s+$', '\n', title.readline())
        res.write(title_content)
        res.write(data.read().replace('\0', ''))
        title.close()
        data.close()
        res.close()
        os.remove("%s-title.csv" % os.path.join(db_dir, table))
        os.remove("%s-data.csv" % os.path.join(db_dir, table))


