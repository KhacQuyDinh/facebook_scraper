# facebook_scraper
## This project is a modified version of Facebook_scraper (https://github.com/kevinzg/facebook-scraper)
## The instructions below are given in the origional repo (https://github.com/kevinzg/facebook-scraper)

## MIT License
 
 
# Facebook Scraper Selenium

Scrape Facebook Public Posts without using Facebook API 

## What It can Do
- Get data including the following fields:
['PostId', 'Group', 'Date', 'Post', 'Link', 'Image', 'Comments', 'Shares', 'Reaction']

## Install Requirements

Please make sure chrome is installed and ```chromedriver``` is placed in the same directory as the file.

```chromedriver``` must have the same version as Chrome browser using (help -> about to show this version).

Find out which version of ```chromedriver``` you need to download in this link [Chrome Web Driver](http://chromedriver.chromium.org/downloads).


```sh
pip install -r requirements.txt
```

## Usage

#### 1. Use scraper.py to print to screen or to file

##### The original version
```
usage: scraper.py [-h] -page PAGE -len LEN [-infinite INFINITE] [-usage USAGE]
                  [-comments COMMENTS]

Facebook Page Scraper

optional arguments:
  -h, --help            show this help message and exit

required arguments:
  -page PAGE, -p PAGE   The Facebook Public Page you want to scrape
  -len LEN, -l LEN      Number of Posts you want to scrape

optional arguments:
  -infinite INFINITE, -i INFINITE
                        Scroll until the end of the page (1 = infinite)
                        (Default is 0)
  -usage USAGE, -u USAGE
                        What to do with the data: Print on Screen (PS), Write
                        to Text File (WT) (Default is WT)
  -comments COMMENTS, -c COMMENTS
                        Scrape ALL Comments of Posts (y/n) (Default is n).
                        When enabled for pages where there are a lot of
                        comments it can take a while

```
##### The new option which is currently used in code (can be changed by coding skills)
###### Use config.yaml with params described as follows
```
credentials:
    email: ""
    password: ""

args:
    # default values are set in codes not in this file
    file_links: "file_links_test.txt" #path to file containing links of groups, type=string, required=True
    len: 4 #Number of Posts you want to scrape, type=int, required=True
    infinite: 0 #Scroll until the end of the page (1 = infinite) (Default is 0), type=int, default=0
    usage: "CSV" #What to do with the data: Print on Screen (PS), Write to Text File (WT), Write CSV file, default="CSV"
    comments: True #Scrape ALL Comments of Posts (True/False) (Default is False).
                 #When enabled for pages where there are a lot of comments it can
                 #take a while, type=string, default=False
```   

###### Type: python3 scraper.py

#### 2. Use ```extract()``` to grab list of posts for additional parsing

```
from scraper import extract

list = extract(page, len, etc..)

# do what you want with the list 
```

Return value of ```extract()``` :

```python
[
{'Post': 'Text text text text text....',
 'Link' : 'https://link.com',
 'Image' : 'https://image.com',
 'Comments': {
        'name1' : {
            'text' : 'Text text...',
            'link' : 'https://link.com',
            'image': 'https://image.com'
         }
        'name2' : {
            ...
            }
         ...
         },
 'Reaction' : { # Reaction only contains the top3 reactions
        'LIKE' : int(number_of_likes),
        'HAHA' : int(number_of_haha),
        'WOW'  : int(number_of_wow)
         }}
  ...
]
```

All fields:
['PostId', 'Group', 'Date', 'Post', 'Link', 'Image', 'Comments', 'Shares', 'Reaction']

### Note:

- Please use this code for Educational purposes only
- Will continue to add additional features and data
    - ~comment chains scraping~
    - comment reaction scraping
    - different comment display (Most Relevant, New, etc)
