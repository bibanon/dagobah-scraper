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

"""Folder names"""
WORK_DIR = "dagobah"                                        # working directory
GALLERY_DIR = path.join(WORK_DIR, "gallery")   # gallery JSON directory
FILE_DIR = path.join(WORK_DIR, "flash")        # file JSON directory

# total up filesize for certain pages
def total_fsize(first_page, last_page):
    total = 0
    for p in range(first_page, last_page + 1):
        # grab a page
        page = json2object(path.join(GALLERY_DIR, '%s.json' % p))
        
        for item in page:
            total += item['size']
        
    return total

# generate a URL list for this slice
def list_files(first_page, last_page):
    fpath = path.join(FILE_DIR, 'dagobah-files_%d-%d.txt' % (first_page, last_page))
    with open(fpath, 'w') as outfile:
        for p in range(first_page, last_page + 1):
            # grab a page
            page = json2object(path.join(GALLERY_DIR, '%s.json' % p))
            
            for item in page:
                outfile.write("http://dagobah.net/flashswf/%s\n" % item['filename'])

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