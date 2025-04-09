from discord.ext import commands
import discord
import requests
from datetime import datetime, timedelta

class General(commands.Cog):
  """Commands for general use"""

  def __init__(self, client):
    self.CLIENT = client
    self.COLOR = 0xB4bb00

  @commands.command(name="ping", help="Sends latency in ms")
  async def ping(self, ctx):
    embed = discord.Embed(
      description=f"🏓 Pong! Latency: {round(self.CLIENT.latency * 1000)}ms",
      color=self.COLOR
    )
    await ctx.send(embed=embed)

  @commands.command(name="dog", help="Sends random dog image")
  async def dog(self, ctx):
    response = requests.get("https://dog.ceo/api/breeds/image/random").json()
    if response["status"]:
      image_link = response["message"]
      await ctx.send(image_link)
    else:
      embed = discord.Embed(
        description="Something went wrong!",
        color=self.COLOR
      )
      await ctx.send(embed=embed)

  @commands.command(name="cat", help="Sends random cat image")
  async def cat(self, ctx):
    response = requests.get("https://api.thecatapi.com/v1/images/search").json()
    try:
      image_link = response[0]["url"]
      await ctx.send(image_link)
    except:
      embed = discord.Embed(
        description="Something went wrong!",
        color=self.COLOR
      )
      await ctx.send(embed=embed)

  @commands.command(name="quote", help="Sends random quote")
  async def quote(self, ctx):
    response = requests.get("https://zenquotes.io/api/random").json()
    embed = discord.Embed(
      description=f"{response[0]['q']}",
      color=self.COLOR
    )
    embed.set_author(name=f"{response[0]['a']}")
    await ctx.send(embed=embed)

  @commands.command(name="timestamp", aliases=["now", "datetime"], help="Sends actual timestamp")
  async def timestamp(self, ctx):
    timestamp = datetime.today()
    embed = discord.Embed(
      title="TIMESTAMP",
      color=self.COLOR
    )
    gmt_m5 = timestamp - timedelta(hours=5)
    gmt_m7 = timestamp - timedelta(hours=7)
    #gmt_p2 = timestamp + timedelta(hours=2)
    gmt_p1 = timestamp + timedelta(hours=1)
    
    embed.add_field(name="🇵🇪 Lima, Perú: ", value=f"`{gmt_m5}`")
    embed.add_field(name="🇺🇸 Las Vegas, USA: ", value=f"`{gmt_m7}`")
    embed.add_field(name="🇪🇸 Madrid, Spain: ", value=f"`{gmt_p1}`")
    await ctx.send(embed=embed)
