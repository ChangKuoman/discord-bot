import discord
from discord.ext import commands
import youtube_dl

class Music(commands.Cog):
  def __init__(self, client):
    
    self.client = client
    self.FFMPEG_OPTIONS = {
      'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
      'options': '-vn'
    }
    self.servers = {}
    self.queue = []
    self.vc = None

  def play_next(self, guild_id):
    if len(self.servers[guild_id]["queue"]) > 0:
      url_m = self.servers[guild_id]["queue"][0]["url"]
      self.servers[guild_id]["queue"].pop(0)
      self.servers[guild_id]["vc"].play(discord.FFmpegOpusAudio(url_m, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(guild_id))

  def check_guild_id(self, guild_id):
    if guild_id not in self.servers.keys():
      self.servers[guild_id] = {"queue": [], "vc": None}

  @commands.command(name="join", aliases=["connect"])
  async def join(self, ctx):
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
        # self.servers[guild_id]["vc"] = await ctx.voice_client.move_to(voice_channel)
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
  async def play(self, ctx, url):
    if ctx.author.voice is None:
      await ctx.send("You're not in a voice channel!")
    elif ctx.voice_client is None:
      await ctx.send("Bot is not in a voice channel!")
    else:
      YDL_OPTIONS = {"format":"bestaudio"}
      with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        error = False
        try:
          info = ydl.extract_info(url, download=False)
          url2 = info["formats"][0]["url"]
          title = info["title"]
        except:
          error = True
      if not error:
        guild_id = str(ctx.guild.id)
        voice_channel = ctx.author.voice.channel

        self.servers[guild_id]["queue"].append({"title": title, "url": url2, "vc": voice_channel})
        await ctx.send("Song added to queue!")

        if self.servers[guild_id]["vc"] is None or not self.servers[guild_id]["vc"].is_connected():
          self.servers[guild_id]["vc"] = await self.servers[guild_id]["queue"][0]["vc"].connect()
        else:
          await self.servers[guild_id]["vc"].move_to(self.servers[guild_id]["queue"][0]["vc"])

        if ctx.voice_client.is_playing() == False:
          url_m = self.servers[guild_id]["queue"][0]["url"]
          self.servers[guild_id]["queue"].pop(0)
          self.servers[guild_id]["vc"].play(discord.FFmpegOpusAudio(url_m, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(guild_id))
      else:
        await ctx.send("You must put a valid url!")

  @commands.command()
  async def pause(self, ctx):
    if ctx.voice_client is not None:
      if ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("Paused ⏸")
      else:
        await ctx.send("There is no song to pause.")
    else:
      await ctx.send("There is no song to pause.")

  @commands.command()
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
    
    if len(self.servers[guild_id]["queue"]):
      response = ""
      for i in range(len(self.servers[guild_id]["queue"])):
        response += str(i+1) + ". " + self.servers[guild_id]["queue"][i]["title"] + '\n'
    else:
      response = "There are no songs is queue."
    await ctx.send(response)

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

      
def setup(client):
  client.add_cog(Music(client))
