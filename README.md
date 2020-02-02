# imageboardscrapebot
A discord bot that scrapes a popular imageboard for images and sends those images on command. 

## Commands

`.gelbooru load_db [tags separated by +] [limit=50]` will load the local database with (50 by default) pages corresponding to the tags since calling a large get request each time will get me blocked from making requests.  

`.gelbooru bomb [tags separated by +] [limit=10] [sfw=false]` will randomy select ten images corresponding to the tags. Modifying the limit will change the number of images, and adding "True" at the end of a command will send safe for work results only. 

`.gelbooru bomball [tags separated by +] [limit=10] [sfw=false]` will select ten images in order corresponding to the tags. Modifying the limit will change the number of images, and adding "True" at the end of a command will send safe for work results only. 

`.gelbooru bombtop [tags separated by +] [limit=10] [sfw=false]` will select the top ten highest scoring images corresponding to the tags. Modifying the limit will change the number of images, and adding "True" at the end of a command will send safe for work results only. 

`.gelbooru favourites` will send all of the user's favourited images. Users can favourite images by thumbs up reacting any image sent by the bot. 

`.gelbooru removefavourite [link]` allows users to remove a favourite from their list of favourites. 

`.gelbooru addfavourite [link]` allows users to manually add a valid link. 

The exact same commands apply for another (nsfw) imageboard (which you can find the name of by typing .help) Simply replace .gelbooru with .<READCTED_NAME_OF_IMAGEBOARD> 

## Dependencies 
Make sure to `pip install` discord, bs4, sqlite3, and requests. 
