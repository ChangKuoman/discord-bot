from discord.ext import commands
from discord import Embed
from replit import db
from random import randint, choice, shuffle
from datetime import datetime, timedelta
import asyncio
import json

# Creates economy in database
if "economy" not in db.keys():
  db["economy"] = {}

# Class for discord Economy
class Economy(commands.Cog):
  """Commands for economy in server"""

  def __init__(self, client):
    # Constants
    self.CLIENT = client
    self.COLOR = 0x35d843
    self.LOWER_DAILY = 10
    self.UPPER_DAILY = 50
    self.STORE_PAGINATION = 3
    self.INVENTORY_PAGINATION = 3

  #~~~~~~~~~~~~~~~~~~~~ USEFUL FUNCTIONS ~~~~~~~~~~~~~~~~~~~~
  async def send_basic_embed(self, ctx, msg):
    embed = Embed(description=msg, color=self.COLOR)
    await ctx.send(embed=embed)
    
  def create_id(self, id):
    db["economy"][id] = {
      "balance": 0,
      "inventory": {},
      "daily": {
        "last_claimed": "",
        "total_claimed": 0,
        "streak": 0
      }
    }

  def get_dates(self):
    # DATE = YYYY-MM-DD
    # DATETIME = YYYY-MM-DD HH-MM-SS
    today_datetime = datetime.now() - timedelta(hours=5)
    tomorrow_datetime = today_datetime + timedelta(days=1)
    tomorrow_date = datetime(tomorrow_datetime.year, tomorrow_datetime.month, tomorrow_datetime.day)
    time_til_tomorrow = tomorrow_date - today_datetime
    yesterday_datetime = today_datetime - timedelta(days=1)
    return (today_datetime, yesterday_datetime, time_til_tomorrow)

  def can_claim(self, today_datetime, last_date_claimed):
    # have not claimed today
    if last_date_claimed == "":
      return True
    last_date_claimed = datetime.strptime(last_date_claimed, '%Y-%m-%d %H:%M:%S.%f')
    if (last_date_claimed.day != today_datetime.day 
        or last_date_claimed.month != today_datetime.month 
        or last_date_claimed.year != today_datetime.year):
      return True
    return False

  def have_streak(self, yesterday_datetime, last_date_claimed):
    # last claimed == yesterday
    if last_date_claimed == "":
      return True
    last_date_claimed = datetime.strptime(last_date_claimed, '%Y-%m-%d %H:%M:%S.%f')
    if (last_date_claimed.day == yesterday_datetime.day 
        and last_date_claimed.month == yesterday_datetime.month 
        and last_date_claimed.year == yesterday_datetime.year):
      return True
    return False

  # -- pagination
  def pagination(self, pages, page, embed):
    embed.clear_fields()
    for object in pages[page]:
      description = ""
      for key, value in object.items():
        if key == "name":
          continue
        description += f"{' '.join(key.split('_')).title()}: `{value}`\n"
      
      embed.add_field(
        name=f"{object['name']}",
        value=f"{description}",
        inline=False
      )
    embed.set_footer(text=f"Page {page + 1}/{len(pages)}")
    

  ############################### DAILY #########################
  @commands.command(
    name="daily",
    help="Free daily foca-coins"
  )
  async def daily(self, ctx):
    user_id = str(ctx.author.id)
    if user_id not in db["economy"].keys():
      self.create_id(user_id)
    
    today_datetime, yesterday_datetime, time_til_tomorrow = self.get_dates()
    last_date_claimed = db["economy"][user_id]["daily"]["last_claimed"]

    if self.can_claim(today_datetime, last_date_claimed):
      # add streak if have
      if self.have_streak(yesterday_datetime, last_date_claimed):
        db["economy"][user_id]["daily"]["streak"] += 1
      else:
        db["economy"][user_id]["daily"]["streak"] = 1
      # add coins
      amount = randint(self.LOWER_DAILY, self.UPPER_DAILY)
      db["economy"][user_id]["balance"] += amount
      db["economy"][user_id]["daily"]["last_claimed"] = str(today_datetime)
      db["economy"][user_id]["daily"]["total_claimed"] += 1
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
    streak = db["economy"][user_id]["daily"]["streak"]
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
    if user_id not in db["economy"].keys():
      self.create_id(user_id)
    embed = Embed(title=f"⚖️ {ctx.author.display_name}'s Balance",
                  description=f"foca-coins: `{db['economy'][user_id]['balance']}`",
                  color=self.COLOR)
    await ctx.send(embed=embed)

  ###################### SLOTS ###########################
  @commands.command(
    name="slots",
    help="Basic slot game to bet [amount]"
  )
  async def slots(self, ctx, amount=None):
    user_id = str(ctx.author.id)
    if user_id not in db["economy"].keys():
      self.create_id(user_id)

    # check amount to bet
    if amount is None:
      await self.send_basic_embed(ctx, "❌ Amount is required!")
    elif amount.isdigit() == False or int(amount) <= 0:
      await self.send_basic_embed(ctx, "❌ Amount is not valid!")
    elif db["economy"][user_id]["balance"] - int(amount) < 0:
      await self.send_basic_embed(ctx, "❌ You don't have enought money to make that bet!")
    else:
      # send message of slots
      amount = int(amount)
      description = (f"Bet amount: `{amount}`"
                    f"\nThree sevens: `{amount*30}`" 
                    f"\nThree equal fruits: `{amount*10}`"
                    f"\nTwo sevens: `{amount*4}`"
                    f"\nOne seven: `{amount}`")
      embed = Embed(title="🍒 Slots Game 🍒",
                    description=description,
                    color=self.COLOR)
      embed.add_field(name="PLAY", value="▶️", inline=True)
      embed.add_field(name="QUIT", value="❌", inline=True)
      embed.set_footer(text=f"Player: {ctx.author.name}")
      message = await ctx.send(embed=embed)
      await message.add_reaction("▶️")
      await message.add_reaction("❌")

      # wait to user input
      def check(reaction, user):
        return (user == ctx.author 
                and str(reaction.emoji) in ["▶️", "❌"] 
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
        # never started game
        if str(reaction.emoji) == "❌":
          embed = Embed(description="🍒 Slots Game Finished 🍒",
                        color=self.COLOR)
          await message.clear_reactions()
          await message.edit(embed=embed)
        # start game
        elif str(reaction.emoji) == "▶️":
          options = ["🍒", "🍉", "🍇", "🍊", "🍓", "7️⃣"]
          game = ["⬜", "⬜", "⬜"]
          db["economy"][user_id]["balance"] -= amount
          await message.clear_reactions()
          embed.clear_fields()
          await message.edit(embed=embed)
          await asyncio.sleep(1)
          embed.add_field(name="Slots", value=f"{''.join(game)}", inline=False)
          await message.edit(embed=embed)
          for slot in range(3):
            for spin in range(3):
              # black box to see changing
              if spin != 0:
                await asyncio.sleep(1)
                game[slot] = "⬛"
                embed.clear_fields()
                embed.add_field(name="Slots", value=f"{''.join(game)}", inline=False)
                await message.edit(embed=embed)

              # options
              await asyncio.sleep(1)
              game[slot] = choice(options)
              embed.clear_fields()
              embed.add_field(name="Slots", value=f"{''.join(game)}", inline=False)
              await message.edit(embed=embed)

          # count if winning
          text_to_send = "Winner!"
          if game.count("7️⃣") == 3:
            amount = amount*30
          elif game.count("7️⃣") == 2:
            amount = amount*4
          elif game.count("7️⃣") == 1:
            amount = amount
          elif (game.count("🍒") == 3 
                or game.count("🍉") == 3 
                or game.count("🍇") == 3 
                or game.count("🍊") == 3 
                or game.count("🍓") == 3):
            amount = amount*10
          else:
            text_to_send = "Lost"
            amount = -amount
            
          # send message
          if amount > 0:
            db["economy"][user_id]["balance"] += amount
          embed.add_field(name=text_to_send, value=f"`{amount}`", inline=False)
          await message.edit(embed=embed)

  ################## ROULETTE #####################
  @commands.command(
    name="roulette",
    help="Roulette game to bet [amount]"
  )
  async def roulette(self, ctx, amount=None):
    user_id = str(ctx.author.id)
    if user_id not in db["economy"].keys():
      self.create_id(user_id)

    # check amount to bet
    if amount is None:
      await self.send_basic_embed(ctx, "❌ Amount is required!")
    elif amount.isdigit() == False or int(amount) <= 0:
      await self.send_basic_embed(ctx, "❌ Amount is not valid!")
    elif db["economy"][user_id]["balance"] - int(amount) < 0:
      await self.send_basic_embed(ctx, "❌ You don't have enought money to make that bet!")
    else:
      # send message of roulette
      amount = int(amount)
      description = (f"Bet amount: `{amount}`"
                    f"\nRed: `{amount*2}`"
                    f"\nBlack: `{amount*2}`")
      embed = Embed(title="🔴 Roulette Game ⚫",
                    description=description,
                    color=self.COLOR)
      embed.add_field(name="PLAY", value="▶️", inline=True)
      embed.add_field(name="QUIT", value="❌", inline=True)
      embed.set_footer(text=f"Player: {ctx.author.name}")
      message = await ctx.send(embed=embed)
      await message.add_reaction("▶️")
      await message.add_reaction("❌")

      # wait to user input
      def check(reaction, user):
        return (user == ctx.author 
                and str(reaction.emoji) in ["▶️", "❌"] 
                and reaction.message.id == message.id)
      error = False
      try:
        reaction, user = await self.CLIENT.wait_for("reaction_add", timeout=15.0, check=check)
        await message.remove_reaction(reaction, user) 
      except:
        error = True
        embed = Embed(description="❌ You took too long to choose!",
                      color=self.COLOR   )
        await message.clear_reactions()
        await message.edit(embed=embed)
  
      if not error:
        # never started game
        if str(reaction.emoji) == "❌":
          embed = Embed(description="🔴 Roulette Game Finished ⚫",
                        color=self.COLOR)
          await message.clear_reactions()
          await message.edit(embed=embed)
        # start game
        elif str(reaction.emoji) == "▶️":
          db["economy"][user_id]["balance"] -= amount
          options = ["🔴", "⚫"]*18
          options.append("⚪")
          place = randint(0, 36)
          times_to_spin = randint(20, 60)

          # select color
          chosen_color = "🔴"
          embed.clear_fields()
          embed.add_field(name="RED", value="🔴", inline=True)
          embed.add_field(name="BLACK", value="⚫", inline=True)
          embed.add_field(name="DEFAULT", value="🔴", inline=True)
          await message.edit(embed=embed)
          await message.clear_reactions()
          await message.add_reaction("⚫")
          await message.add_reaction("🔴")

          # wait for user input of color
          def check2(reaction, user):
            return (user == ctx.author 
                    and str(reaction.emoji) in ["🔴", "⚫"] 
                    and reaction.message.id == message.id)
          try:
            reaction, user = await self.CLIENT.wait_for("reaction_add", timeout=15.0, check=check2)
            chosen_color = str(reaction.emoji)
          except:
            pass
          finally:
            await message.clear_reactions()
            await message.add_reaction(chosen_color)
          
          embed.clear_fields()
          await message.edit(embed=embed)
          for i in range(times_to_spin):
            await asyncio.sleep(0.5)
            embed.clear_fields()
            roulette = (f"{options[(place+i-2)%37]}"
                       f"{options[(place+i-1)%37]}"
                       f"➡️"
                       f"{options[(place+i)%37]}"
                       f"⬅️"
                       f"{options[(place+i+1)%37]}"
                       f"{options[(place+i+2)%37]}")
            embed.add_field(name="Roulette", value=roulette, inline=False)
            await message.edit(embed=embed)
            
          winner_color = options[(place+i)%37]
          if winner_color == chosen_color:
            db["economy"][user_id]["balance"] += amount*2
            embed.add_field(name="Winner!", value=f"`{amount*2}`")
          else:
            embed.add_field(name="Lost", value=f"`{amount}`")
          await message.edit(embed=embed)

  ##################### STORE ##########################
  @commands.command(
    name="store",
    help="Sends Foca's Store"
  )
  async def store(self, ctx):
    embed = Embed(title="🏪 Foca's Store",
                  color=self.COLOR)
    with open("assets/store.json", 'r') as file:
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
    if user_id not in db["economy"].keys():
      self.create_id(user_id)

    with open("assets/store.json", 'r') as file:
      STORE = json.load(file)
    
    if len(product) == 0:
      await self.send_basic_embed(ctx, "❌ Product is Required!")
    elif "_".join(product).lower() not in STORE.keys():
      await self.send_basic_embed(ctx, "❌ Product Not Found in Store!")
    else:
      product_name = "_".join(product).lower()
      product = STORE[product_name]

      user_inventory = db["economy"][user_id]["inventory"]
      if db["economy"][user_id]["balance"] - product["price"] < 0:
        await self.send_basic_embed(ctx, "❌ Not enought money to buy product!")
      else:
        if product_name in user_inventory.keys():
          await self.send_basic_embed(ctx, "❌ You already have this product!")
        else:
          db["economy"][user_id]["inventory"][product_name] = product
          today_date = datetime.now() - timedelta(hours=5)
          db["economy"][user_id]["inventory"][product_name]["obtained"] = f"{today_date.year}-{today_date.month}-{today_date.day}"
          db["economy"][user_id]["balance"] -= product["price"]
          
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
    if user_id not in db["economy"].keys():
      self.create_id(user_id)
    embed = Embed(title=f"🎒 {ctx.author.display_name}'s Inventory",
                  color=self.COLOR)
    
    list_items = [item for item in db["economy"][user_id]["inventory"].values()]
    
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

  async def sc_diamonds(self, ctx, embed, message):
    matrix = [[["⏺"] for _ in range(4)] for _ in range(4)]
    
    def add_emoji(emoji, quantity, matrix):
      count = 0
      while count < quantity:
        r_1, r_2 = randint(0, 3), randint(0, 3)
        while len(matrix[r_1][r_2]) > 2:
          r_1, r_2 = randint(0, 3), randint(0, 3)
        matrix[r_1][r_2].append(emoji)
        count += 1

    add_emoji("💵", 5, matrix)
    add_emoji("💎", 3, matrix)
    add_emoji("2️⃣", 3, matrix)

    embed.clear_fields()
    def draw_game(matrix, marked_places):
      numbers = ["1️⃣","2️⃣","3️⃣","4️⃣"]
      letters = ["🇦", "🇧", "🇨", "🇩"]
      empty = "🟦"
      hole = "🕳️"
      game = empty + "".join(numbers) + '\n'
      for i in range(4):
        game += letters[i]
        for j in range(4):
          if (i, j) in marked_places:
            if len(matrix[i][j]) == 1:
              game += hole
            else:
              game += matrix[i][j][1]
          else:
            game += matrix[i][j][0]
        # salto de linea
        if i != 3:
          game += '\n'
      return game

    marked_places = []
    q_diamonds = 0
    opportunities = 3
    
    game = draw_game(matrix, marked_places)
    await message.clear_reactions()
    embed.add_field(name="DIAMOND SCRATCHCARD", value=game, inline=False)
    embed.add_field(name="OPPORTUNITIES", value=f"{opportunities}", inline=False)
    await message.edit(embed=embed)

    while opportunities != 0:
      
      await message.add_reaction("1️⃣")
      await message.add_reaction("2️⃣")
      await message.add_reaction("3️⃣")
      await message.add_reaction("4️⃣")

      # wait to user input
      def check_numbers_diamonds(reaction, user):
        return (user == ctx.author 
                and str(reaction.emoji) in ["1️⃣", "2️⃣", "3️⃣", "4️⃣"] 
                and reaction.message.id == message.id)
      while True:
        try:
          reaction, user = await self.CLIENT.wait_for("reaction_add", timeout=15.0, check=check_numbers_diamonds)
          await message.remove_reaction(reaction, user) 
          break
        except:
          continue

      number = str(reaction.emoji)
      await message.clear_reactions()
      await message.add_reaction("🇦")
      await message.add_reaction("🇧")
      await message.add_reaction("🇨")
      await message.add_reaction("🇩")
      
      # wait to user input
      def check_letter_diamonds(reaction, user):
        return (user == ctx.author 
                and str(reaction.emoji) in ["🇦", "🇧", "🇨", "🇩"] 
                and reaction.message.id == message.id)
      while True:
        try:
          reaction, user = await self.CLIENT.wait_for("reaction_add", timeout=15.0, check=check_letter_diamonds)
          await message.remove_reaction(reaction, user)
          break
        except:
          continue

      letter = str(reaction.emoji)
      await message.clear_reactions()
      dict_for_emojis = {
        "1️⃣" : 0, "2️⃣" : 1, "3️⃣" : 2, "4️⃣" : 3,
        "🇦" : 0, "🇧" : 1, "🇨" : 2, "🇩" : 3
      }
      i, j = dict_for_emojis[letter], dict_for_emojis[number]
      if (i, j) in marked_places:
        continue
      marked_places.append((i, j))

      embed.clear_fields()
      
      if len(matrix[i][j]) > 1:
        if matrix[i][j][1] == "2️⃣":
          opportunities += 1
        elif matrix[i][j][1] == "💵":
          db["economy"][str(ctx.author.id)]["balance"] += 1
          embed.add_field(name="IMMEDIATLY WON", value="`1`", inline=False)
        else:
          q_diamonds += 1
      opportunities -= 1
      
      game = draw_game(matrix, marked_places)
      embed.add_field(name="DIAMOND SCRATCHCARD", value=game, inline=False)
      embed.add_field(name="OPPORTUNITIES", value=f"{opportunities}", inline=False)
      await message.edit(embed=embed)

    if q_diamonds > 0:
      won = 0
      if q_diamonds == 1:
        won = 10
      elif q_diamonds == 2:
        won = 100
      elif q_diamonds == 3:
        won = 500
      db["economy"][str(ctx.author.id)]["balance"] += won
      
      game = draw_game(matrix, marked_places)
      embed.clear_fields()
      embed.add_field(name="DIAMOND SCRATCHCARD", value=game, inline=False)
      embed.add_field(name="OPPORTUNITIES", value=f"{opportunities}", inline=False)
      embed.add_field(name="YOU WON", value=f"`{won}`", inline=False)
      await message.edit(embed=embed)
  
  @commands.command(
    name="scratchcards",
    help="Many games of scratchcards"
  )
  async def scratchcards(self, ctx):
    user_id = str(ctx.author.id)
    if user_id not in db["economy"].keys():
      self.create_id(user_id)

    # many games to play!
    embed = Embed(title="❓ Scratchcards ❓",
                  color=self.COLOR)
    DIAMONDS_HTP = """Bet amount: `10`
    How to play:
    You are able to scratch 3 times
    Find 3 diamonds to win the big prize: `500`
    Find 2 diamonds to win the medium prize: `100`
    Find 1 diamond to win the small prize: `10`
    If you find a second chance, you will be able to scratch again
    If you find a dollar, you will win it immediatly
    """
    THREE_IN_A_ROW_HTP = """
    
    """
    ANIMALS_HTP = """
    
    """
    embed.add_field(name="1️⃣ Diamonds", value=DIAMONDS_HTP, inline=False)
    embed.add_field(name="2️⃣ 3️ in a row", value=THREE_IN_A_ROW_HTP, inline=False)
    embed.add_field(name="3️⃣ Animals", value=ANIMALS_HTP, inline=False)
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
        if db["economy"][user_id]["balance"] - 10 < 0:
          await self.send_basic_embed(ctx, "❌ You don't have enought money to make that bet!")
        else:
          db["economy"][user_id]["balance"] -= 10
          await self.sc_diamonds(ctx, embed, message)
        
        
      elif str(reaction.emoji) == "2️⃣":
        pass
      elif str(reaction.emoji) == "3️⃣":
        pass

        
