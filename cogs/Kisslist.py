from discord.ext import commands
from replit import db
from discord import Embed

if "kisslist" not in db.keys():
  db["kisslist"] = {}

class Kisslist(commands.Cog):
  """Commands for kisslist related stuff"""

  def __init__(self, client):
    self.CLIENT = client
    self.COLOR = 0xFF5F13
    self.NUMBERS = {
      "0": "0️⃣", "1": "1️⃣", "2": "2️⃣", "3": "3️⃣", "4": "4️⃣",
      "5": "5️⃣", "6": "6️⃣", "7": "7️⃣", "8": "8️⃣", "9": "9️⃣"
    }
    self.LETTERS = {
      "A": "🇦", "B": "🇧", "C": "🇨", "D": "🇩", "E": "🇪", "F": "🇫",
      "G": "🇬", "H": "🇭", "I": "🇮", "J": "🇯", "K": "🇰", "L": "🇱",
      "M": "🇲", "N": "🇳", "O": "🇴", "P": "🇵", "Q": "🇶", "R": "🇷",
      "S": "🇸", "T": "🇹", "U": "🇺", "V": "🇻", "W": "🇼", "X": "🇽",
      "Y": "🇾", "Z": "🇿"
    }

  @commands.group(name="kisslist", aliases=["kl"], invoke_without_command=False, help="Base command for kisslist group")
  async def kisslist(self, ctx):
    author_id = str(ctx.author.id)
    if author_id not in db["kisslist"].keys():
      list = {}
      for i in range(65, 91):
        list[chr(i)] = 0
      db["kisslist"][author_id] = list
  
  @kisslist.command(name="show", help="Sends kisslist [None | all | number | numbers]")
  async def kisslist_show(self, ctx, msg=None):
    author_id = str(ctx.author.id)
    author_name = str(ctx.author.display_name)
    description = ""
    if msg is None:
      for key, value in db["kisslist"][author_id].items():
        emoji = "✅" if value else "❌"
        description += f"{self.LETTERS[key]}: {emoji}\n"
    elif msg == "all":
      for key, value in db["kisslist"][author_id].items():
        emoji = "✅"*value if value else "❌"
        description += f"{self.LETTERS[key]}: {emoji}\n"
    elif msg in ["number", "numbers"]:
      for key, value in db["kisslist"][author_id].items():
        emoji = ""
        for number in str(value):
          emoji += self.NUMBERS[number]
        description += f"{self.LETTERS[key]}: {emoji}\n"
    else:
      description = "Kisslist show command not found!"
    embed = Embed(
      title=f"{author_name}'s KISSLIST",
      description=description,
      color=self.COLOR
    )
    await ctx.send(embed=embed)

  @kisslist.command(name="clear", help="Clears kisslist")
  async def kisslist_clear(self, ctx):
    author_id = str(ctx.author.id)
    del db["kisslist"][author_id]
    embed = Embed(
      description="Kisslist cleared",
      color=self.COLOR
    )
    await ctx.send(embed=embed)

  @kisslist.command(name="add", help="Add letter(s) to kisslist [letter(s)]")
  async def kisslist_add(self, ctx, *msg):
    author_id = str(ctx.author.id)
    description = ""
    for word in msg:
      letter = str(word).upper()[0]
      if ord(letter) in range(65, 91):
        db["kisslist"][author_id][letter] += 1
        description += "Letter " + letter + " added to kisslist\n"
    if description == "":
      description = "No letters where added."
    embed = Embed(
      description=description,
      color=self.COLOR
    )
    await ctx.send(embed=embed)

  @kisslist.command(name="remove", aliases=["delete"], help="Remove letter(s) from kisslist [letter(s)]")
  async def kisslist_remove(self, ctx, *msg):
    author_id = str(ctx.author.id)
    description = ""
    for word in msg:
      letter = str(word).upper()[0]
      if ord(letter) in range(65, 91):
        if db["kisslist"][author_id][letter] - 1 >= 0:
          db["kisslist"][author_id][letter] -= 1
          description += "Letter " + letter + " removed from kisslist\n"
    if description == "":
      description = "No letters where removed."
    embed = Embed(
      description=description,
      color=self.COLOR
    )
    await ctx.send(embed=embed)

  @kisslist.command(name="set", help="Sets letter to number [letter][number]")
  async def kisslist_set(self, ctx, letter, number):
    author_id = str(ctx.author.id)
    letter = str(letter).upper()[0]
    number = str(number)
    if ord(letter) not in range(65, 91):
      description = "No valid letter"
    elif number.isdigit() == False or int(number) < 0:
      description = "No valid number"
    else:
      db["kisslist"][author_id][letter] = int(number)
      description = "Letter " + letter + " set to " + number
    embed = Embed(
      description=description,
      color=self.COLOR
    )
    await ctx.send(embed=embed)
