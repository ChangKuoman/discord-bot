import discord
from discord.ext import commands
from keep_alive import keep_alive
import os
import Music
import Mensajes
import Kisslist

cogs = [Mensajes, Kisslist, Music]

client = commands.Bot(command_prefix='$', intents=discord.Intents.all())

client.remove_command('help')

for i in range(len(cogs)):
  cogs[i].setup(client)

@client.event
async def on_ready():
  print("We have logged in as {0.user}".format(client))

try:
  keep_alive()
  client.run(os.environ['token'])
except:
  os.system("kill 1")
