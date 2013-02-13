all:
	@true

DATE=$(shell date +%Y%m%d%H%M)

DUMP=calebasse-dump-$(DATE).sql.bz2
LAST_DUMP=calebasse-dump-last.sql.bz2

dump:
		pg_dump -O -c | bzip2 >$(HOME)/$(DUMP)
		ln -sf $(HOME)/$(DUMP) $(HOME)/$(LAST_DUMP)

load:
	dropdb calebasse
	createdb calebasse
	scp aps-prod:/home/calebasse/$(LAST_DUMP) .
	bzip2 -dc ./$(LAST_DUMP) | psql calebasse

reload:
	dropdb calebasse
	createdb calebasse
	bzip2 -dc ./$(LAST_DUMP) | psql calebasse
