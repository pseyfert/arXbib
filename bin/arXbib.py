#!/usr/bin/env python

from arxbib import arXbib
import sys

if __name__ == "__main__":
    arxbib = arXbib()
    arxbib.main(sys.argv[1:])
