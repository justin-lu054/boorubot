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
from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial


def dump_gelbooru(tags: str, pageLimit: int) -> int:
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
                print("page " + str(pid) + " loaded")
            except:
                print("Error loading element")
            pid += 1
    db.commit()
    cursor.close()
    db.close()
    return pid

def dump_rule34(tags: str, pageLimit: int) -> int:
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
                print("An error occurred.")
    pid += 1
    db.commit()
    cursor.close()
    db.close()
    return pid

def fetchByTag(tags: str, dbName: str, sfw: typing.Optional[bool] = False, sortByScore: typing.Optional[bool] = False) -> list:
    #parse tags param
    tagList = tags.split("+")    
    sql = f"SELECT * FROM {dbName} WHERE tags LIKE '%{tagList[0]}%'"
    for elem in tagList:
        sql += f" AND tags LIKE '%{elem}%'"   
    if sfw is True: 
        sql += " AND rating = 's'"
    if sortByScore is True:
        sql += " ORDER BY score DESC"

    db = sqlite3.connect("scrapedlinks.sqlite")
    cursor = db.cursor() 
    cursor.execute(sql)
    result = cursor.fetchall()
    db.commit()
    cursor.close()
    db.close()
    return result

def fetchByFavourite(user_id: int, db_name: str) -> list:
    db = sqlite3.connect("scrapedlinks.sqlite")
    cursor = db.cursor()
    sql = (f"SELECT link FROM {db_name} WHERE user_id = '{user_id}'")
    cursor.execute(sql)
    results = cursor.fetchall() 
    db.commit()
    cursor.close()
    db.close()
    return results

