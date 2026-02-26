from discord.ext import commands
import discord
import os
from gtts import gTTS
from google import genai
import asyncio

class LLMAI(commands.Cog):
  """Commands for using AI"""

  def __init__(self, client):
    self.CLIENT = client
    self.COLOR = 0xFF0000
    API_KEY = os.getenv("GOOGLE_API_KEY")

    self.GEMINI_CLIENT = genai.Client(api_key=API_KEY)
    self.GEMINI_MODEL = "gemini-2.0-flash"
    self.FILE_PATH = "assets/downloads/gemini.mp3"

  @commands.command(name="asks", help="Briefly answer a question using AI.")
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
