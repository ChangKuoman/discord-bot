import discord
from discord.ext import commands
import yt_dlp
import re
import json
import os
from modules import YoutubeSearch

class Music(commands.Cog):
  """Commands for playing music in server"""

  def __init__(self, client):
    self.servers = {}
    self.CLIENT = client
    self.COLOR = 0x28B4FF
    self.QUEUE_PAGINATION = 5
    self.FFMPEG_OPTIONS = {
      'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
      'options': '-vn'
    }
    with open("assets/regex.json", "r") as file:
      data = json.load(file)
    self.REGEX = re.compile(f"{data['url']}")
    self.OUTPUT_PATH = "assets/downloads/output.m4a"
    try:
      if os.path.exists(self.OUTPUT_PATH):
        os.remove(self.OUTPUT_PATH)
    except Exception as e:
      print(f"Error: {e}")

  def __del__(self):
    try:
      if os.path.exists(self.OUTPUT_PATH):
        os.remove(self.OUTPUT_PATH)
    except Exception as e:
      print(f"Error: {e}")

  def play_next(self, guild_id):
    # deletes file after playing
    if os.path.exists(self.OUTPUT_PATH):
      os.remove(self.OUTPUT_PATH)

    if len(self.servers[guild_id]["queue"]) > 0:
      song = self.servers[guild_id]["queue"].pop(0)
      url = song["url"]

      opts = { 'outtmpl': self.OUTPUT_PATH, 'format': 'best', }
      try:
          with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
      except Exception as e:
          print(f"Error: {e}")

      self.servers[guild_id]["vc"].play(
        discord.FFmpegPCMAudio(self.OUTPUT_PATH),
        after=lambda e: self.play_next(guild_id)
      )
      self.servers[guild_id]["playing"] = song
    else:
      self.servers[guild_id]["playing"] = None

  def check_guild_id(self, guild_id):
    if guild_id not in self.servers.keys():
      self.servers[guild_id] = {"queue": [], "vc": None, "playing": None}

  async def send_basic_embed(self, ctx, description):
    embed = discord.Embed(
      description=description,
      color=self.COLOR
    )
    await ctx.send(embed=embed)

  @commands.command(name="connect", aliases=["join"], help="Bot joins channel")
  async def connect(self, ctx):
    guild_id = str(ctx.guild.id)
    self.check_guild_id(guild_id)
    if ctx.author.voice is None:
      description = "❌ You're not in a voice channel!"
    elif ctx.voice_client is None:
      self.servers[guild_id]["vc"] = await ctx.author.voice.channel.connect()
      description = "🔗 Connected"
    else:
      await ctx.voice_client.disconnect()
      self.servers[guild_id]["vc"] = await ctx.author.voice.channel.connect()
      description = "🚚 Moved"
    await self.send_basic_embed(ctx, description)

  @commands.command(name="disconnect", aliases=["leave"], help="Bot leaves channel")
  async def disconnect(self, ctx):
    guild_id = str(ctx.guild.id)
    self.check_guild_id(guild_id)

    if ctx.voice_client is not None:
      if len(self.servers[guild_id]["queue"]) > 0:
        self.servers[guild_id]["queue"].clear()
      if ctx.voice_client.is_playing():
        ctx.voice_client.stop()

      await ctx.voice_client.disconnect()
      description = "🍂 Disconnected"
    else:
      description = "❌ Bot not in voice channel"
    await self.send_basic_embed(ctx, description)

  @commands.command(name="pause", help="Pauses song")
  async def pause(self, ctx):
    if ctx.voice_client is not None and ctx.voice_client.is_playing():
      ctx.voice_client.pause()
      description = "⏸ Paused"
    else:
      description = "❌ There is no song to pause"
    await self.send_basic_embed(ctx, description)

  @commands.command(name="resume", help="Resumes song")
  async def resume(self, ctx):
    if ctx.voice_client is not None and ctx.voice_client.is_paused():
      ctx.voice_client.resume()
      description = "▶️ Resumed"
    else:
      description = "❌ There is no song to resume"
    await self.send_basic_embed(ctx, description)

  @commands.command(name="status", aliases=["stats"], help="Info of playing song")
  async def status(self, ctx):
    guild_id = str(ctx.guild.id)
    self.check_guild_id(guild_id)
    embed = discord.Embed(title="🎵 Music Status", color=self.COLOR)

    if ctx.voice_client is not None:
      embed.add_field(name="Playing:", value=f"`{str(ctx.voice_client.is_playing())}`", inline=False)
      if self.servers[guild_id]["playing"] is not None:
        embed.add_field(name="Song:", value=f"`{self.servers[guild_id]['playing']['title']}`", inline=False)
        embed.add_field(name="URL:", value=f"`{self.servers[guild_id]['playing']['url']}`", inline=False)
    else:
      embed.add_field(name="Playing:", value=f"`False`", inline=False)
    await ctx.send(embed=embed)

  @commands.command(name="clear", aliases=["cls", "kill"], help="Clears all song queue")
  async def clear(self, ctx):
    guild_id = str(ctx.guild.id)
    self.check_guild_id(guild_id)
    if len(self.servers[guild_id]["queue"]) > 0:
      self.servers[guild_id]["queue"].clear()
      description = "🗑️ Queue cleared"
    else:
      description = "❌ There is no queue to clear"
    await self.send_basic_embed(ctx, description)

  @commands.command(name="queue", aliases=["q"], help="Sends songs queue")
  async def queue(self, ctx):
    guild_id = str(ctx.guild.id)
    self.check_guild_id(guild_id)

    def pagination(pages, page, embed):
      embed.clear_fields()
      for i in range(len(pages[page])):
        title = pages[page][i]['title']
        yt_url = pages[page][i]['url']
        user = pages[page][i]['requested_by']
        embed.add_field(
          name=f"{i+1 + page*self.QUEUE_PAGINATION}. {title}",
          value=f"{yt_url} - {user}",
          inline=False
        )
      embed.set_footer(text=f"Page {page + 1}/{len(pages)}")

    embed = discord.Embed(
      title=f"🎵 {ctx.guild.name}'s Music Queue",
      color=self.COLOR
    )
    list_songs = self.servers[guild_id]["queue"]
    if len(list_songs) == 0:
      embed = embed.add_field(name="Songs:", value="`No songs in queue!`", inline=False)
      await ctx.send(embed=embed)
    else:
      pages = [list_songs[i:i + self.QUEUE_PAGINATION] for i in range(0, len(list_songs), self.QUEUE_PAGINATION)]
      page = 0

      pagination(pages, page, embed)
      message = await ctx.send(embed=embed)
      await message.add_reaction("⬅️")
      await message.add_reaction("➡️")
      await message.add_reaction("❌")

      while True:
        def check(reaction, user):
          return (user == ctx.author
                  and str(reaction.emoji) in ["⬅️", "➡️", "❌"]
                  and reaction.message.id == message.id)
        try:
          reaction, user = await self.CLIENT.wait_for("reaction_add", timeout=20.0, check=check)

          if str(reaction.emoji) == "⬅️":
            await message.remove_reaction("⬅️", user)
            if page == 0:
              continue
            page -= 1
            pagination(pages, page, embed)
            await message.edit(embed=embed)

          elif str(reaction.emoji) == "➡️":
            await message.remove_reaction("➡️", user)
            if page == len(pages) - 1:
              continue
            page += 1
            pagination(pages, page, embed)
            await message.edit(embed=embed)

          elif str(reaction.emoji) == "❌":
            await message.clear_reactions()
            page = 0
            pagination(pages, page, embed)
            await message.edit(embed=embed)
            break

        except:
          await message.clear_reactions()
          page = 0
          pagination(pages, page, embed)
          await message.edit(embed=embed)
          break

  ### play functions

  def search_url(self, url):
    YDL_OPTIONS = {
        "format": "bestaudio/best",
        #"quiet": True,
        "playlist_items": "1-10",  # Specify the range of videos to extract
        "noplaylist": True,  # Disable playlist extraction
    }
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
      try:
        info = ydl.extract_info(url, download=False)
        return info
      except:
        return None

  def add_song(self, ctx, song):
    guild_id = str(ctx.guild.id)
    user = str(ctx.author.display_name)
    voice_channel = ctx.author.voice.channel
    title = song["title"]
    url = song["webpage_url"]


    self.servers[guild_id]["queue"].append({
      "url": url,
      "title": title,
      "vc": voice_channel,
      "requested_by": user
    })

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

      url = song["url"]
      opts = { 'outtmpl': self.OUTPUT_PATH, 'format': 'best', }
      try:
          with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
      except Exception as e:
          print(f"Error: {e}")

      self.servers[guild_id]["vc"].play(
        discord.FFmpegPCMAudio(self.OUTPUT_PATH),
        after=lambda e: self.play_next(guild_id)
      )
      self.servers[guild_id]["playing"] = song

  async def set_one_song(self, ctx, response, message=None):
    self.add_song(ctx, response)
    embed = discord.Embed(
      description="🎵 Song added to queue!",
      color=self.COLOR
    )
    if message:
      await message.edit(embed=embed)
    else:
      await ctx.send(embed=embed)
    await self.move_client(ctx)
    await self.play_song(ctx)

  async def set_playlist(self, ctx, response):
    for entry in response["entries"]:
      self.add_song(ctx, entry)
    await self.send_basic_embed(ctx, "🎵 Playlist added to queue!")
    await self.move_client(ctx)
    await self.play_song(ctx)

  @commands.command(name="play", aliases=["p", "add"], help="Add to queue song [url song | url playlist | search]")
  async def play(self, ctx, *msg):

    guild_id = str(ctx.guild.id)
    self.check_guild_id(guild_id)

    if ctx.author.voice is None:
      await self.send_basic_embed(ctx, "❌ You're not in a voice channel!")
    elif len(msg) == 0:
      await self.send_basic_embed(ctx, "❌ You must put a valid url/search!")

    # when is url:
    elif len(msg) == 1 and self.REGEX.match(msg[0]):
      ###
      if "spotify" in msg[0] or "apple" in msg[0]:
        await self.send_basic_embed(ctx, "😪 We're sorry, but currently we don't support spotify or apple music links")
      else:
      ###
        response = self.search_url(msg[0])
        if response is None:
          await self.send_basic_embed(ctx, "❌ You must put a valid url!")
        else:
          if "playlist" in msg[0]:
            await self.set_playlist(ctx, response)
          else:
            await self.set_one_song(ctx, response)
    else:

      results = json.loads(YoutubeSearch(" ".join(msg), max_results=5).to_json())

      a, b, c, d, e = results["videos"]
      songs=f"""🇦 `{a['title']}` - {a['channel']} - {a['duration']}
  🇧 `{b['title']}` - {b['channel']} - {b['duration']}
  🇨 `{c['title']}` - {c['channel']} - {c['duration']}
  🇩 `{d['title']}` - {d['channel']} - {d['duration']}
  🇪 `{e['title']}` - {e['channel']} - {e['duration']}
  """
      embed = discord.Embed(
        title="Choose a song",
        description=songs,
        color=self.COLOR
      )

      message = await ctx.send(embed=embed)
      await message.add_reaction("🇦")
      await message.add_reaction("🇧")
      await message.add_reaction("🇨")
      await message.add_reaction("🇩")
      await message.add_reaction("🇪")

      def check(reaction, user):
        return (user == ctx.author
                and str(reaction.emoji) in ["🇦", "🇧", "🇨", "🇩", "🇪"]
                and reaction.message.id == message.id)

      error = False
      try:
        reaction, user = await self.CLIENT.wait_for("reaction_add", timeout=15.0, check=check)
        embed = discord.Embed(
          description="🔎 Searching song!",
          color=self.COLOR
        )
        await message.remove_reaction(reaction, user)
        await message.clear_reactions()
        await message.edit(embed=embed)
      except:
        error = True
        embed = discord.Embed(
          description="❌ You took too long to choose!",
          color=self.COLOR
        )
        await message.clear_reactions()
        await message.edit(embed=embed)

      if not error:
        if str(reaction.emoji) == "🇦":
          url = "https://www.youtube.com" + a["url_suffix"]
        elif str(reaction.emoji) == "🇧":
          url = "https://www.youtube.com" + b["url_suffix"]
        elif str(reaction.emoji) == "🇨":
          url = "https://www.youtube.com" + c["url_suffix"]
        elif str(reaction.emoji) == "🇩":
          url = "https://www.youtube.com" + d["url_suffix"]
        elif str(reaction.emoji) == "🇪":
          url = "https://www.youtube.com" + e["url_suffix"]

        response = self.search_url(url)
        if response is None:
          await self.send_basic_embed(ctx, "❌ Something went wrong!")
        else:
          await self.set_one_song(ctx, response, message)