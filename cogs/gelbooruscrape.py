import discord
from discord.ext import commands
import asyncio 
import requests
import bs4
import json
import sqlite3
import random
import typing
from cogs.imagereccomend import getNRecommendations


class GelbooruScrapeCog(commands.Cog, name = "GelbooruScrape"):
    def __init__(self, bot):
        self.bot = bot 
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        #ignore bot reactions 
        if user == self.bot.user:
            return 

        if "img2.gelbooru.com" in reaction.message.embeds[0].image.url:
            if (reaction.emoji == '👍'): 
                db = sqlite3.connect("scrapedlinks.sqlite")
                cursor = db.cursor()
                sql = f"SELECT tags FROM sauce WHERE link = '{reaction.message.embeds[0].image.url}'"
                cursor.execute(sql)
                result = cursor.fetchone()

                if (result is None):
                    await self.bot.send("Unknown link detected")
                    return

                tags = result[0]

                sql = "INSERT OR IGNORE INTO sauceusers(user_id, link, tags) VALUES(?, ?, ?)"
                val = (user.id, reaction.message.embeds[0].image.url, tags)
                cursor.execute(sql, val)
                db.commit()
                cursor.close()
                db.close()
                await reaction.message.channel.send(user.mention + " has added an image to their favourites")
    
    @commands.group(invoke_without_command=True)
    async def gelbooru(self, ctx):
        await ctx.send("available commands: load_db, bomb, bomball, bombtop, addfavourite, removefavourite, favourites")
    
    #loads all images associated with a tag into a db
    #default page limit is 50
    @gelbooru.command()
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
                url = "https://gelbooru.com/index.php?page=dapi&api_key=be736997038e0532fd915204d83b32a59ea16a85a1efd4da4ac1a0b6475360c8&user_id=511816&s=post&q=index&json=1"
                url += ("&pid=" + str(pid))
                url += ("&tags=" + tags)
                resp = requests.get(url)
                data = resp.json()
                
                if (data == []):
                    break 

                for entry in data: 
                    link = (entry["file_url"])
                    entryTags = (entry["tags"])
                    rating = (entry["rating"])
                    score = (entry["score"])
                    try: 
                        sql = "INSERT OR IGNORE INTO sauce(link, tags, rating, score) VALUES(?, ?, ?, ?)"
                        val = (link, entryTags, rating, score)
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



    @gelbooru.command()
    async def bomb(self, ctx, tags=None, limit: typing.Optional[int] = 10, sfw: typing.Optional[bool] = False):
        try: 
            if (tags is None):
                await ctx.send("Usage: .bomb [tags separated by +] [limit=10] [sfw=false]")
                return 
            
            #parse tags param
            tagList = tags.split("+")
        
            sql = f"SELECT * FROM sauce WHERE tags LIKE '%{tagList[0]}%'"
            for elem in tagList:
                sql += f" AND tags LIKE '%{elem}%'"   
            
            if sfw is True: 
                sql += " AND rating = 's'"

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
                embed = discord.Embed(title=f"{i+1}/{limit}", 
                                    description="",
                                    color=discord.Color.blue())
                embed.set_image(url=random.choice(result)[0])
                message = await ctx.send(embed=embed)
                await message.add_reaction('\U0001F44D')
            db.commit()
            cursor.close()
            db.close()
        except:
            await ctx.send("Usage: .bomb [tags separated by +] [limit=10] [sfw=false]")
    
    @gelbooru.command()
    async def bomball(self, ctx, tags=None, limit: typing.Optional[int] = 10, sfw: typing.Optional[bool] = False):
        try: 
            if (tags is None):
                await ctx.send("Usage: .bomball [tags] [limit=10] [sfw=False]")
                return 
            
            #parse tags param
            tagList = tags.split("+")
        
            sql = f"SELECT * FROM sauce WHERE tags LIKE '%{tagList[0]}%'"
            for elem in tagList:
                sql += f" AND tags LIKE '%{elem}%'"   
            
            if sfw is True: 
                sql += " AND rating = 's'"

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
                embed = discord.Embed(title=f"{i+1}/{limit}", 
                                    description="",
                                    color=discord.Color.blue())
                embed.set_image(url=result[i][0])
                message = await ctx.send(embed=embed)
                await message.add_reaction('\U0001F44D')
            db.commit()
            cursor.close()
            db.close()
        except:
            await ctx.send("Usage: .bomball [tags] [limit=10] [sfw=False]")
    

    #Gets the top posts
    @gelbooru.command()
    async def bombtop(self, ctx, tags=None, limit: typing.Optional[int] = 10, sfw: typing.Optional[bool] = False):
        try: 
            if (tags is None):
                await ctx.send("Usage: .bombtop [tags] [limit=10] [sfw=False]")
                return 

            #parse tags param
            tagList = tags.split("+")
        
            sql = f"SELECT * FROM sauce WHERE tags LIKE '%{tagList[0]}%'"
            for elem in tagList:
                sql += f" AND tags LIKE '%{elem}%'"   
            
            if sfw is True: 
                sql += " AND rating = 's'"

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
                embed = discord.Embed(title=f"{i+1}/{limit}", 
                                    description="",
                                    color=discord.Color.blue())
                embed.set_image(url=result[i][0])
                message = await ctx.send(embed=embed)
                await message.add_reaction('\U0001F44D')
            db.commit()
            cursor.close()
            db.close()
        except:
            await ctx.send("Usage: .bombtop [tags] [limit=10] [sfw=False]")

    @gelbooru.command()
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

            sql = f"SELECT tags FROM sauceusers WHERE link = '{link}'"
            cursor.execute(sql)
            result = cursor.fetchone()
            if (result is None):
                await ctx.send("Unknown link detected")
                return 
            tags = result[0]
            sql = "INSERT OR IGNORE INTO sauceusers(user_id, link, tags) VALUES(?, ?, ?)"
            val = (ctx.message.author.id, link, tags)
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
            await ctx.message.channel.purge(limit=1)
            await ctx.send(ctx.message.author.mention + " has added a link to favourites.")
        except:
            await ctx.send("An error occurred. Usage: .addfavourite [url]")
    
    @gelbooru.command()
    async def removefavourite(self, ctx, link=None):
        try:
            if (link is None):
                await ctx.send("Usage: .favourite [url]")
                return 
            db = sqlite3.connect("scrapedlinks.sqlite")
            cursor = db.cursor()
            sql = f"SELECT user_id, link FROM sauceusers where link = '{link}'"
            cursor.execute(sql)
            result = cursor.fetchall()
            if (result == []):
                await ctx.send("No favourites found with that link.")
                return
            sql = f"DELETE FROM sauceusers WHERE link='{link}'"
            cursor.execute(sql)
            await ctx.message.channel.purge(limit=1)
            await ctx.send("Removed from favourites.")
            db.commit()
            cursor.close()
            db.close()
        except:
            await ctx.send("An error occurred. Usage: .addfavourite [url]")
    
    @gelbooru.command()
    async def favourites(self, ctx):
        try:
            db = sqlite3.connect("scrapedlinks.sqlite")
            cursor = db.cursor()
            sql = (f"SELECT link FROM sauceusers WHERE user_id = '{ctx.message.author.id}'")
            cursor.execute(sql)
            results = cursor.fetchall() 
            await ctx.send(f"Results found for {ctx.message.author.name}:")
            count = 1
            for result in results: 
                embed = discord.Embed(title=f"{count}/{len(results)}", 
                                    description=f"{ctx.message.author.name}'s favourites",
                                    color=discord.Color.blue())
                embed.set_image(url=result[0])
                message = await ctx.send(embed=embed)
                count += 1
            db.commit()
            cursor.close()
            db.close()
        except:
            await ctx.send("An error occurred. Usage: .favourites")    
    @gelbooru.command()
    async def recommend(self, ctx, number: int=10):
        try:
            recommendations = getNRecommendations(ctx.message.author.id, "gelbooru", number)
            if (recommendations is False):
                await ctx.send("Please add some items to your favourites first.")
            else:
                count = 1
                for link in recommendations:
                    embed = discord.Embed(title=f"{count}/{len(recommendations)}", 
                                    description=f"{ctx.message.author.name}'s recommendations",
                                    color=discord.Color.blue())
                    embed.set_image(url=link)
                    message = await ctx.send(embed=embed)
                    await message.add_reaction('\U0001F44D')
                    count += 1
        except:
            await ctx.send("Usage: .recommend [numofrecommendations]")

def setup(bot):
    bot.add_cog(GelbooruScrapeCog(bot))
    print("gelbooru scrape is loaded")
