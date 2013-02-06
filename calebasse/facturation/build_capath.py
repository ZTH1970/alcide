#!/usr/bin/env python

import sys
from transmission_utils import build_capath

if __name__ == '__main__':
    if len(sys.argv) == 2:
        capath = sys.argv[1]
    else:
        print >> sys.stderr, "syntax: build_capath.py /ca/path"
        sys.exit(1)
    print "get capath certificates in", capath
    build_capath(capath)

