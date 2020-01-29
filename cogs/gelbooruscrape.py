import discord
from discord.ext import commands
import asyncio 
import requests
import bs4
import json
import sqlite3
import random

def thumbToImg(thumblink):
    imglink = thumblink.replace("gelbooru", "img2.gelbooru").replace("thumbnails", "samples").replace("thumbnail_", "sample_")
    return imglink


class GelbooruScrapeCog(commands.Cog, name = "GelbooruScrape"):
    def __init__(self, bot):
        self.bot = bot 
    
    @commands.group(invoke_without_command=True)
    async def gelbooru(self, ctx):
        await ctx.send("available commands: load_db, bomb")
    
    #loads all images associated with a tag into a db
    #default limit is 1000
    @gelbooru.command()
    async def load_db(self, ctx, tag=None, limit=500):   
        try:
            if tag is None:
                await ctx.send("Please specify a tag, or a series of tags separated by '+' followed by an (optional) limit")
                return 

            pid = 0
            errCount = 0
            pageCount = 1
            db = sqlite3.connect("scrapedlinks.sqlite")
            cursor = db.cursor()
            while True:
                res = requests.get("https://gelbooru.com/index.php?page=post&s=list&tags=" + tag + "&pid=" + str(pid))    
                res.raise_for_status()
                page = bs4.BeautifulSoup(res.text, "html.parser")
                url = page.select('span[class="thumb"] > a > img')
                for i in range(len(url)):
                    try:
                        tags = (url[i].get("title"))
                        link = (thumbToImg(url[i].get("src")))

                        #will only insert if not already exists
                        sql = "INSERT OR IGNORE INTO sauce(link, tags) VALUES(?, ?)"
                        val = (link, tags)
                        cursor.execute(sql, val)
                    except:
                        print("error occurred")
                        errCount += 1
                pid += 20
                print(str(pageCount) + " pages loaded.")
                pageCount += 1
                if ((pid > limit) or len(url) == 0):
                    break
            db.commit()
            cursor.close()
            db.close()
            await ctx.send("Finished Loading")
            await ctx.send("Failed to load " + str(errCount) + " items.")
        except:
            await ctx.send("Usage: .db_load [tag]")


    @gelbooru.command()
    async def bomb(self, ctx, tags=None, limit=10):
        try: 
            if (tags is None):
                await ctx.send("Usage: .bomb [tag]")
                return 
            tagList = tags.split("+")

            sql = f"SELECT * FROM sauce WHERE tags LIKE '%{tagList[0]}%'"
            for elem in tagList:
                sql += f" AND tags LIKE '%{elem}%'"   

            db = sqlite3.connect("scrapedlinks.sqlite")
            cursor = db.cursor() 
            cursor.execute(sql)
            result = cursor.fetchall()
            if (result == []):
                await ctx.send("Nothing found with that tag. Try using .load_db")
                return
            for i in range(limit): 
                await ctx.send(random.choice(result)[0])
            db.commit()
            cursor.close()
            db.close()
        except:
            await ctx.send("Usage: .bomb [tags]")
                

def setup(bot):
    bot.add_cog(GelbooruScrapeCog(bot))
    print("gelbooru scrape is loaded")
