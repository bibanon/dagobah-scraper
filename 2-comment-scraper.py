#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pyquery import PyQuery
import re
from sys import argv
from os import path
from datetime import datetime

# file manipulation and download libraries
from utils import *

"""Folder names"""
WORK_DIR = "dagobah"                                        # working directory
GALLERY_DIR = path.join(WORK_DIR, "gallery")   # gallery JSON directory

# add comments and tags to the items of the gallery
def metadator(first_page, last_page):
    pages = []
    for p in range(first_page, last_page + 1):
        print("Downloading comments for page #%d..." % p)
        
        # grab a page
        page = json2object(path.join(GALLERY_DIR, '%s.json' % p))
        
        # add comments and tags into the page
        comments2object(page)
        
        # save the data
        object2json(page, path.join(GALLERY_DIR, '%s.json' % p))
        
    return pages
    
# converts comments to a python object, and also adds all tags into gallery object 
def comments2object(gallery_page):
    """
    [
        {
            "filename": "1_wildcard.swf",
            "username": "TecDax",
            "timestamp": "2009-09-01 04:31",
            "text": "Why is this not a game?"
        }
    ]
    """
    
    for item in gallery_page:
        # grab comments page and set up pyquery on it
        COMMENTS_URL = "http://dagobah.net/flash/%s/comments" % item['filename']
        webpage = requests.get(COMMENTS_URL)
        pq = PyQuery(webpage.content)
        
        # clear thread with every item
        thread = []
        
        # fill comments dictionary
        """
        * `div.c5t_comment_list` - Contains all comments.
          * `div.c5t_comment_item` - Repeating div that contains the comment.
            * `div.c5t_comment_item_title` (optional) - Comment title.
            * `div.c5t_comment_item_text` - The body of the comment.
            * `div.c5t_comment_item_details` - `#2 - <username> - 09/01/2009 - 04:31` The order of the comment. (might be better to grab this ourselves from loop index)
              * `a.comment_name_link` (optional) - Contains the username. Can be blank.
              * date (regex) - You will need to regex the Date out of this string. Seems to be MM/DD/YYYY.
              * time (regex) - You will need to regex the Time out of the string. Seems to be HH:MM.
        """
        # grab full tags list from <div id="flashmenu">
        for div in pq('div#flashmenu').items():
            # enumerated for loop to serialize HTML into elements using the process of Positional Scraping
            for j, span in enumerate(div.find("span").items()):
                # add full tags list to gallery: strangely, they separate by `-`
                if j == 12:
                    item['tags'] = []
                    for tag in re.split(r' - ', span.text()):
                        # some items use youtube embeds as a supplement, store that
                        if re.search('^v=.+$', tag):
                            item['youtube_id'] = re.sub('^v=', '', tag)
                        else:
                            item['tags'].append(tag)

                    print(item['filename'])
                    print(item['tags'])
        
        # grab all comments
        for elements in pq('div.c5t_comment_item').items():
            comment = {}
            for div in elements.find('div').items():
                # title of the comment (optional)
                if div.hasClass('c5t_comment_item_title'):
                    comment['title'] = div.text()
                    
                if div.hasClass('c5t_comment_item_text'):
                    comment['text'] = div.text()
                    
                if div.hasClass('c5t_comment_item_details'):
                    # item: #2 - High-guy - 09/14/2013 - 15:36
                    # format: ['lolzors', '12/29/2010', '16:44']
                    # month = 1, day = 2, year = 3
                    details = re.findall(r'#\d+ -(.+)- (\d+)/(\d+)/(\d\d\d\d) - (\d\d):(\d\d)', div.text())[0]
                    
                    comment['username'] = details[0].strip()
                    
                    # convert date + time into datetime object
                    date = datetime(int(details[3]), int(details[1]), int(details[2]), int(details[4]), int(details[5]))
                    comment['date'] = str(date.date())
                    comment['time'] = str(date.time())
                    
            # add elements of comment to thread
            print(comment)
            thread.append(comment)
       
        # add comments to item element
        item['comments'] = thread
        
if __name__ == '__main__':
    # check for arguments
    if len(argv) == 3:
        first_page = int(argv[1])
        last_page = int(argv[2])
        
        metadator(first_page, last_page)
    else:
        print "Usage: %s <first_page> <last_page>" % argv[0]
        exit()