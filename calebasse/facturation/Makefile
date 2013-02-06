CAPATH=/var/lib/calebasse/gie-cps.capath/

capath:
	mkdir -p $(CAPATH)
	python ./transmission_utils.py $(CAPATH)
	c_rehash $(CAPATH)

