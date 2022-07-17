from discord.ext import commands
import discord
import requests
from datetime import datetime, timedelta

def get_quote():
  response = requests.get("https://zenquotes.io/api/random").json()
  quote = response[0]['q'] + " -" + response[0]['a']
  return quote

def get_cat():
  response = requests.get("https://api.thecatapi.com/v1/images/search").json()
  image_link = response[0]["url"]
  return image_link

def get_dog():
  response = requests.get("https://dog.ceo/api/breeds/image/random").json()
  if response["status"]:
    image_link = response["message"]
    return image_link
  else:
    return "Something went wrong!"

class Messages(commands.Cog):
  def __init__(self, client):
    self.client = client
    self.color = 0x28B4FF

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
    commands = """ping -> pong!
cat -> random image of cat
dog -> random image of dog
quote -> random quote
time | dt | timestamp | ts | date | now | datetime -> LV and Lima time
help -> get commands help
"""
    music_commands = """connect | join -> bot joins channel
disconnect | leave -> bot leaves channel
play | p | add [url] -> play url song
pause -> pauses song
resume -> resumes song
queue | q -> shows queue
status | stats -> Bool is_playing
clear | cls | kill -> clears all queue
next | skip -> skips song to the next
"""
    help_extensions = """kisslist help -> commands for kisslist extension
"""
    embed = discord.Embed(title=f"HELP LIST", color=self.color)
    embed.add_field(name="Prefix", value="`$`", inline=True)
    embed.add_field(name="Commands", value=f"`{commands}`", inline=False)
    embed.add_field(name="Music Commands", value=f"`{music_commands}`", inline=False)
    embed.add_field(name="Extensions", value=f"`{help_extensions}`", inline=False)
    
    await ctx.send(embed=embed)

  @commands.command()
  async def prueba(self, ctx):
    embed = discord.Embed(title=f"{ctx.author.name}'s")

    embed.add_field(name="field1:", value="`15`", inline=False)
    embed.add_field(name="field2:", value="16", inline=False)

    embed.set_footer(text="some text")
    await ctx.send(embed=embed)
  