Dagobah is a major Flash site in 4chan's history that retains many of the Flash swfs made by /f/ from 2008 to today.

While it seems lively now, it could have issues in the future. 

I'm putting together this scraper to grab any kind of paginated gallery and scrape the tags into a database.

Dagobah Scraping Process
------------------------

The scraping progress for Dagobah ended up being pretty involved, but it was worth the effort to archive all metadata and tags.

### Gallery Parsing

Parsing the gallery item is harder, because the items are separated by `<br></br>`, so index based scraping will have to be used instead.

All of these can be found under `<div id="flashlist">`.

```
<a href="/flash/3_anime_songs.swf" id="f10166" class="flash">
    <img src="/t100/3_anime_songs.jpg" class="flashthumbLARGE" alt="F">
    <span class="flashname">3 anime songs</span>
    <span class="description">tags:</span>
    <span class="value"> Loop, anime, epilepsy</span>
<br>
    <span class="rating">rating:</span>
    <span class="value"> 2.5 </span>
    <span class="amount"> (34)</span>
<br>
    <span class="views">views:</span>
    <span class="value"> 4729</span>
<br>
    <span class="rating" onmouseover="">comments:<span class="value"> 4 </span></span>
<br>
    <span class="size">size:</span>
    <span class="value"> 1.3 MB</span>
<br>
    <span class="date">date:</span>
    <span class="value"> 26.01.2012</span>
</a>
```

If you forget to grab it from the gallery but have all the filenames, you can also grab it from comments as well.

### Positional Scraping

The technique I use to serialize this poorly designed list is Positional Scraping. This processes the list of elements in an item based solely on it's index in the list. 

Since we know that a robot and not a human generated this list, it always has a pattern. Thankfully, the size and format of this list doesn't change, so we don't need to do crazy heuteristics based on amount of elements.

In the gallery view above, the links are encapsulated by a `<div id="flashlist"><div>`, which is easy to grab with pyquery's `div#flashlist`. 

But a better method to grab the elements of the flashlist is to find only links that match `a.flash` (`flash` class attribute) inside the `div`.

Now, we get to Positional Scraping. Using PyQuery, I selected all `a.flash` links, and filtered out all `span.value` tags so I could see the bare element titles. I used an enumerated `for` loop to index all displayed elements.

```
[0] <span class="flashname">4chan vs reddit</span>
[1] <span class="description">tags:</span>
[3] <span class="rating">rating:</span>
[5] <span class="amount"> (26)</span>
[6] <span class="views">views:</span>
[10] <span class="size">size:</span>
[12] <span class="date">date:</span>
```

From here, we can tell that index 0 and index 5 have the value in the element title. For the others, index 2 corresponds to `description` (actually, tags), index 3 corresponds to `rating`, index 6 corresponds to `views`, and so on.

The `span` tags at those indicies should contain the values corresponding to the preceding element. Thus, we just grab that element and display it's text contents. 

