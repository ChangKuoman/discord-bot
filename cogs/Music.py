import discord
from discord.ext import commands
import youtube_dl
from youtube_search import YoutubeSearch
from datetime import datetime, timedelta
import re

class Music(commands.Cog):
  def __init__(self, client):
    self.client = client
    self.FFMPEG_OPTIONS = {
      'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
      'options': '-vn'
    }
    self.servers = {}
    self.color = 0x28B4FF
    self.regex = re.compile('^(?!mailto:)(?:(?:http|https|ftp)://)(?:\\S+(?::\\S*)?@)?(?:(?:(?:[1-9]\\d?|1\\d\\d|2[01]\\d|22[0-3])(?:\\.(?:1?\\d{1,2}|2[0-4]\\d|25[0-5])){2}(?:\\.(?:[0-9]\\d?|1\\d\\d|2[0-4]\\d|25[0-4]))|(?:(?:[a-z\\u00a1-\\uffff0-9]+-?)*[a-z\\u00a1-\\uffff0-9]+)(?:\\.(?:[a-z\\u00a1-\\uffff0-9]+-?)*[a-z\\u00a1-\\uffff0-9]+)*(?:\\.(?:[a-z\\u00a1-\\uffff]{2,})))|localhost)(?::\\d{2,5})?(?:(/|\\?|#)[^\\s]*)?$')

  def play_next(self, guild_id):
    if len(self.servers[guild_id]["queue"]) > 0:
      song = self.servers[guild_id]["queue"].pop(0)
      url = song["url"]
      self.servers[guild_id]["vc"].play(
        discord.FFmpegOpusAudio(url, **self.FFMPEG_OPTIONS),
        after=lambda e: self.play_next(guild_id)
      )
      self.servers[guild_id]["playing"] = song
    else:
      self.servers[guild_id]["playing"] = None
      
  def check_guild_id(self, guild_id):
    if guild_id not in self.servers.keys():
      self.servers[guild_id] = {"queue": [], "vc": None, "playing": None}

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

  @commands.command(name="status", aliases=["stats"])
  async def status(self, ctx):
    guild_id = str(ctx.guild.id)
    self.check_guild_id(guild_id)

    embed = discord.Embed(title="Music Status", color=self.color)
    
    if ctx.voice_client is not None:
      embed.add_field(name="Playing:", value=f"`{str(ctx.voice_client.is_playing())}`", inline=False)
      if self.servers[guild_id]["playing"] is not None:
        embed.add_field(name="Song:", value=f"`{self.servers[guild_id]['playing']['title']}`", inline=False)
        embed.add_field(name="URL:", value=f"`{self.servers[guild_id]['playing']['yt_url']}`", inline=False)
    else:
      embed.add_field(name="Playing:", value=f"`{str(ctx.voice_client.is_playing())}`", inline=False)
    await ctx.send(embed=embed)

  @commands.command(name="clear", aliases=["cls", "kill"])
  async def clear(self, ctx):
    guild_id = str(ctx.guild.id)
    self.check_guild_id(guild_id)
    
    if len(self.servers[guild_id]["queue"]) > 0:
      self.servers[guild_id]["queue"].clear()
      await ctx.send("Queue cleared")
    else:
      await ctx.send("There is no queue to clear")

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

  ### play functions

  def search_url(self, url):
    YDL_OPTIONS = {"format":"bestaudio"}
    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
      try:
        info = ydl.extract_info(url, download=False)
        return info
      except:
        return None

  def add_song(self, ctx, song):
    guild_id = str(ctx.guild.id)
    guild_name = str(ctx.guild.name)
    user = str(ctx.author.display_name)
    voice_channel = ctx.author.voice.channel
    url = song["formats"][0]["url"]
    title = song["title"]
    yt_url = song["webpage_url"]

    self.servers[guild_id]["queue"].append({
      "title": title,
      "url": url,
      "vc": voice_channel,
      "yt_url": yt_url,
      "requested_by": user
    })
    self.log_song(guild_id, guild_name, title, url, yt_url)

  async def move_client(self, ctx):
    guild_id = str(ctx.guild.id)
    if (self.servers[guild_id]["vc"] is None) or (not self.servers[guild_id]["vc"].is_connected()):
      self.servers[guild_id]["vc"] = await self.servers[guild_id]["queue"][0]["vc"].connect()
    else:
      await self.servers[guild_id]["vc"].move_to(self.servers[guild_id]["queue"][0]["vc"])

  async def play_song(self, ctx):
    guild_id = str(ctx.guild.id)
    if ctx.voice_client.is_playing() == False:
      song = self.servers[guild_id]["queue"].pop(0)
      url_m = song["url"]
      self.servers[guild_id]["vc"].play(
        discord.FFmpegOpusAudio(url_m, **self.FFMPEG_OPTIONS),
        after=lambda e: self.play_next(guild_id)
      )
      self.servers[guild_id]["playing"] = song

  async def set_one_song(self, ctx, response, message=None):
    self.add_song(ctx, response)
    embed = discord.Embed(description="🎵 Song added to queue!")
    if message:
      await message.edit(embed=embed)
    else:
      await ctx.send(embed=embed)
    await self.move_client(ctx)
    await self.play_song(ctx)

  async def set_playlist(self, ctx, response):
    for entry in response["entries"]:
      self.add_song(ctx, entry)
    embed = discord.Embed(description=f"🎵 Playlist added to queue!")
    await ctx.send(embed=embed)
    await self.move_client(ctx)
    await self.play_song(ctx)

  @commands.command(name="play", aliases=["p", "add"])
  async def play(self, ctx, *msg):
    guild_id = str(ctx.guild.id)
    self.check_guild_id(guild_id)

    if ctx.author.voice is None:
      await ctx.send("You're not in a voice channel!")
    elif len(msg) == 0:
      await ctx.send("You must put a valid url/search!")
    
    # when is url:
    elif len(msg) == 1 and self.regex.match(msg[0]):
      response = self.search_url(msg[0])
      if response is None:
        await ctx.send("You must put a valid url!")
      else:
        if "playlist" in msg[0]:
          await self.set_playlist(ctx, response)
        else:
          await self.set_one_song(ctx, response)
    # when is search
    else:
      search = " ".join(msg)
      results = YoutubeSearch(search, max_results=5).to_dict()
  
      a, b, c, d, e = results
      songs=f"""🇦 `{a['title']}` - {a['channel']} - {a['duration']}
  🇧 `{b['title']}` - {b['channel']} - {b['duration']}
  🇨 `{c['title']}` - {c['channel']} - {c['duration']}
  🇩 `{d['title']}` - {d['channel']} - {d['duration']}
  🇪 `{e['title']}` - {e['channel']} - {e['duration']}
  """
      embed = discord.Embed(title="Choose a song", description=songs)
      
      message = await ctx.send(embed=embed)
      await message.add_reaction("🇦")
      await message.add_reaction("🇧")
      await message.add_reaction("🇨")
      await message.add_reaction("🇩")
      await message.add_reaction("🇪")
  
      def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["🇦", "🇧", "🇨", "🇩", "🇪"]

      error = False
      try:
        reaction, user = await self.client.wait_for("reaction_add", timeout=15.0, check=check)
        embed = discord.Embed(description="🔎 Searching song!")
        await message.remove_reaction(reaction, user)
        await message.clear_reactions()
        await message.edit(embed=embed)
      except:
        error = True
        embed = discord.Embed(description=":x: You took too long to choose!")
        await message.clear_reactions()
        await message.edit(embed=embed)

      if not error:
        if str(reaction.emoji) == "🇦":
          url = "https://www.youtube.com/" + a["url_suffix"]
        elif str(reaction.emoji) == "🇧":
          url = "https://www.youtube.com/" + b["url_suffix"]
        elif str(reaction.emoji) == "🇨":
          url = "https://www.youtube.com/" + c["url_suffix"]
        elif str(reaction.emoji) == "🇩":
          url = "https://www.youtube.com/" + d["url_suffix"]
        elif str(reaction.emoji) == "🇪":
          url = "https://www.youtube.com/" + e["url_suffix"]

        response = self.search_url(url)
        if response is None:
          await ctx.send("Something went wrong!")
        else:
          await self.set_one_song(ctx, response, message)