async def sendimgs(ctx: commands.Context, tags: str, dbName: str, mode:str, limit: typing.Optional[int] = 10, sfw: typing.Optional[bool] = False):
    try: 
        if (mode == "top"):
            result = fetchByTag(tags, dbName, sfw, True)
        else:
            result = fetchByTag(tags, dbName, sfw)
        if (result == []):
            await ctx.send("Nothing found with that tag. Try using .load_db")
            return
            
        if limit > len(result):
            limit = len(result)

        for i in range(limit): 
            embed = discord.Embed(title=f"{i+1}/{limit}", 
                                    description="",
                                    color=discord.Color.blue())
            imglink = ""
            if (mode == "random"):
                imglink = random.choice(result)[0]
                embed.set_image(url=imglink)
            else:
                imglink = result[i][0]
                embed.set_image(url=imglink)
            embed.add_field(name="Image Link", value=imglink, inline=True)
            embed.set_footer(text=f"Requested by: {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
            message = await ctx.send(embed=embed)
            await message.add_reaction('\U0001F44D')
    except:
        await ctx.send("An error occurred. Please consult .help and verify that you are using the command correctly.")  

async def sendfavourites(ctx: commands.Context, db_name: str):
    try:
        results = fetchByFavourite(ctx.message.author.id, db_name)
        count = 1
        for result in results: 
            embed = discord.Embed(title=f"{count}/{len(results)}", 
                                description=f"{ctx.message.author.name}'s favourites",
                                color=discord.Color.blue())
            embed.set_image(url=result[0])
            embed.add_field(name="Image Link", value=result[0], inline=True)
            embed.set_footer(text=f"Requested by: {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
            message = await ctx.send(embed=embed)
            count += 1
    except:
        await ctx.send("An error occurred. Usage: .favourites")    

async def _addfavourite(ctx: commands.Context, source: str, link: str):
    if (source == "gelbooru"):
        db_name_1 = "sauce"
        db_name_2 = "sauceusers"
    else:
        db_name_1 = "sauce34"
        db_name_2 = "sauce34users"
    try:
        if (link is None):
            await ctx.send("Usage: .addfavourite [url]")
            return 
        if not (("gelbooru.com" in link) or ("rule34.xxx" in link)):
            await ctx.send("Please enter a valid link")
            return
        db = sqlite3.connect("scrapedlinks.sqlite")
        cursor = db.cursor()
        sql = f"SELECT tags FROM {db_name_1} WHERE link = '{link}'"
        cursor.execute(sql)
        result = cursor.fetchone()
        if (result is None):
            await ctx.send("Unknown link detected.")
            return 
        tags = result[0]
        sql = f"INSERT OR IGNORE INTO {db_name_2}(user_id, link, tags) VALUES(?, ?, ?)"
        val = (ctx.message.author.id, link, tags)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        await ctx.message.channel.purge(limit=1)
        await ctx.send(ctx.message.author.mention + " has added a link to favourites.")
    except:
        await ctx.send("An error occurred. Usage: .addfavourite [url]")

async def _removefavourite(ctx: commands.Context, db_name: str, link: str):
    try:
        if (link is None):
            await ctx.send("Usage: .favourite [url]")
            return 
        db = sqlite3.connect("scrapedlinks.sqlite")
        cursor = db.cursor()
        sql = f"SELECT user_id, link FROM {db_name} where link = '{link}'"
        cursor.execute(sql)
        result = cursor.fetchall()
        if (result == []):
            await ctx.send("No favourites found with that link.")
            return
        sql = f"DELETE FROM {db_name} WHERE link='{link}'"
        cursor.execute(sql)
        await ctx.message.channel.purge(limit=1)
        await ctx.send("Removed from favourites.")
        db.commit()
        cursor.close()
        db.close()
    except:
        await ctx.send("An error occurred. Usage: .removefavourite [url]")

async def sendrecommendations(ctx: commands.Context, source: str, limit: typing.Optional[int] = 10):
    try:
        recommendations = getNRecommendations(ctx.message.author.id, source, limit)
        if (recommendations is False):
            await ctx.send("Please add some items to your favourites first.")
        else:
            count = 1
            for link in recommendations:
                embed = discord.Embed(title=f"{count}/{len(recommendations)}", 
                                description=f"{ctx.message.author.name}'s recommendations",
                                color=discord.Color.blue())
                embed.set_image(url=link)
                embed.add_field(name="Image Link", value=link, inline=True)
                embed.set_footer(text=f"Requested by: {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
                message = await ctx.send(embed=embed)
                await message.add_reaction('\U0001F44D')
                count += 1
    except:
        await ctx.send("Usage: .recommend [numofrecommendations]")




class Rule34Cog(commands.Cog, name= "Rule34Scrape"):
    def __init__(self, bot):
        self.bot = bot 
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user == self.bot.user:
            return 
        if "us.rule34.xxx" in reaction.message.embeds[0].image.url:
            if (reaction.emoji == '👍'): 
                db = sqlite3.connect("scrapedlinks.sqlite")
                cursor = db.cursor()
                sql = f"SELECT tags FROM sauce34 WHERE link = '{reaction.message.embeds[0].image.url}'"
                cursor.execute(sql)
                result = cursor.fetchone()

                if (result is None):
                    await self.bot.send("Unknown link detected")
                    return

                tags = result[0]

                sql = "INSERT OR IGNORE INTO sauce34users(user_id, link, tags) VALUES(?, ?, ?)"
                val = (user.id, reaction.message.embeds[0].image.url, tags)
                cursor.execute(sql, val)
                db.commit()
                cursor.close()
                db.close()
                await reaction.message.channel.send(user.mention + " has added an image to their favourites")
    
    @commands.group(invoke_without_command=True)
    async def rule34(self, ctx):
        await ctx.send("available commands: load_db, bomb, bomball, bombtop, addfavourite, removefavourite, favourites")

    @rule34.command()
    async def load_db(self, ctx, tags=None, pageLimit: typing.Optional[int] = 10000):   
        try:
            if tags is None:
                await ctx.send("Usage: .load_db [tags separated by +] [numberOfPages=50]")
                return 
            pid = await asyncio.get_event_loop().run_in_executor(ThreadPoolExecutor(max_workers=1), partial(dump_rule34, tags, pageLimit))
            await ctx.send(str(pid) + " pages loaded")
        except:
            await ctx.send("An error occured. Usage: .load_db [tags separated by +] [numberOfPages=50]")

    @rule34.command()
    async def bomb(self, ctx, tags=None, limit: typing.Optional[int] = 10):
        if (tags is None):
            await ctx.send("Please specify some tags.")
            return 
        await sendimgs(ctx, tags, "sauce34", "random", limit, False)
    
    @rule34.command()
    async def bomball(self, ctx, tags=None, limit: typing.Optional[int] = 10):
        if (tags is None):
            await ctx.send("Please specify some tags.")
            return 
        await sendimgs(ctx, tags, "sauce34", "standard", limit, False)
    
    @rule34.command()
    async def bombtop(self, ctx, tags=None, limit: typing.Optional[int] = 10):
        if (tags is None):
            await ctx.send("Please specify some tags.")
            return 
        await sendimgs(ctx, tags, "sauce34", "top", limit, False)

    @rule34.command()
    async def addfavourite(self, ctx, link=None):
        await _addfavourite(ctx, "rule34", link)
    
    @rule34.command()
    async def removefavourite(self, ctx, link=None):
        await _removefavourite(ctx, "sauce34users", link)
    
    @rule34.command()
    async def favourites(self, ctx):
        await sendfavourites(ctx, "sauce34users")

    @rule34.command()
    async def recommend(self, ctx, limit: int=10):
        await sendrecommendations(ctx, "rule34", limit)


class GelbooruCog(commands.Cog, name = "GelbooruScrape"):
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
    async def load_db(self, ctx, tags=None, pageLimit: typing.Optional[int] = 10000):   
        try:
            if tags is None:
                await ctx.send("Usage: .load_db [tags separated by +] [numberOfPages=all]")
                return 
            pid = await asyncio.get_event_loop().run_in_executor(ThreadPoolExecutor(max_workers=1), partial(dump_gelbooru, tags, pageLimit))
            await ctx.send(str(pid) + " pages loaded")
        except:
            await ctx.send("An error occured. Usage: .load_db [tags separated by +] [numberOfPages=all]")

    @gelbooru.command()
    async def bomb(self, ctx, tags=None, limit: typing.Optional[int] = 10, sfw: typing.Optional[bool] = False):
        if (tags is None):
            await ctx.send("Please specify some tags.")
            return
        await sendimgs(ctx, tags, "sauce", "random", limit, sfw)
    
    @gelbooru.command()
    async def bomball(self, ctx, tags=None, limit: typing.Optional[int] = 10, sfw: typing.Optional[bool] = False):
        if (tags is None):
            await ctx.send("Please specify some tags.")
            return
        await sendimgs(ctx, tags, "sauce", "standard", limit, sfw)
    
    #Gets the top posts
    @gelbooru.command()
    async def bombtop(self, ctx, tags=None, limit: typing.Optional[int] = 10, sfw: typing.Optional[bool] = False):
        if (tags is None):
            await ctx.send("Please specify some tags.")
            return
        await sendimgs(ctx, tags, "sauce", "top", limit, sfw)

    @gelbooru.command()
    async def addfavourite(self, ctx, link=None):
        await _addfavourite(ctx, "gelbooru", link)
    
    @gelbooru.command()
    async def removefavourite(self, ctx, link=None):
        await _removefavourite(ctx, "sauceusers", link)
    
    @gelbooru.command()
    async def favourites(self, ctx):
        await sendfavourites(ctx, "sauceusers")

    @gelbooru.command()
    async def recommend(self, ctx, limit: int=10):
        await sendrecommendations(ctx, "gelbooru", limit)
    
def setup(bot):
    bot.add_cog(GelbooruCog(bot))
    print("gelbooru cog is loaded")
    bot.add_cog(Rule34Cog(bot))
    print("rule34 cog is loaded")
