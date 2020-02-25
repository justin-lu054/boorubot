import sys
from discord.ext import commands
import discord
import random


class CommandErrorHandler(commands.Cog, name="ErrorHandler"):
    def __init__(self, bot):
        self.bot = bot
    
    #Sends a generic error message when an error occurs. Specific details can be accessed in logs.
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            print(error)
            return await ctx.send("Command not found. Please refer to .help")
            
        elif isinstance(error, commands.CommandInvokeError):
            print(error)
            return await ctx.send("Incorrect syntax. Please refer to the .help for the command you are trying to use.")
            
        elif isinstance(error, commands.ConversionError):
            print(error)
            return await ctx.send("Incorrect syntax. Please refer to the .help for the command you are trying to use.")
            
        else:
            print(error)
            return await ctx.send("An error occurred. Please refer to .help command and verify your command parameters.")
    
    
    @commands.command()
    async def help(self, ctx, cog='all'):
        # The third parameter comes into play when
        # only one word argument has to be passed by the user

        # Prepare the embed

        help_embed = discord.Embed(
            title='Help',
            color=discord.Color.blue())

        help_embed.set_thumbnail(url=self.bot.user.avatar_url)
        help_embed.set_footer(
            text=f'Requested by {ctx.message.author.name}',
            icon_url=self.bot.user.avatar_url
        )
        help_embed.add_field(name="Help",
                        value="Please refer to https://github.com/justin-lu054/imageboardscrapebot/wiki/Commands-Reference for a full list of commands.", 
                        inline=False)
        await ctx.send(embed=help_embed)

def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
    print("Error handler loaded")