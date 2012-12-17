#!/usr/bin/env python

import re
import os

from datetime import datetime

# Config
dbs = ["F_ST_ETIENNE_CMPP", "F_ST_ETIENNE_CAMSP", "F_ST_ETIENNE_SESSAD", "F_ST_ETIENNE_SESSAD_TED"]
tables = ["actes",
"actes_non_factures",
"adresses",
"annexes",
"autorite_parentale",
"avs_genre",
"b2",
"banques",
"blocage",
"caisses",
"categorie_code_nf",
"civilite",
"classes",
"code_events",
"code_nf",
"codes_gestion",
"conge",
"conges_motifs",
"contact_qui",
"contacts",
"contrat",
"convocations",
"cp",
"crm_medicaux",
"csp",
"decisions",
"departements",
"details_actes",
"details_ev",
"details_factures",
"details_rr",
"details_rs",
"diag_exter",
"discipline",
"dossiers",
"dossiers_ecoles",
"dossiers_mises",
"droits",
"ecoles",
"etablissement",
"ev",
"factures",
"fin_attente_motifs",
"fin_bilan",
"fratrie",
"genre_etab",
"genre_pc",
"grands_regimes",
"historique",
"ins_motif_exprim",
"ins_motifs",
"ins_provenance",
"intervenants",
"intervenants_etablissements",
"intervenants_exterieurs",
"maj",
"marque",
"medecins_exterieurs",
"messages",
"mises",
"nationalite",
"noemie",
"notes",
"parametres",
"parente",
"pc",
"pds",
"periodes_pc",
"pmt",
"prix_journee",
"profession",
"quartiers",
"rang",
"reglements",
"reguls",
"rejets_motifs",
"rm",
"rr",
"rs",
"save_data",
"section_educative",
"sexe",
"situation_familiale",
"sollicitation",
"sor_motifs",
"sor_orientation",
"stats",
"suivi",
"taches",
"transmission",
"transparams",
"transports",
"type_acte",
"type_acte_categorie",
"type_transport",
"users"]

export_path = os.path.join("C:\\", "export", datetime.now().strftime("%Y%m%d-%H%M%S"))


os.mkdir(export_path)

for db in dbs:
    db_dir = os.path.join(export_path, db)
    os.mkdir(db_dir)
    for table in tables:
        os.system('sqlcmd -S SRVAPS -E -h-1 -s, -Q"SET NOCOUNT ON;' + \
                ' SELECT column_name from ' + \
                '%s.INFORMATION_SCHEMA.COLUMNS ' % db + \
                " where TABLE_NAME='%s';\" " % table + \
                ' -o "%s-title.csv"' % os.path.join(db_dir, table))
        os.system('bcp %s.dbo.%s out %s-data.csv -w  -t"-!-!-EOSEP-!-!-" -T -SSRVAPS' % (db, table, os.path.join(db_dir, table)))
        title = open("%s-title.csv" % os.path.join(db_dir, table), 'r')
        data = open("%s-data.csv" % os.path.join(db_dir, table), 'r')
        res = open("%s.csv" % os.path.join(db_dir, table), "a+")
        title_content = title.read()
        title_content, nb = re.subn(r'\s+\n', ',', title_content)
        title_content = title_content[:-1] + '\n'
        res.write(title_content)
        lines = data.readlines()
        for i, line in enumerate(lines):
            if i == 0:
                line = line[2:]
            line = unicode(line, 'cp1252')
            line = line.replace('\0', '')
            line = line.replace('\r\n', '')
            line = line.replace('\n', '')
            cols = line.split("-!-!-EOSEP-!-!-")
            line = ""
            for i, col in enumerate(cols):
                col = col.replace('"', '\\"')
                if i != 0:
                    line += ',"'
                else:
                    line += '"'
                line += col + '"'
            line += "\n"
            res.write(line.encode('utf-8'))
        title.close()
        data.close()
        res.close()
        os.remove("%s-title.csv" % os.path.join(db_dir, table))
        os.remove("%s-data.csv" % os.path.join(db_dir, table))


