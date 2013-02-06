CAPATH=/var/lib/calebasse/gip-cps.capath/

capath:
	mkdir -p $(CAPATH)
	python ./transmission_utils.py $(CAPATH)
	c_rehash $(CAPATH)

