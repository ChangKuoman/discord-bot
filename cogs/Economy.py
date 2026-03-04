from discord.ext import commands
from discord import Embed
from random import randint
from datetime import datetime, timedelta
import json
import shelve
from .utils import Scratchcards, General, Roulette, Slots

# Class for discord Economy
class Economy(commands.Cog, Scratchcards, General, Roulette, Slots):
  """Commands for economy in server"""

  def __init__(self, client):
    # Constants
    self.CLIENT = client
    self.COLOR = 0x35d843
    self.LOWER_DAILY = 10
    self.UPPER_DAILY = 50
    self.STORE_PAGINATION = 3
    self.INVENTORY_PAGINATION = 3
    self.db = shelve.open("data/economy", writeback=True)

  def __del__(self):
    self.db.close()

  ############################### DAILY #########################
  @commands.command(
    name="daily",
    help="Free daily foca-coins"
  )
  async def daily(self, ctx):
    user_id = str(ctx.author.id)
    if user_id not in self.db.keys():
      self.create_id(user_id)

    today_datetime, yesterday_datetime, time_til_tomorrow = self.get_dates()
    last_date_claimed = self.db[user_id]["daily"]["last_claimed"]

    if self.can_claim(today_datetime, last_date_claimed):
      # add streak if have
      if self.have_streak(yesterday_datetime, last_date_claimed):
        self.db[user_id]["daily"]["streak"] += 1
      else:
        self.db[user_id]["daily"]["streak"] = 1
      # add coins
      amount = randint(self.LOWER_DAILY, self.UPPER_DAILY)
      self.db[user_id]["balance"] += amount
      self.db[user_id]["daily"]["last_claimed"] = str(today_datetime)
      self.db[user_id]["daily"]["total_claimed"] += 1
      # embed message
      embed = Embed(title="💸 Daily Claim",
              description=f"**{ctx.author.display_name}** claim their daily: `{amount}`",
              color=self.COLOR)
    else:
      # embed message
      embed = Embed(title="💸 Daily Claim",
              description=f"**{ctx.author.display_name}** already claimed their daily",
              color=self.COLOR)
    # add last fields and send
    streak = self.db[user_id]["daily"]["streak"]
    embed.add_field(name="Next claim in", value=f"`{time_til_tomorrow}`", inline=True)
    embed.add_field(name="Streak", value=f"`{streak}`", inline=True)
    await ctx.send(embed=embed)

  ###################### BALANCE ###############################
  @commands.command(
    name="balance",
    aliases=["bal"],
    help="Shows your foca-coins"
  )
  async def balance(self, ctx):
    user_id = str(ctx.author.id)
    if user_id not in self.db.keys():
      self.create_id(user_id)
    embed = Embed(title=f"⚖️ {ctx.author.display_name}'s Balance",
                  description=f"foca-coins: `{self.db[user_id]['balance']}`",
                  color=self.COLOR)
    await ctx.send(embed=embed)

  ###################### SLOTS ###########################
  @commands.command(
    name="slots",
    help="Basic slot game to bet [amount]"
  )
  async def slots(self, ctx, amount=None):
    user_id = str(ctx.author.id)
    if user_id not in self.db.keys():
      self.create_id(user_id)

    # check amount to bet
    if amount is None:
      await self.send_basic_embed(ctx, "❌ Amount is required!")
    elif amount.isdigit() == False or int(amount) <= 0:
      await self.send_basic_embed(ctx, "❌ Amount is not valid!")
    elif self.db[user_id]["balance"] - int(amount) < 0:
      await self.send_basic_embed(ctx, "❌ You don't have enought money to make that bet!")
    else:
      # send message of slots
      await self.play_slots(ctx, amount, user_id)

  ################## ROULETTE #####################
  @commands.command(
    name="roulette",
    help="Roulette game to bet [amount]"
  )
  async def roulette(self, ctx, amount=None):
    user_id = str(ctx.author.id)
    if user_id not in self.db.keys():
      self.create_id(user_id)

    # check amount to bet
    if amount is None:
      await self.send_basic_embed(ctx, "❌ Amount is required!")
    elif amount.isdigit() == False or int(amount) <= 0:
      await self.send_basic_embed(ctx, "❌ Amount is not valid!")
    elif self.db[user_id]["balance"] - int(amount) < 0:
      await self.send_basic_embed(ctx, "❌ You don't have enought money to make that bet!")
    else:
      # send message of roulette
      await self.play_roulette(ctx, amount, user_id)

  ##################### STORE ##########################
  @commands.command(
    name="store",
    help="Sends Foca's Store"
  )
  async def store(self, ctx):
    embed = Embed(title="🏪 Foca's Store",
                  color=self.COLOR)
    with open("assets/store.json", 'r', encoding='utf-8') as file:
      STORE = json.load(file)
    list_store = [item for item in STORE.values()]
    # [ list[i:i + pagination] for i in range (0, len(list), pagination) ]
    # [
    #   list[0:  0  + x]
    #   list[x:  x  + x]
    #   list[2x: 2x + x]
    # ]
    pages = [list_store[i:i + self.STORE_PAGINATION] for i in range(0, len(list_store), self.STORE_PAGINATION)]
    page = 0

    self.pagination(pages, page, embed)
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
        reaction, user = await self.CLIENT.wait_for("reaction_add", timeout=60.0, check=check)

        if str(reaction.emoji) == "⬅️":
          page += (0 if page == 0 else -1)
        elif str(reaction.emoji) == "➡️":
          page += (0 if page == len(pages) - 1 else +1)
        elif str(reaction.emoji) == "❌":
          await message.clear_reactions()
          embed = Embed(description="🏪 Foca's Store Closed",
                        color=self.COLOR)
          await message.edit(embed=embed)
          break

        await message.remove_reaction(str(reaction.emoji), user)
        self.pagination(pages, page, embed)
        await message.edit(embed=embed)
      except:
        await message.clear_reactions()
        embed = Embed(description="🏪 Foca's Store Closed due Time Out",
                      color=self.COLOR)
        await message.edit(embed=embed)
        break

  ######################### BUY ##################
  @commands.command(
    name="buy",
    help="Buy item of store [product]"
  )
  async def buy(self, ctx, *product):
    user_id = str(ctx.author.id)
    if user_id not in self.db.keys():
      self.create_id(user_id)

    with open("assets/store.json", 'r', encoding='utf-8') as file:
      STORE = json.load(file)

    if len(product) == 0:
      await self.send_basic_embed(ctx, "❌ Product is Required!")
    elif "_".join(product).lower() not in STORE.keys():
      await self.send_basic_embed(ctx, "❌ Product Not Found in Store!")
    else:
      product_name = "_".join(product).lower()
      product = STORE[product_name]

      user_inventory = self.db[user_id]["inventory"]
      if self.db[user_id]["balance"] - product["price"] < 0:
        await self.send_basic_embed(ctx, "❌ Not enought money to buy product!")
      else:
        if product_name in user_inventory.keys():
          await self.send_basic_embed(ctx, "❌ You already have this product!")
        else:
          self.db[user_id]["inventory"][product_name] = product
          today_date = datetime.now() - timedelta(hours=5)
          self.db[user_id]["inventory"][product_name]["obtained"] = f"{today_date.year}-{today_date.month}-{today_date.day}"
          self.db[user_id]["balance"] -= product["price"]

          embed = Embed(
            description=f"Bought: **{product['name']}**",
            color=self.COLOR
          )
          await ctx.send(embed=embed)

  ################## INVENTORY ##################################
  @commands.command(
    name="inventory",
    help="Sends user inventory"
  )
  async def inventory(self, ctx):
    user_id = str(ctx.author.id)
    if user_id not in self.db.keys():
      self.create_id(user_id)
    embed = Embed(title=f"🎒 {ctx.author.display_name}'s Inventory",
                  color=self.COLOR)

    list_items = [item for item in self.db[user_id]["inventory"].values()]

    if len(list_items) == 0:
      embed.add_field(name="Objects", value="`You don't have any objects yet`", inline=False)
      await ctx.send(embed=embed)
    else:
      pages = [list_items[i:i + self.INVENTORY_PAGINATION] for i in range(0, len(list_items), self.INVENTORY_PAGINATION)]
      page = 0
      self.pagination(pages, page, embed)
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
          reaction, user = await self.CLIENT.wait_for("reaction_add", timeout=60.0, check=check)

          if str(reaction.emoji) == "⬅️":
            page += (0 if page == 0 else -1)
          elif str(reaction.emoji) == "➡️":
            page += (0 if page == len(pages) - 1 else +1)
          elif str(reaction.emoji) == "❌":
            await message.clear_reactions()
            embed = Embed(description=f"🎒 {ctx.author.display_name}'s Inventory Closed",
                          color=self.COLOR)
            await message.edit(embed=embed)
            break

          await message.remove_reaction(str(reaction.emoji), user)
          self.pagination(pages, page, embed)
          await message.edit(embed=embed)
        except:
          await message.clear_reactions()
          embed = Embed(description=f"🎒 {ctx.author.display_name}'s Inventory Closed due Time Out",
                        color=self.COLOR)
          await message.edit(embed=embed)
          break

  @commands.command(
    name="scratchcards",
    aliases=["scratchers", "scratch", "sc", "scratchcard", "scratcher"],
    help="Many games of scratchcards"
  )
  async def scratchcards(self, ctx):
    user_id = str(ctx.author.id)
    if user_id not in self.db.keys():
      self.create_id(user_id)

    # many games to play!
    embed = Embed(title="❓ Scratchcards ❓",
                  color=self.COLOR)
    DIAMONDS_HTP = """**Bet amount:** `20`
    Hᴏᴡ ᴛᴏ ᴘʟᴀʏ:
    Yᴏᴜ ᴀʀᴇ ᴀʙʟᴇ ᴛᴏ sᴄʀᴀᴛᴄʜ 3 ᴛɪᴍᴇs
    Fɪɴᴅ 3 💎, ᴡɪɴ `500` - **0.18%**
    Fɪɴᴅ 2 💎, ᴡɪɴ `100` - **6.96%**
    Fɪɴᴅ 1 💎, ᴡɪɴ `20` - **41.79%**
    Fɪɴᴅ ᴀ 💵, ᴡɪɴ `1` ɪᴍᴍᴇᴅɪᴀᴛʟʏ - **70.74%**
    Fɪɴᴅ ᴀ 2️⃣ ᴄʜᴀɴᴄᴇ ᴛᴏ sᴄʀᴀᴛᴄʜ ᴀɢᴀɪɴ - **48.93%**
    """
    THREE_IN_A_ROW_HTP = """**Bet amount:** `5`
    Hᴏᴡ ᴛᴏ ᴘʟᴀʏ:
    Sᴄʀᴀᴛᴄʜ 3 ᴛɪᴍᴇs
    Fɪɴᴅ 3 ᴏꜰ ᴛʜᴇ sᴀᴍᴇ ᴏʙᴊᴇᴄᴛ ɪɴ ᴀ ʀᴏᴡ, ᴡɪɴ `5000` - **0.13%**
    """
    ANIMALS_HTP = """**Bet amount:** `10`
    Hᴏᴡ ᴛᴏ ᴘʟᴀʏ:
    Cʜᴏᴏsᴇ ʏᴏᴜʀ ᴀɴɪᴍᴀʟ, ᴀɴᴅ ᴛʜᴇɴ ʏᴏᴜ ᴡɪʟʟ ʙᴇ ᴀʙʟᴇ ᴛᴏ sᴄʀᴀᴛᴄʜ 3 ᴛɪᴍᴇs
    Fɪɴᴅ 3 ᴀɴɪᴍᴀʟs ᴏꜰ ᴛʜᴇ sᴀᴍᴇ ᴀs ʏᴏᴜʀs, ᴡɪɴ `1000` - **0.39%**
    Fɪɴᴅ 2 ᴀɴɪᴍᴀʟs ᴏꜰ ᴛʜᴇ sᴀᴍᴇ ᴀs ʏᴏᴜʀs, ᴡɪɴ `500` - **6.25%**
    Fɪɴᴅ 1 ᴀɴɪᴍᴀʟ ᴏꜰ ᴛʜᴇ sᴀᴍᴇ ᴀs ʏᴏᴜʀs, ᴡɪɴ `10` - **25%**
    """
    embed.add_field(name="1️⃣ **Diamonds** 💎", value=DIAMONDS_HTP, inline=False)
    embed.add_field(name="2️⃣ **3 in a row** ⚽", value=THREE_IN_A_ROW_HTP, inline=False)
    embed.add_field(name="3️⃣ **Animals** 🐶", value=ANIMALS_HTP, inline=False)
    embed.set_footer(text=f"Player: {ctx.author.name}")
    message = await ctx.send(embed=embed)

    await message.add_reaction("1️⃣")
    await message.add_reaction("2️⃣")
    await message.add_reaction("3️⃣")

    # wait to user input
    def check(reaction, user):
      return (user == ctx.author
              and str(reaction.emoji) in ["1️⃣", "2️⃣", "3️⃣"]
              and reaction.message.id == message.id)
    error = False
    try:
      reaction, user = await self.CLIENT.wait_for("reaction_add", timeout=15.0, check=check)
      await message.remove_reaction(reaction, user)
    except:
      error = True
      embed = Embed(description="❌ You took too long to choose!",
                    color=self.COLOR)
      await message.clear_reactions()
      await message.edit(embed=embed)

    if not error:
      if str(reaction.emoji) == "1️⃣":
        if self.db[user_id]["balance"] - 20 < 0:
          await self.send_basic_embed(ctx, "❌ You don't have enought money to make that bet!")
        else:
          self.db[user_id]["balance"] -= 20
          await self.sc_diamonds(ctx, embed, message)

      elif str(reaction.emoji) == "2️⃣":
        if self.db[user_id]["balance"] - 5 < 0:
          await self.send_basic_embed(ctx, "❌ You don't have enought money to make that bet!")
        else:
          self.db[user_id]["balance"] -= 5
          await self.sc_3row(ctx, embed, message)

      elif str(reaction.emoji) == "3️⃣":
        if self.db[user_id]["balance"] - 10 < 0:
          await self.send_basic_embed(ctx, "❌ You don't have enought money to make that bet!")
        else:
          self.db[user_id]["balance"] -= 10
          await self.sc_animals(ctx, embed, message)

