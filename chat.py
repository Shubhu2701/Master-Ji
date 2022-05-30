import discord
from discord.ext import commands
import random


class chat(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.message="""```General Commands:
        
;help - Displays all the available commands.
;join - Joins the voice channel.
;play <keyword> - Finds the song using the provided <keyword> on youtube and plays it in your current voice channel.
;pause - Pauses the current song playing in the voice channel.
;loop - Loops the song playing currently.
;resume - Resumes the paused song.
;now - Displays the song playing currently.
;queue - Displays the top 10 songs in the current queue.
;skip - Skips the current song.
;clear - Clears the queue.
;leave - Kicks the bot out of the voice channel.
```
"""
        self.hell=['Hello Sir.', 'Kiddan Soniyo!', 'Hanji', 'Greetings', 'Salutations!', 'Konichiwa!', 'Ha Bete', 'Howdy!']
        
    @commands.command()
    async def hello(self,ctx):
        await ctx.send(random.choice(self.hell))
    
    @commands.command(name='help',aliases=['HELP','Help','h','H'],help='Displays all the available commands.')
    async def help(self, ctx):
        await ctx.send(self.message)
    
    @commands.command(name='sky',aliases=['SKY','Sky','AAKASH','aakash','Aakash','DIXIT','dickshit','dixit','Dixit','Dickshit','shubhukabeta'])
    async def sky(self,ctx):
        await ctx.send('https://www.pornhub.com')
        
def setup(client):
	client.add_cog(chat(client))