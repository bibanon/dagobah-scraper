Dagobah is a large archive of ancient 4chan flash animations, dating all the way back to 2008 when the site was first founded. Anyone can upload files to this site.

Because of it's 45,175+ image collection containing flash animations that date from 4chan's earliest history, the Bibliotheca Anonoma is conducting a contingency archival of the site.

We will use custom built Python scraping scripts to reduce strain on the server, and avoid the many pitfalls encountered by scraping an automatically generated database view.

## Using this Scraper

PyQuery currently works best on Python2, so use python2 for all installation.

First, install all dependencies:

	sudo pip install pyquery lxml

Then, run the following scripts, one by one, to dump Dagobah's entire collection, as well as all tags:

1. Grab all the pages from dagobah's gallery. The first argument is the page to start from, and the second argument is the page to stop at.

		python 1-gallery-scraper.py 1 262

2. The next step is to grab all comments and tags for each item. This can take a few hours: if you lose connection, continue where you left off: change the start page to the last one you've edited.

		python 2-comment-scraper.py 1 262

3. Finally, we need to download the flash files themselves. This script will obtain the filenames and scrape the flash files. If you lose connection, continue where you left off: change the start page to the last one you've edited.

        python 3-download-items.py 1 262

Everything is stored under `dagobah`, from the JSON gallery page dumps in `gallery/` to the `images/` folder. All images are sorted into folders named by their first two characters (to reduce strain on file explorers).

You can use this exported data to create your own web viewable Macrochan! Though please, make a real API with generated JSON, so we won't have to go through this horrifying export process again.