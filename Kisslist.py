from discord.ext import commands
from replit import db

class Kisslist(commands.Cog):
  if "kisslist" not in db.keys():
    db["kisslist"] = {}
  
  def __init__(self, client):
    self.client = client
    self.numbers = {
      "0": "0️⃣",
      "1": "1️⃣",
      "2": "2️⃣",
      "3": "3️⃣",
      "4": "4️⃣",
      "5": "5️⃣",
      "6": "6️⃣",
      "7": "7️⃣",
      "8": "8️⃣",
      "9": "9️⃣"
    }

  # checks author in kisslist db
  def check_author(self, author_id):
    if author_id not in db["kisslist"].keys():
      list = {}
      for i in range(65, 91):
        list[chr(i)] = 0
      db["kisslist"][author_id] = list

  # shows kisslist
  def show(self, author_id, author_name):
    self.check_author(author_id)

    list = author_name + " KISSLIST:\n"
    for key, value in db["kisslist"][author_id].items():
      list += key + " - "
      if value:
        list += "✅"
      else:
        list += "❌"
      list += '\n'
    return list

  # shows all kisslist
  def show_all(self, author_id, author_name):
    self.check_author(author_id)

    list = author_name + " KISSLIST:\n"
    for key, value in db["kisslist"][author_id].items():
      list += key + " - "
      if value:
        for i in range(value):
          list += "✅"
      else:
        list += "❌"
      list += '\n'
    return list

  # shows numbers kisslist
  def show_number(self, author_id, author_name):
    self.check_author(author_id)

    list = author_name + " KISSLIST:\n"
    for key, value in db["kisslist"][author_id].items():
      list += key + " - "
      for number in str(value):
        list += self.numbers[number]
      list += '\n'
    return list
    
  #delete kisslist
  def delete(self, author_id):    
    if author_id in db["kisslist"]:
      del db["kisslist"][author_id]
      return "Kisslist deleted"
    else:
      return "No kisslist was found to delete"

  #creates kisslist
  def create(self, author_id):
    if author_id not in db["kisslist"].keys():
      self.check_author(author_id)
      return "Kisslist created"
    else:
      return "Kisslist already in database"

  # add letters to kisslist
  def add(self, author_id, words):
    self.check_author(author_id)
    added = ""
    
    for word in words:
      letter = str(word).upper()[0]
      if ord(letter) in range(65, 91):
        db["kisslist"][author_id][letter] += 1
        added += "Letter " + letter + " added to kisslist\n"
    return added

  # remove letters from kisslist
  def remove(self, author_id, words):
    if author_id not in db["kisslist"].keys():
      self.check_author(author_id)
    else:
      removed = ""
      for word in words:
        letter = str(word).upper()[0]
        if ord(letter) in range(65, 91):
          if db["kisslist"][author_id][letter] - 1 >= 0:
            db["kisslist"][author_id][letter] -= 1
            removed += "Letter " + letter + " removed from kisslist\n"
    return removed

  # set letter to number
  def set(self, author_id, letter, number):
    self.check_author(author_id)
    letter = str(letter).upper()[0]
    number = str(number)
    if ord(letter) not in range(65, 91):
      return "No valid letter"
    if number.isdigit() == False:
      return "No valid number"
    number = int(number)
    if number < 0:
      return "No valid number"
    db["kisslist"][author_id][letter] = number
    return "Letter " + letter + " set to " + str(number)

  #help
  def help(self):
    message = """
```
KISSLIST HELP:
Base command: kisslist | kl
Subcommands:
  + help -> shows commands
  + show [None] [all] [number | numbers] -> show kisslist
  + add [letter(s)] -> add letter(s) to kisslist
  + remove [letter(s)] -> remove letter(s) from kisslist
  + set [letter] [number] -> sets letter to number
  + delete -> deletes kisslist
  + create -> creates kisslist
```
    """
    return message

  # commands
  @commands.command(name="kisslist", aliases=["kl"])
  async def kisslist(self, ctx, *msg):
    if len(msg) == 0:
      await ctx.send("Command Not Found :(")
    else:
      author_id = str(ctx.author.id)
      author_name = str(ctx.author)
      if msg[0] == "help":
        response = self.help()
        await ctx.send(response)

      elif msg[0] == "show":
        if len(msg) == 1:
          response = self.show(author_id, author_name)
        elif len(msg) == 2 and msg[1] == "all":
          response = self.show_all(author_id, author_name)
        elif len(msg) == 2 and msg[1] in ["number", "numbers"]:
          response = self.show_number(author_id, author_name)
        else:
          response = "Command Not Found! - show"
        await ctx.send(response)

      elif msg[0] == "delete":
        if len(msg) == 1:
          response = self.delete(author_id)
        else:
          response = "Command Not Found! - delete"
        await ctx.send(response)

      elif msg[0] == "create":
        if len(msg) == 1:
          response = self.create(author_id)
        else:
          response = "Command Not Found! - create"
        await ctx.send(response)
        
      elif msg[0] == "add":
        response = self.add(author_id, msg[1::])
        if response == "":
          response = "No letters where added."
        await ctx.send(response)
      
      elif msg[0] == "remove":
        response = self.remove(author_id, msg[1::])
        if response == "":
          response = "No letters where removed."
        await ctx.send(response)

      elif msg[0] == "set":
        if len(msg) == 3:
          response = self.set(author_id, msg[1], msg[2])
        else:
          response = "Command Not Found! - set"
        await ctx.send(response)

      else:
        await ctx.send("Command Not Found! - commands")

def setup(client):
  client.add_cog(Kisslist(client))
