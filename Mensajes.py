from discord.ext import commands
from functions import (
  get_quote,
  get_cat,
  get_dog
)
from datetime import datetime, timedelta

class Mensajes(commands.Cog):
  def __init__(self, client):
    self.client = client

  @commands.command()
  async def prueba(self, ctx):
    await ctx.send(ctx.guild.id)

  @commands.command(name="time", aliases=["now", "dt", "datetime", "date", "ts", "timestamp"])
  async def time(self, ctx):
    timestamp = datetime.today()
    result = ""
    result += "Perú: " + str(timestamp - timedelta(hours=5)) + '\n'
    result += "LV: " + str(timestamp - timedelta(hours=7)) + '\n'
    await ctx.send(result)

  @commands.command()
  async def ping(self, ctx):
    await ctx.send("pong!")

  @commands.command()
  async def quote(self, ctx):
    quote = get_quote()
    await ctx.send(quote)

  @commands.command()
  async def dog(self, ctx):
    dog = get_dog()
    await ctx.send(dog)

  @commands.command()
  async def cat(self, ctx):
    cat = get_cat()
    await ctx.send(cat)

  @commands.command()
  async def help(self, ctx):
    help = """
```
HELP:
Prefix: $
Commands:
  + ping -> pong!
  + cat -> send image of a cat
  + dog -> send image of a dog
  + quote -> send quote
Music commands:
  + connect | join -> bot joins channel
  + disconnect | leave -> bot leaves channel
  + play | p | add [url] -> play url song
  + pause -> pauses song
  + resume -> resumes song
  + queue | q -> shows queue
  + status | stats -> Bool is_playing
  + clear | cls | kill -> clears all queue
  + next | skip -> skips song to the next
Extensions:
  + kisslist help -> commands for kisslist extension
```
"""

    await ctx.send(help)


def setup(client):
  client.add_cog(Mensajes(client))

