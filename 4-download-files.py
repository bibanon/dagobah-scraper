#!/usr/bin/env python
# -*- coding: utf-8 -*-
# BASC Dagobah Scraper: 3-list-files.py
# Designed to obtain a total filesize of a slice of pages, and create a URL list for downloads.

# compatibility layer for print function
from __future__ import print_function

# file manipulation and download libraries
from os import path
from sys import argv
from utils import *

if __name__ == '__main__':
    # check for arguments
    if len(argv) == 3:
        first_page = int(argv[1])
        last_page = int(argv[2])
        print("Page Range: (%d - %d)" % (first_page, last_page))
        
        # display total filesize for slice
        fsize = total_fsize(first_page, last_page)
        print("Total Filesize:", "%f MB" % fsize, "or", "%f GB" % (fsize / 1000.0))
        
        # generate url list for wget to use
        mkdirs(FILE_DIR)
        list_files(first_page, last_page)
        
    else:
        print("Usage: %s <first_page> <last_page>" % argv[0])
        exit()