That data can also be processed before displaying. For example, the string of comma separated tags is converted into a Python list using [list comprehension.](http://stackoverflow.com/a/4071407) We also converted the date to ISO format.

```
# index 3+4: rating
if i == 4:
    print("rating: %s" % span.text())
    
# index 10+11: filesize
if i == 11:
    print("size: %s" % span.text())
    
# index 12+13: date
if i == 13:
    # date format is DD.MM.YYYY, which is weird. Convert to YYYY-MM-DD datetime object
    date_raw = [int(tag) for tag in span.text().split('.')]
    date = datetime(date_raw[2], date_raw[1], date_raw[0])
    print("date: %s" % date.date())
```

For index 0 and 5 that have the value in the element title, we can just match the corresponding span tags directly. Some text processing with a bit of regex can be useful to remove unnecessary elements (such as parentheses).

```
# index 0: flashname
if span.hasClass("flashname"):
    print("title: %s" % span.text())

# index 5: amount
if span.hasClass("amount"):
    # remove parentheses
    print("amount: %s" % re.sub(r'[()]', '', span.text()))
```

Notice that some `span.value` tags actually contain hidden elements in the gap between index 6-10: comments.

```
# index 6+7: # of views
if i == 7:
    print("views: %s" % span.text())

# index 8+9: # of comments
if i == 9:
    print("comments: %s" % span.text())
```

The last thing to watch out for is tags. Although tags are displayed on the gallery view, only at most two tags are shown, and the third tag is truncated if it is long.

So while we could grab the tags from the gallery, we're better off skipping it now and grabbing it from the comments page.

```
# index 1+2: tags
if i == 2:
    # extract tags using list comprehension: http://stackoverflow.com/a/4071407
    tags = [tag.strip() for tag in span.text().split(',')]
    print("tags: %s" % tags)
```

Finally, to serialize the data for programs to use: instead of printing the data, we simply store it in a dictionary.

## Comment Page Parsing

Each file has a Comment Page, which contains an infobox with all full tags associated with the item (contained in `div#flashmenu` just like the gallery), and comments of course.

* `div.c5t_comment_list` - Contains all comments.
  * `div.c5t_comment_item` - Repeating div that contains the comment.
    * `div.c5t_comment_item_title` (optional) - Comment title.
    * `div.c5t_comment_item_text` - The body of the comment.
    * `div.c5t_comment_item_details` - `#2 - <username> - 09/01/2009 - 04:31` The order of the comment. (might be better to grab this ourselves from loop index)
      * `a.comment_name_link` (optional) - Contains the username. Can be blank.
      * date (regex) - You will need to regex the Date out of this string. Seems to be MM/DD/YYYY.
      * time (regex) - You will need to regex the Time out of the string. Seems to be HH:MM.

### Pesky Details Regex

One of the frustrations I faced was that `div.c5t_comment_item_details` was a ` - ` delimited string, not a set of solid HTML tags. This makes it difficult to parse as any CSV.

There were two strings that screwed with `.strip('-')`, which I used with list comprehension to create a list effectively.

The first string that caused problems was this one. I first resolved to simply use a `.string('[ ]*-[ ]*')`, but that led only to the next issue:

`#1 - - 09/14/2013 - 10:03`

Another string that causes problems is the case where the username contains a dash. This confuses the list generator and and causes `guy` to be parsed as the date.

`#2 - High-guy - 09/14/2013 - 15:36`

In the end, I decided to abandon using `.strip('-')`, and use a complete sentence regex with multiple matches. To deal with the case of no username (where there is only one space there instead: `- -`), and then strip the whitespace afterwards.

`#\d+ -(.+)- (\d+)/(\d+)/(\d\d\d\d) - (\d\d):(\d\d)`

![Pythex - Regex for details](http://i.imgur.com/D2D9HW3.png)

### Flashlist Parsing (for Tags)

The Comment page has a more complete tag list, so we will use that with Pagination Scraping. As show in the index map below, the `tags` list should be in the 12th `span` tag.

```
[0]: Rating:
[2]: (51)
[3]: hits:
[5]: size:
[7]: posted:
[9]: approved by:
[11]: tags:
```

Dagobah Table/JSON Schemas
--------------------------

This is a description of the data formats we used in the metadata dumps.

### JSON Schema

In the end, we elected to store each page in a JSON file, to make it more human readable, continuable, and parsable far into the future. Comments/Tags are added in the second run.

We can convert it to a SQL database after all data gets scraped.


```
[
    {
        "comment_amt": 3,
        "comments": [
            {
                "date": "2015-07-28",
                "text": "What is this song?",
                "time": "07:26:00",
                "title": "",
                "username": "Sotishima"
            },
            {
                "date": "2015-07-28",
                "text": "my ears hurt :[",
                "time": "15:50:00",
                "title": "",
                "username": "lakithunder562"
            },
            {
                "date": "2015-07-30",
                "text": "this is amazing, source?",
                "time": "16:39:00",
                "title": "",
                "username": "Name"
            }
        ],
        "date": "2015-07-27",
        "filename": "anon_partyhard174.swf",
        "id": "f14237",
        "raters": 26,
        "rating": 1.9,
        "size": 4.9,
        "tags": [
            "Loop",
            "NSFW"
        ],
        "title": "anon partyhard174",
        "views": 1666,
        "youtube_id": ""
    }
]
```

### URL Schema

* `http://dagobah.net/flash/404.swf` - File viewing URL.
* `http://dagobah.net/flash/download/404.swf` - File download URL.
* `http://dagobah.net/flashswf/404.swf` - File embed URL.
* `http://dagobah.net/flash/404.swf/comments` - Comment URL.
* `http://dagobah.net/t100/404.swf` - 100x100px thumbnail URL.

### Table `files`

```
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
```

* `filename` (Primary Key) - The filename is always unique, and forms the URL.
  * _Gallery_ - Found in `<a href="/flash/3_anime_songs.swf" id="f10166" class="flash"></a>`
* `id` - Flash ID as displayed in the gallery. It is also a candidate for the primary key, but since filename is always unique we chose to use that instead, since it's more descriptive.
  * _Gallery_ - Found in `<a href="/flash/3_anime_songs.swf" id="f10166" class="flash"></a>`
* `title` - The Title of the flash file.
  * _Gallery_ - Found in `<span class="flashname">3 anime songs</span>`
  * _Viewer_ - Found in `<span class="fontFlashname" id="flash_otsikko">404</span>`, where `404` is the name
* `rating` - A float value from 1-5.
  * _Gallery_ - 
  * _Viewer_ - Found in `<li class="current-rating">Currently 3.39/5</li>`.
* `raters` - Amount of people who actually rated the post.
  * _Gallery_
  * Found in `<span class="votedxtimes">(123 votes)</span>`
* `size` - Filesize of the item. To keep the data consistent, all kilobyte entries are converted to floating point megabytes.
  * _Gallery_
* `date` - ISO posting date of the item, in `YYYY-MM-DD`
  * _Gallery_
* `youtubeid` (optional) - Some newer Dagobah links provide a YouTube embed instead. Get the ID from it.
  * _Viewer_ 

### Table `comments`

A table listing all comments attached to an item.

* `commentid` (INTEGER PRIMARY KEY AUTOINCREMENT) - The ID of the comment. Produced automatically.
* `filename` (Foreign Key) - The filename that the comment will be associated with.
* `comment` - The body of the comment.
* `username` (optional) - The username.
* `title` (optional) - The title.
* `timestamp` (ORDER BY) - The date and time that the comment was posted. This also represents the post order.

### Table `tag`

A one-to-many linking table should be used to store tags.

* `filename` (Foreign Key) - The filename that the tag will be associated with.
* `tag` - One tag that the filename will be associated with. Not unique.
  * This should probably be extracted from the comments page (which has the full list), not the viewer page.