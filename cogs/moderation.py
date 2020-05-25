import discord
from discord.ext import commands 
import asyncio 
import datetime

class ModCog(commands.Cog, name = "Moderation"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def kick(self, ctx, user: discord.Member, *, reason=None): 
        if user.guild_permissions.administrator:
            await ctx.send("you can't kick the admin lmao")
        elif ctx.message.author.guild_permissions.kick_members:
            if reason is None:
                await ctx.guild.kick(user=user, reason="None")
                await ctx.send(f"{user} has been kicked.")
            else: 
                await ctx.guild.kick(user=user, reason=reason)
                await ctx.send(f"{user} has been kicked for {reason}")
        else:
            await ctx.send("Invalid permissions")    

    @commands.command()
    async def ban(self, ctx, user: discord.Member, *, reason=None): 
        if user.guild_permissions.administrator:
            await ctx.send("you can't kick the admin lmao")
        elif ctx.message.author.guild_permissions.ban_members:
            if reason is None:
                await ctx.guild.ban(user=user, reason="None")
                await ctx.send(f"{user} has been banned.")
            else: 
                await ctx.guild.ban(user=user, reason=reason)
                await ctx.send(f"{user} has been banned for {reason}")
        else:
            await ctx.send("Invalid permissions")    

    @commands.command()
    async def purge(self, ctx, *, number:int=None):
        if ctx.message.author.guild_permissions.manage_messages:
            try:
                if number is None:
                    await ctx.send("You must enter a number")
                else:
                    deleted = await ctx.message.channel.purge(limit=number)
                    await ctx.send(f"Messages deleted by {ctx.message.author.mention}: {len(deleted)}")
            except:
                await ctx.send("Cannot purge messages")
        else:
            await ctx.send("Invalid permissions")       

def setup(bot):
    bot.add_cog(ModCog(bot))
    print("Moderation is loaded")
