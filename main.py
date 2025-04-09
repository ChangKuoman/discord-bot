import discord
from discord.ext import commands
import os
from cogs import setup
from dotenv import load_dotenv
import asyncio

client = commands.Bot(command_prefix='$', intents=discord.Intents.all())
client.remove_command('help')
asyncio.run(setup(client))

@client.event
async def on_ready():
  print("Logged as {0.user}".format(client))

if __name__ == "__main__":
  try:
    load_dotenv()
    client.run(os.getenv("token"))
  except:
    os.system("kill 1")
