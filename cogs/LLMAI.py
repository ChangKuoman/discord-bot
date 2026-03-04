from discord.ext import commands
import discord
import os
from gtts import gTTS
from google import genai
import asyncio
from dotenv import load_dotenv
from .utils import init_db, whitelisted_only, add_to_whitelist, remove_from_whitelist
from typing import Literal

class LLMAI(commands.Cog):
  """Commands for using AI"""

  def __init__(self, client):
    self.CLIENT = client
    self.COLOR = 0xFF0000
    load_dotenv()
    API_KEY = os.getenv("GOOGLE_API_KEY")

    init_db()

    self.GEMINI_CLIENT = genai.Client(api_key=API_KEY)
    self.GEMINI_MODEL = "gemma-3-27b-it" # prev model was deprecated
    self.FILE_PATH = "assets/downloads/gemini.mp3"

  @commands.command(name="whitelist", help="adds or remove from whitelist", aliases=["wl"])
  @commands.is_owner()
  async def whitelist(self, ctx, action: Literal["add", "remove"], user: discord.User):

    if action == "add":

      if add_to_whitelist(user.id):
          answer = f"✅ {user.name} has been added to the whitelist."
      else:
          answer = f"ℹ️ {user.name} is already on the whitelist."

    elif action == "remove":

      if remove_from_whitelist(user.id):
          answer = f"✅ {user.name} has been removed from the whitelist."
      else:
          answer = f"⚠️ {user.name} was not on the whitelist to begin with."

    embed = discord.Embed(
      title="WHITELIST UPDATE",
      description=answer,
      color=self.COLOR
    )
    await ctx.send(embed=embed)

  @whitelist.error
  async def whitelist_error(self, ctx, error):
    if isinstance(error, commands.UserNotFound):
        message = "❌ I couldn't find that user. Please mention them or use their ID."
    elif isinstance(error, commands.CheckFailure):
      if isinstance(error, commands.NotOwner):
        message = "⛔ Only the bot owner can use this."
      else:
        message = "🚫 You are not authorized to use this feature."
    elif isinstance(error, commands.MissingRequiredArgument):
        message = "❓ Missing arguments! Usage: `!wl <add|remove> <user>`"
    else:
        message = f"Unhandled error: {error}"

    embed = discord.Embed(
      title="FOCA BOT ERROR",
      description=message,
      color=self.COLOR
    )

    await ctx.send(embed=embed)

  @commands.command(name="asks", help="Briefly answer a question using AI.")
  @whitelisted_only()
  async def asks(self, ctx, *msg):
    msg = " ".join(msg)
    response = self.GEMINI_CLIENT.models.generate_content(
        model=self.GEMINI_MODEL, contents=f"In just 1 paragraph (less than 500 characters): {msg}"
    )
    answer = response.text

    embed = discord.Embed(
      title="FOCA-BOT ANSWERS",
      description=answer,
      color=self.COLOR
    )
    await ctx.send(embed=embed)

  @commands.command(name="ask", help="Answer a question using AI.")
  @whitelisted_only()
  async def ask(self, ctx, *msg):
    msg = " ".join(msg)
    response = self.GEMINI_CLIENT.models.generate_content(
        model=self.GEMINI_MODEL, contents=f"In less than 4096 characters: {msg}"
    )
    answer = response.text

    embed = discord.Embed(
      title="FOCA-BOT ANSWERS",
      description=answer,
      color=self.COLOR
    )
    await ctx.send(embed=embed)

  @commands.command(name="asktts", help="Briefly answer a question using AI and TTS.")
  @whitelisted_only()
  async def asktts(self, ctx, *msg):
    msg = " ".join(msg)
    response = self.GEMINI_CLIENT.models.generate_content(
        model=self.GEMINI_MODEL, contents=f"In less than 4096 characters: {msg}"
    )
    answer = response.text
    tts = gTTS(answer, lang='en')
    tts.save(self.FILE_PATH)

    embed = discord.Embed(
      title="FOCA-BOT ANSWERS: TRANSCRIPT",
      description=answer,
      color=self.COLOR
    )

    if ctx.author.voice is None:
      embed.set_footer(text="❌ You're not in a voice channel!")
    else:
      voice_client = ctx.guild.voice_client
      if voice_client is None:
        channel = ctx.author.voice.channel
        voice_client = await channel.connect()

        def play_next(ctx):
          coro = ctx.voice_client.disconnect()
          fut = asyncio.run_coroutine_threadsafe(coro, self.CLIENT.loop)

        voice_client.play(
          discord.FFmpegPCMAudio(self.FILE_PATH),
          after=lambda e: play_next(ctx)
        )

      elif voice_client.is_playing():
        embed.set_footer(text="❌ You're already playing audio!")

      elif ctx.guild.voice_client.channel != ctx.author.voice.channel:
        await voice_client.move_to(ctx.author.voice.channel)
        voice_client.play(discord.FFmpegPCMAudio(self.FILE_PATH))

    await ctx.send(embed=embed)
