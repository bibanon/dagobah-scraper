#!/usr/bin/env python
# -*- coding: utf-8 -*-
# BASC Dagobah Scraper: 1-gallery-scraper.py
# Designed to obtain all metadata from Dagobah's paginated gallery.

from pyquery import PyQuery
import lxml
import re
import requests
from sys import argv
from os import path
from datetime import datetime

# file manipulation and download libraries
from utils import *

"""Folder names"""
WORK_DIR = "dagobah"                                        # working directory
GALLERY_DIR = path.join(WORK_DIR, "gallery")   # gallery JSON directory

# grab multiple pages of the gallery, between bounds set by argument
# Gallery object is a list (gallery) of lists (pages), which contain dictionaries (items)
def paginator(first_page, last_page):
    pages = []
    for p in range(first_page, last_page + 1):
        print("Downloading page #%d..." % p)
        
        # URL format for gallery sorted alphabetically is http://dagobah.net/?page=<PAGE_NUM>&o=n&d=i
        BASE_GALLERY_URL = "http://dagobah.net"
        payload = {'page': p, 'o': 'n', 'd': 'i'}
        webpage = requests.get(BASE_GALLERY_URL, params=payload)
        page = gallery2object(webpage.content)
        
        # save the data to folder in #.json
        object2json(page, path.join(GALLERY_DIR, '%s.json' % p))
        pages.append(page)
        
    return pages

def gallery2object(html_doc):
    """
        // example JSON object:
        [
            {
                "filename": "4chan_vs_reddit.swf",
                "id": "f14075",
                "title": "4chan vs reddit",
                "tags": [
                    'Misc', 
                    'rule_no_1'
                ]
                "rating": 3.7,
                "raters": 26,
                "views": 1754,
                "commentamt": 8,
                "comments": [],
                "size": "9.8",  // always in MB, KB represented in decimal
                "date": "2015-05-22",
                "youtubeid": ""
            }
        ]
    """
    pq = PyQuery(html_doc)
    
    # grab all <a class="flash"> items
    flashlist = []
    for a in pq('a.flash').items():
        item = {}
        item['filename'] = re.sub('/flash/', '', a.attr['href'])
        item['id'] = a.attr['id']
        
        # enumerated for loop to serialize HTML into elements using the process of Positional Scraping
        for i, span in enumerate(a.find("span").items()):
            # index 0: flashname
            if span.hasClass("flashname"):
                item['title'] = span.text()
            
            # index 3+4: rating
            if i == 4:
                item['rating'] = float(span.text())
            
            # index 5: # of raters
            if span.hasClass("amount"):
                # remove parentheses
                item['raters'] = int(re.sub(r'[()]', '', span.text()))
                
            # index 6+7: # of views
            if i == 7:
                item['views'] = int(span.text())
                
            # index 8+9: # of comments
            if i == 9:
                item['comment_amt'] = int(span.text())
                
            # index 10+11: filesize
            if i == 11:
                raw_size = span.text()
                
                # convert to megabytes for float representation
                if (re.search(' [Kk][Bb]', raw_size)):   # kilobytes
                    size = float(re.sub(' [Kk][Bb]', '', raw_size)) / 1000.0
                elif (re.search(' [Mb][Bb]', raw_size)): # megabytes: just strip MB
                    size = float(re.sub(' [Mm][Bb]', '', raw_size))
                elif (re.search(' [Bb]', raw_size)):     # bytes: convert to MB
                    size = float(re.sub(' [Bb]', '', raw_size)) / 1000.0 / 1000.0
                else: # no known size: perhaps for youtube videos
                    size = 0
                
                item['size'] = size
                
            # index 12+13: date
            if i == 13:
                # date format is DD.MM.YYYY, which is weird. Convert to YYYY-MM-DD datetime object
                date_raw = [int(tag) for tag in span.text().split('.')]
                date = datetime(date_raw[2], date_raw[1], date_raw[0])
                item['date'] = str(date.date())
                
            # placeholder for comments and tags
            item['comments'] = []
            item['tags'] = []
            item['youtube_id'] = ""
                
        flashlist.append(item)
                
    return flashlist

def gallery2sql(gallery):
    # write gallery object to SQLite database
    pass

if __name__ == '__main__':
    # check for arguments
    if len(argv) == 3:
        first_page = int(argv[1])
        last_page = int(argv[2])
        
        # make sure path exists
        mkdirs(GALLERY_DIR)
        
        # grab a gallery page 
        gallery = paginator(first_page, last_page)
    else:
        print("Usage: %s <first_page> <last_page>" % argv[0])
        exit()