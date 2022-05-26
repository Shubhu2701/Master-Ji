import os
import discord
from discord.ext import commands
import music
import chat

token = 'OTc4OTc2MTQwOTIyMzU1NzUy.Gehv5B.xExK4ZcR9toaGWbAznXLJHuom9-QtMwBHwL6hI'
cogs=[chat,music]
client = commands.Bot(command_prefix="~", intents=discord.Intents.all())
client.remove_command('help')
for i in range(len(cogs)):
    cogs[i].setup(client)
    	
@client.event
async def on_ready():
	print(f'We have logged in as {client.user}')

client.run(token)