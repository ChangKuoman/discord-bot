from discord.ext import commands
import discord
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

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
    # Current UTC time
    timestamp = datetime.now(ZoneInfo("UTC"))

    # Local times
    lima_time = timestamp.astimezone(ZoneInfo("America/Lima"))
    california_time = timestamp.astimezone(ZoneInfo("America/Los_Angeles"))
    madrid_time = timestamp.astimezone(ZoneInfo("Europe/Madrid"))

    # Emoji for DST
    def dst_emoji(dt):
        return "☀️" if dt.dst() and dt.dst().total_seconds() != 0 else ""

    embed = discord.Embed(
      title="TIMESTAMP",
      color=self.COLOR
    )

    # Add fields with time + DST emoji
    embed.add_field(
        name=f"🇵🇪 Lima, Perú {dst_emoji(lima_time)}",
        value=f"`{lima_time.strftime('%Y-%m-%d %H:%M:%S')}`"
    )

    embed.add_field(
        name=f"🇺🇸 California, USA {dst_emoji(california_time)}",
        value=f"`{california_time.strftime('%Y-%m-%d %H:%M:%S')}`"
    )

    embed.add_field(
        name=f"🇪🇸 Madrid, Spain {dst_emoji(madrid_time)}",
        value=f"`{madrid_time.strftime('%Y-%m-%d %H:%M:%S')}`"
    )

    await ctx.send(embed=embed)
