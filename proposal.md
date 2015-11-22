## The Depaginator

The proposed **BASC Depaginator** will be an all purpose, fully configurable tool for archiving paginated image/file galleries. 

These sites do not lend themselves well to archival with a brute-force scraper, since they often end up falling into infinite loops, or fail to grab everything, often ending up with piles of useless data.

In addition, they often rely on complex display systems that were made to be easy for humans to use, but create horrific spaghetti code for any robot to parse through. Finally, these robots add significant strain to the server.

The Depaginator has several tasks:

1. Create a SQLite database with a schema that fits the task of storing and reporting the metadata we want.
2. Parse the paginated galleries one page at a time. This will usually lead you to a URL of the image/file viewer (which can be stored in the database), though sometimes you may be lucky enough to get some extra metadata.
  * Store the URLs in the database along with the filename as the primary key.
3. Grab all URLs from the database and access each image/file viewer page. From here, grab as much metadata as possible, grab a link to the actual image, and store it in the database.
  * For items such as tags or categories, a separate linking table with a one to many relationship from tag to file may be necessary.
4. Download all images from the website. It might be helpful to generate a txt dump of all file URLs, so they can be grabbed using Wget or grab-site.

### Database Manager

This time, this is a good chance to learn some SQLAlchemy. It's the better way to work with SQL.

### Gallery Parser

This parser generates a list of all files in the gallery. Generally, it grabs a certain amount of image URLs from one page, then jumps to the next page and grabs again, and so on. 

The user sets the total amount of pages in the site. If the site doesn't tell you, you'll have to figure it out by going to the final page possible.

On Dagobah, the format is as follows for page 3: `http://dagobah.net/?page=3&o=n&d=i`

### Image Nabber

In this step, we actually go into the Image View URLs in question and extract any metadata from there, especially the actual Image URLs.

You could also download images in this set in this step, but it is better to grab all the URLs and metadata first here.

### Comment Scraper

Thankfully, Dagobah has a simple URL scheme where every single image at `http://dagobah.net/flash/404.swf` has a comments section at `http://dagobah.net/flash/404.swf/comments`.

Thus, we can create a `comments` table with a foreign key `filename` that links each comment to the record in the `files` table.

### Export to JSON or TXT

The final step is to export all image URLs to TXT, or a JSON file which can have the Image/File Viewer URLs as well. This makes it possible to use an external tool such as `wget` for the images, or grab-site, which creates WARCs.

### Scraper

Alternatively, we could make a specific downloader which will handle the scraping. This makes it possible to set certain ranges to download, to spread the archival workload across machines for parallel scraping and diversity in IP ranges.

