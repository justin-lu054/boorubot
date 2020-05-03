import os
import discord
from discord.ext import commands
import asyncio
import sys
import datetime
import os
from dotenv import load_dotenv
import sqlite3

load_dotenv("config.env")
TOKEN = os.getenv("BOT_TOKEN")
GUILD = os.getenv("GUILD")

bot = commands.Bot(command_prefix = '.')
bot.remove_command("help")
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
initial_extensions = ["cogs.moderation", "cogs.imgcog", "cogs.errorhandler"]
if __name__ == "__main__":
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f"Failed to load extension {extension}", file=sys.stderr)

@bot.event  
async def on_error(event, *args, **kwargs):
    with open("err.log", "a") as f:
        if event == "on_message":
            f.write(f"Unhandled message: {args[0]}\n")

bot.run(TOKEN)
