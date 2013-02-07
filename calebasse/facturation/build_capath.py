#!/usr/bin/env python

import sys
from transmission_utils import CAPATH, build_capath

if __name__ == '__main__':
    print "get capath certificates in", CAPATH
    build_capath(CAPATH)

