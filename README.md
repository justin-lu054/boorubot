# imageboardscrapebot
A discord bot that scrapes a popular imageboard for images and sends those images on command. 

## Commands

`.gelbooru load_db [tags separated by +] [limit=500]` will load the local database with (500 by default) image links corresponding to the tags since calling a get request each time takes too long. 

`.gelbooru bomb [tags separated by +] [limit=10]` will randomly select (ten by default) images corresponding to the tags. 

## Dependencies 
Make sure to `pip install` discord, bs4, sqlite3, and requests. 
