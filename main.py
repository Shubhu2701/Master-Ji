import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import music
import chat


load_dotenv()
token = os.getenv('TOKEN') 
cogs=[chat,music]
client = commands.Bot(command_prefix=";",intents=discord.Intents.all())
client.remove_command('help')
for i in range(len(cogs)):
    cogs[i].setup(client)
    	
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

client.run(token)