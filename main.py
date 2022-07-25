import discord
from discord.ext import commands
from keep_alive import keep_alive
import os
from cogs import setup

client = commands.Bot(command_prefix='$', intents=discord.Intents.all())
client.remove_command('help')
setup(client)

@client.event
async def on_ready():
  print("Logged as {0.user}".format(client))

if __name__ == "__main__":
  try:
    keep_alive()
    client.run(os.environ['token'])
  except:
    os.system("kill 1")
