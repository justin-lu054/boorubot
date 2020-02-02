import os
import discord
from discord.ext import commands
import asyncio
import sys
import datetime
import sqlite3

#YOUR .env FILEPATH HERE
#load_dotenv(r"C:\Users\justi\Discord\keys.env")
TOKEN = "BOT_TOKEN_HERE"
GUILD = "LocalBotTest"

bot = commands.Bot(command_prefix = '.')

@bot.event
async def on_ready():
    #Select the guild the bot is connected to
    for guild in bot.guilds:
        if guild.name == GUILD:
            break
    print(f"{bot.user} has connected to Discord!")
    print(f"{guild.name}(id: {guild.id})")
    members = "\n - ".join([member.name for member in guild.members])
    print(f"Guild members:\n - {members}")

#Loads all of the cogs
#removed unnecessary cogs
initial_extensions = ["cogs.moderation", "cogs.matrixcalculation", "cogs.gelbooruscrape", "cogs.rule34scrape"]
if __name__ == "__main__":
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f"Failed to load extension {extension}", file=sys.stderr)

@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(f"Hi {member.name}, welcome to the server")

@bot.event
async def on_error(event, *args, **kwargs):
    with open("err.log", "a") as f:
        if event == "on_message":
            f.write(f"Unhandled message: {args[0]}\n")
#try:
bot.run(TOKEN)
#except:
    #print("Error running bot")

#temporairly disabling the time logger
"""
finally:
    #IMPORTANT!!!! YOU MUST USE CTRL+C TO CLOSE IT AND NOT KILL TERMINAL!
    #log the last online time for the bot
    #Use DateTime API
    for guild in bot.guilds:
        if guild.name == GUILD:
            break
    #get time in UTC
    endTime = datetime.datetime.utcnow()
    db = sqlite3.connect("leveling.sqlite")
    cursor = db.cursor()
    cursor.execute(f"SELECT time FROM lastonline WHERE server_id = '{guild.id}'")
    result = cursor.fetchone()
    if result is None:
        sql = ("INSERT INTO lastonline(time, server_id) VALUES(?, ?)")
        val = (endTime, guild.id)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
    else:
        sql = ("UPDATE lastonline SET time = ? where server_id = ?")
        val = (endTime, guild.id)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
"""