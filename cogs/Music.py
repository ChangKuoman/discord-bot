import discord
from discord.ext import commands
import youtube_dl
from datetime import datetime, timedelta

class Music(commands.Cog):
  def __init__(self, client):
    self.client = client
    self.FFMPEG_OPTIONS = {
      'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
      'options': '-vn'
    }
    self.servers = {}
    self.color = 0x28B4FF
  
  def play_next(self, guild_id):
    if len(self.servers[guild_id]["queue"]) > 0:
      song = self.servers[guild_id]["queue"].pop(0)
      url = song["url"]
      self.servers[guild_id]["vc"].play(
        discord.FFmpegOpusAudio(url, **self.FFMPEG_OPTIONS),
        after=lambda e: self.play_next(guild_id)
      )

  def check_guild_id(self, guild_id):
    if guild_id not in self.servers.keys():
      self.servers[guild_id] = {"queue": [], "vc": None}

  def log_song(self, guild_id, guild_name, title, url, yt_url):
    with open("logs/songs.csv", "a") as log:
      time = str(datetime.today() - timedelta(hours=5))
      text = ",".join([
        guild_id,
        guild_name,
        title,
        time,
        yt_url,
        url
      ])
      log.write(text)
      log.write('\n')
  
  @commands.command(name="connect", aliases=["join"])
  async def connect(self, ctx):
    if ctx.author.voice is None:
      await ctx.send("You're not in a voice channel!")

    else:
      guild_id = str(ctx.guild.id)
      self.check_guild_id(guild_id)
      voice_channel = ctx.author.voice.channel
      
      if ctx.voice_client is None:
        self.servers[guild_id]["vc"] = await voice_channel.connect()
        await ctx.send("Connected")
      else:
        await ctx.voice_client.disconnect()
        self.servers[guild_id]["vc"] = await voice_channel.connect()
        await ctx.send("Moved")

  @commands.command(name="disconnect", aliases=["leave"])
  async def disconnect(self, ctx):
    guild_id = str(ctx.guild.id)
    self.check_guild_id(guild_id)
    
    if ctx.voice_client is not None:
      if len(self.servers[guild_id]["queue"]) > 0:
        self.servers[guild_id]["queue"].clear()
      if ctx.voice_client.is_playing():      
        ctx.voice_client.stop()
      
      await ctx.voice_client.disconnect()
      await ctx.send("Disconnected")
    else:
      await ctx.send("Bot not in voice channel")

  @commands.command(name="play", aliases=["p", "add"])
  async def play(self, ctx, url=None):
    if ctx.author.voice is None:
      await ctx.send("You're not in a voice channel!")
    elif ctx.voice_client is None:
      await ctx.send("Bot is not in a voice channel!")
    elif url is None:
      await ctx.send("You must put a valid url!")

    else:
      YDL_OPTIONS = {"format":"bestaudio"}
      with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        error = False
        try:
          info = ydl.extract_info(url, download=False)
          url2 = info["formats"][0]["url"]
          title = info["title"]
          yt_url = info["webpage_url"]
        except:
          error = True
      if error:
        await ctx.send("You must put a valid url!")
      
      else:
        guild_id = str(ctx.guild.id)
        guild_name = str(ctx.guild.name)
        user = str(ctx.author.display_name)
        voice_channel = ctx.author.voice.channel

        self.servers[guild_id]["queue"].append({
          "title": title,
          "url": url2,
          "vc": voice_channel,
          "yt_url": yt_url,
          "requested_by": user
        })
        await ctx.send("Song added to queue!")
        self.log_song(guild_id, guild_name, title, url2, yt_url)
        
        if (self.servers[guild_id]["vc"] is None) or (not self.servers[guild_id]["vc"].is_connected()):
          self.servers[guild_id]["vc"] = await self.servers[guild_id]["queue"][0]["vc"].connect()
        else:
          await self.servers[guild_id]["vc"].move_to(self.servers[guild_id]["queue"][0]["vc"])

        if ctx.voice_client.is_playing() == False:
          song = self.servers[guild_id]["queue"].pop(0)
          url_m = song["url"]
          self.servers[guild_id]["vc"].play(
            discord.FFmpegOpusAudio(url_m, **self.FFMPEG_OPTIONS),
            after=lambda e: self.play_next(guild_id)
          )

  @commands.command(name="pause")
  async def pause(self, ctx):
    if ctx.voice_client is not None:
      if ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("Paused ⏸")
      else:
        await ctx.send("There is no song to pause.")
    else:
      await ctx.send("There is no song to pause.")

  @commands.command(name="resume")
  async def resume(self, ctx):
    if ctx.voice_client is not None:
      if ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("Resumed ⏯")
      else:
        await ctx.send("There is no song to resume.")
    else:
      await ctx.send("There is no song to resume.")
  
  @commands.command(name="queue", aliases=["q"])
  async def queue(self, ctx):
    guild_id = str(ctx.guild.id)
    self.check_guild_id(guild_id)

    embed = discord.Embed(title=f"{ctx.guild.name}'s Music Queue", color=self.color)

    if len(self.servers[guild_id]["queue"]):
      for i in range(len(self.servers[guild_id]["queue"])):
        title = self.servers[guild_id]['queue'][i]['title']
        yt_url = self.servers[guild_id]['queue'][i]['yt_url']
        user = self.servers[guild_id]['queue'][i]['requested_by']
        embed.add_field(name=f"{i+1}. {title}", value=f"{yt_url} - {user}", inline=False)
    else:
      embed = embed.add_field(name="Songs:", value="`No songs in queue!`", inline=False)
    
    embed.set_footer(text=f"Requested by: {ctx.author.name}")
    await ctx.send(embed=embed)

  @commands.command(name="status", aliases=["stats"])
  async def status(self, ctx):
    if ctx.voice_client is not None:
      await ctx.send("Playing: " + str(ctx.voice_client.is_playing()))
    else:
      await ctx.send("Playing: False")

  @commands.command(name="clear", aliases=["cls", "kill"])
  async def clear(self, ctx):
    guild_id = str(ctx.guild.id)
    self.check_guild_id(guild_id)
    
    if len(self.servers[guild_id]["queue"]) > 0:
      self.servers[guild_id]["queue"].clear()
      await ctx.send("Queue cleared")
    else:
      await ctx.send("There is no queue to clear")

  @commands.command(name="next", aliases=["skip"])
  async def next(self, ctx):
    guild_id = str(ctx.guild.id)
    self.check_guild_id(guild_id)
    if ctx.voice_client is None:
      await ctx.send("Bot not in voice channel")
    else:

      if len(self.servers[guild_id]["queue"]) > 0:
        self.servers[guild_id]["vc"].stop()
        await ctx.send("Next song playing ⏯")
      else:
        self.servers[guild_id]["vc"].stop()
        await ctx.send("No more song in queue to play.")
