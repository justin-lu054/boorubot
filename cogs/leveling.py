import discord
from discord.ext import commands
import asyncio 
import datetime
import sqlite3
import os
import math

class LevelingCog(commands.Cog, name = "Leveling"):
    def __init__(self, bot):
        self.bot = bot 

    #Fixed
    @commands.Cog.listener()
    async def on_message(self, message):
        #Prevents the bot from being logged in the database
        if message.author == self.bot.user:
            return
        db = sqlite3.connect("leveling.sqlite")
        cursor = db.cursor()
        #grab id of message author
        cursor.execute(f"SELECT user_id FROM levels WHERE guild_id = '{message.author.guild.id}' and user_id = '{message.author.id}'")
        result = cursor.fetchone()
        #if not in db, add them 
        #FIXED BY changing "message" to "message.author.id on line 24......... "
        if result is None:
            sql = ("INSERT INTO levels(guild_id, user_id, exp, lvl) VALUES(?, ?, ?, ?)")
            val = (message.author.guild.id, message.author.id, 2, 0)
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
        else:              #user_id is index 0, exp is index 1, etc...
            cursor.execute(f"SELECT user_id, exp, lvl FROM levels WHERE guild_id = '{message.author.guild.id}' and user_id = '{message.author.id}'")
            result1 = cursor.fetchone()
            exp = int(result1[1])
            sql = ("UPDATE levels SET exp = ? WHERE guild_id = ? and user_id = ?")
            val = (exp + 2, str(message.guild.id), str(message.author.id))
            cursor.execute(sql, val)
            db.commit()
            #fetch updated results
            cursor.execute(f"SELECT user_id, exp, lvl FROM levels WHERE guild_id = '{message.author.guild.id}' and user_id = '{message.author.id}'")
            result2 = cursor.fetchone()
            #feth initial xp and level
            xp_start = int(result2[1])
            lvl_start = int(result2[2])
            xp_end = math.floor(5 * (lvl_start ** (1/6) + 25 * lvl_start + 10))
            if xp_start > xp_end: 
                await message.channel.send(f"{message.author.mention} has leveled up to level {lvl_start + 1}")
                sql = ("UPDATE levels SET lvl = ?, exp = ? WHERE guild_id = ? and user_id = ?")
                val = (lvl_start + 1, 0, str(message.guild.id), str(message.author.id))
                cursor.execute(sql, val)
                db.commit()
            cursor.close()
            db.close()

    @commands.command()
    async def rank(self, ctx, user:discord.User=None):
        if user is None:
            db = sqlite3.connect("leveling.sqlite")
            cursor = db.cursor()
            cursor.execute(f"SELECT user_id, exp, lvl FROM levels WHERE guild_id = '{ctx.message.author.guild.id}' and user_id = '{ctx.message.author.id}'")
            result = cursor.fetchone()
            if result is None:
                await ctx.send("That user is not yet ranked")
            else:
                await ctx.send(f"{user.name} is currently level '{str(result[2])}' and has '{str(result[1])}' XP")
        else:
            db = sqlite3.connect("leveling.sqlite")
            cursor = db.cursor()
            cursor.execute(f"SELECT user_id, exp, lvl FROM levels WHERE guild_id = '{ctx.message.author.guild.id}' and user_id = '{user.id}'")
            result = cursor.fetchone()
            if result is None:
                await ctx.send("That user is not yet ranked")
            else:
                await ctx.send(f"{user.name} is currently level '{str(result[2])}' and has '{str(result[1])}' XP")

        
        
def setup(bot):
    bot.add_cog(LevelingCog(bot))
    print("Leveling is loaded")
