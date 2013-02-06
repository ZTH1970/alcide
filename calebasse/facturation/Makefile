CAPATH=/var/lib/calebasse/gip-cps.capath/

capath:
	mkdir -p $(CAPATH)
	python build_capath.py $(CAPATH)
	c_rehash $(CAPATH)

