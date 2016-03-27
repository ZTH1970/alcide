all:
	@true

DATE=$(shell date +%Y%m%d%H%M)

DUMP=alcide-dump-$(DATE).sql.bz2
LAST_DUMP=alcide-dump-last.sql.bz2

dump:
		pg_dump -O -c | bzip2 >$(HOME)/$(DUMP)
		ln -sf $(HOME)/$(DUMP) $(HOME)/$(LAST_DUMP)

load:
	dropdb alcide
	createdb alcide
	scp aps-prod:/home/alcide/$(LAST_DUMP) .
	bzip2 -dc ./$(LAST_DUMP) | psql alcide

reload:
	dropdb alcide
	createdb alcide
	bzip2 -dc ./$(LAST_DUMP) | psql alcide
