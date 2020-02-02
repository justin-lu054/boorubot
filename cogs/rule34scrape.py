import discord
from discord.ext import commands
import asyncio 
import requests
import bs4
import json
import sqlite3
import random
import typing

def thumbToImg(thumblink):
    imglink = thumblink.replace("gelbooru", "img2.gelbooru").replace("thumbnails", "samples").replace("thumbnail_", "sample_")
    return imglink


class Rule34ScrapeCog(commands.Cog, name = "Rule34Scrape"):
    def __init__(self, bot):
        self.bot = bot 

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        #ignore bot reactions 
        if user == self.bot.user:
            return 

        if "us.rule34.xxx" in reaction.message.content.lower():
            if (reaction.emoji == '👍'): 
                db = sqlite3.connect("scrapedlinks.sqlite")
                cursor = db.cursor()
                sql = f"SELECT tags FROM sauce34 WHERE link = '{reaction.message.content}'"
                cursor.execute(sql)
                result = cursor.fetchone()

                if (result is None):
                    await ctx.send("Unknown link detected")
                    return

                tags = result[0]

                sql = "INSERT OR IGNORE INTO sauce34users(user_id, link, tags) VALUES(?, ?, ?)"
                val = (user.id, reaction.message.content, tags)
                cursor.execute(sql, val)
                db.commit()
                cursor.close()
                db.close()
                await reaction.message.channel.send(user.mention + " has added an image to their favourites")

    
    @commands.group(invoke_without_command=True)
    async def rule34(self, ctx):
        await ctx.send("available commands: load_db, bomb, bomball, bombtop, addfavourite, removefavourite, favourites")
    
    #loads all images associated with a tag into a db
    #default limit is 1000
    @rule34.command()
    async def load_db(self, ctx, tags=None, pageLimit: typing.Optional[int] = 50):   
        try:
            if tags is None:
                await ctx.send("Usage: .load_db [tags separated by +] [numberOfPages=50]")
                return 
            pid = 0
            db = sqlite3.connect("scrapedlinks.sqlite")
            cursor = db.cursor()
            #parse tags param
            tags = tags.replace("+", " ")

            for i in range(pageLimit): 
                url = "https://rule34.xxx/index.php?page=dapi&s=post&q=index&json=1"
                url += ("&pid=" + str(pid))
                url += ("&tags=" + tags)
                resp = requests.get(url)
                data = resp.json()
                
                if (data == []):
                    break 

                for entry in data: 
                    link = ("https://us.rule34.xxx/images/" + entry["directory"] + "/" + entry["image"])
                    entryTags = (entry["tags"])
                    score = (entry["score"])
                    try: 
                        sql = "INSERT OR IGNORE INTO sauce34(link, tags, score) VALUES(?, ?, ?)"
                        val = (link, entryTags, score)
                        cursor.execute(sql, val)   
                    except:
                        await ctx.send("Error loading an item into database.") 
                pid += 1
            db.commit()
            cursor.close()
            db.close()
            await ctx.send(str(pid) + " pages loaded")

        except:
            await ctx.send("An error occured. Usage: .load_db [tags separated by +] [numberOfPages=50]")



    @rule34.command()
    async def bomb(self, ctx, tags=None, limit: typing.Optional[int] = 10):
        try: 
            if (tags is None):
                await ctx.send("Usage: .bomb [tags separated by +] [limit=10]")
                return 
            
            #parse tags param
            tagList = tags.split("+")
        
            sql = f"SELECT * FROM sauce34 WHERE tags LIKE '%{tagList[0]}%'"
            for elem in tagList:
                sql += f" AND tags LIKE '%{elem}%'"   
            
            db = sqlite3.connect("scrapedlinks.sqlite")
            cursor = db.cursor() 
            cursor.execute(sql)
            result = cursor.fetchall()
            if (result == []):
                await ctx.send("Nothing found with that tag. Try using .load_db")
                return
            
            if limit > len(result):
                limit = len(result)

            for i in range(limit): 
                message = await ctx.send(random.choice(result)[0])
                await message.add_reaction('\U0001F44D')
            db.commit()
            cursor.close()
            db.close()
        except:
            await ctx.send("Usage: .bomb [tags separated by +] [limit=10]")
    
    @rule34.command()
    async def bomball(self, ctx, tags=None, limit: typing.Optional[int] = 10):
        try: 
            if (tags is None):
                await ctx.send("Usage: .bomball [tags] [limit=10]")
                return 
            
            #parse tags param
            tagList = tags.split("+")
        
            sql = f"SELECT * FROM sauce34 WHERE tags LIKE '%{tagList[0]}%'"
            for elem in tagList:
                sql += f" AND tags LIKE '%{elem}%'"   
            
            db = sqlite3.connect("scrapedlinks.sqlite")
            cursor = db.cursor() 
            cursor.execute(sql)
            result = cursor.fetchall()
            if (result == []):
                await ctx.send("Nothing found with that tag. Try using .load_db")
                return
            
            if limit > len(result):
                limit = len(result)

            for i in range(limit): 
                message = await ctx.send(result[i][0])
                await message.add_reaction('\U0001F44D')
            db.commit()
            cursor.close()
            db.close()
        except:
            await ctx.send("Usage: .bomball [tags] [limit=10]")
    
    @rule34.command()
    async def bombtop(self, ctx, tags=None, limit: typing.Optional[int] = 10):
        #try: 
            if (tags is None):
                await ctx.send("Usage: .bombtop [tags] [limit=10]")
                return 

            #parse tags param
            tagList = tags.split("+")
        
            sql = f"SELECT * FROM sauce34 WHERE tags LIKE '%{tagList[0]}%'"
            for elem in tagList:
                sql += f" AND tags LIKE '%{elem}%'"   

            sql += " ORDER BY score DESC"
            db = sqlite3.connect("scrapedlinks.sqlite")
            cursor = db.cursor() 
            cursor.execute(sql)
            result = cursor.fetchall()
            if (result == []):
                await ctx.send("Nothing found with that tag. Try using .load_db")
                return
            
            if limit > len(result):
                limit = len(result)

            for i in range(limit): 
                message = await ctx.send(result[i][0])
                await message.add_reaction('\U0001F44D')
            db.commit()
            cursor.close()
            db.close()
        #except:
            #await ctx.send("Usage: .bombtop [tags] [limit=10]")

    @rule34.command()
    async def addfavourite(self, ctx, link=None):
        try:
            if (link is None):
                await ctx.send("Usage: .addfavourite [url]")
                return 
            if not ("img.booru.org" in link):
                await ctx.send("please enter a valid link")
                return
            db = sqlite3.connect("scrapedlinks.sqlite")
            cursor = db.cursor()

            sql = f"SELECT tags FROM sauce34users WHERE link = '{link}'"
            cursor.execute(sql)
            result = cursor.fetchone()
            if (result is None):
                await ctx.send("Unknown link detected")
                return 
            tags = result[0]
            sql = "INSERT OR IGNORE INTO sauce34users(user_id, link, tags) VALUES(?, ?, ?)"
            val = (ctx.message.author.id, link, tags)
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
            await ctx.message.channel.purge(limit=1)
            await ctx.send(ctx.message.author.mention + " has added a link to favourites.")
        except:
            await ctx.send("An error occurred. Usage: .addfavourite [url]")
    
    @rule34.command()
    async def removefavourite(self, ctx, link=None):
        try:
            if (link is None):
                await ctx.send("Usage: .favourite [url]")
                return 
            db = sqlite3.connect("scrapedlinks.sqlite")
            cursor = db.cursor()
            sql = f"SELECT user_id, link FROM sauce34users where link = '{link}'"
            cursor.execute(sql)
            result = cursor.fetchall()
            if (result == []):
                await ctx.send("No favourites found with that link.")
                return
            sql = f"DELETE FROM sauce34users WHERE link='{link}'"
            cursor.execute(sql)
            await ctx.message.channel.purge(limit=1)
            await ctx.send("Removed from favourites.")
            db.commit()
            cursor.close()
            db.close()
        except:
            await ctx.send("An error occurred. Usage: .addfavourite [url]")
    
    @rule34.command()
    async def favourites(self, ctx):
        try:
            db = sqlite3.connect("scrapedlinks.sqlite")
            cursor = db.cursor()
            sql = (f"SELECT link FROM sauce34users WHERE user_id = '{ctx.message.author.id}'")
            cursor.execute(sql)
            results = cursor.fetchall() 
            await ctx.send(f"Results found for {ctx.message.author.name}:")
            for result in results: 
                await ctx.send(result[0])
            db.commit()
            cursor.close()
            db.close()
        except:
            await ctx.send("An error occurred. Usage: .favourites")    

def setup(bot):
    bot.add_cog(Rule34ScrapeCog(bot))
    print("rule34 scrape is loaded")
