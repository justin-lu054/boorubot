# imageboardscrapebot
A discord bot that scrapes a popular imageboard for images and sends those images on command. 

## Commands

### .gelbooru

If you would like to specify more than one tag to search by, please separate your tags with a +

To add any image from the bot to your favourites, simply thumbs react the image.

`.gelbooru load_db [tags separated by +] [limit=50]` will load the local database with (50 by default) pages corresponding to the tags since calling a large get request each time will get me blocked from making requests.  

`.gelbooru bomb [tags separated by +] [limit=10] [sfw=false]` will randomy select (ten by default) images corresponding to the tags. Modifying the limit will change the number of images, and adding "True" at the end of a command will send safe for work results only. 

`.gelbooru bomball [tags separated by +] [limit=10] [sfw=false]` will select (ten by default) images in order corresponding to the tags. Modifying the limit will change the number of images, and adding "True" at the end of a command will send safe for work results only. 

`.gelbooru bombtop [tags separated by +] [limit=10] [sfw=false]` will select the top (ten by default) highest scoring images corresponding to the tags. Modifying the limit will change the number of images, and adding "True" at the end of a command will send safe for work results only. 

`.gelbooru favourites` will send all of the user's favourited images. Users can favourite images by thumbs up reacting any image sent by the bot. 

`.gelbooru removefavourite [link]` allows users to remove a favourite from their list of favourites. 

`.gelbooru addfavourite [link]` allows users to manually add a valid link to their favourites. 

`.gelbooru recommend [limit=10]` will select (ten by default) images that are the most similar to the user's favourites. This recommendation system uses tag counts, and cosine similarity as a similarity metric. It is entirely dependent on the accuracy of the image metadata. Different simlarity metrics, and reccomendation systems are being tested.

### .rule34 

The exact same commands as above can be used for the rule34 image board. 


