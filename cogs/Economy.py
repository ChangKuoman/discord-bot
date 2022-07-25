from discord.ext import commands
from discord import Embed
from replit import db
from random import randint, choice, shuffle
from datetime import datetime, timedelta
import asyncio
import json

if "economy" not in db.keys():
  db["economy"] = {}

class Economy(commands.Cog):
  """Commands for economy in server"""
  def __init__(self, client):
    self.CLIENT = client
    self.COLOR = 0x35d843
    self.LOWER_DAILY = 10
    self.UPPER_DAILY = 50
    self.JOBS_PAGINATION = 4
    self.INVENTORY_PAGINATION = 3
    self.STORE_PAGINATION = 3
    with open("assets/job.json", "r") as file:
      self.JOBS = json.load(file)
    with open("assets/store.json", "r") as file:
      self.STORE = json.load(file)
    with open("assets/question.json", "r") as file:
      self.QUIZ = json.load(file)
      self.QUESTIONS = self.QUIZ["questions"]

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
  
  def get_dates(self):
    today_datetime = datetime.now() - timedelta(hours=5)
    tomorrow_date = today_datetime + timedelta(days=1)
    tomorrow_datetime = datetime(tomorrow_date.year, tomorrow_date.month, tomorrow_date.day)
    time = tomorrow_datetime - today_datetime
    yesterday_datetime = today_datetime - timedelta(days=1)
    return today_datetime, yesterday_datetime, time

  def check_day(self, today_datetime, last_date):
    if last_date == "":
      return True
    last_date = datetime.strptime(last_date, '%Y-%m-%d %H:%M:%S.%f')
    if (last_date.day != today_datetime.day 
        or last_date.month != today_datetime.month 
        or last_date.year != today_datetime.year):
      return True
    return False

  def check_streak(self, yesterday_datetime, last_date):
    if last_date == "":
      return True
    last_date = datetime.strptime(last_date, '%Y-%m-%d %H:%M:%S.%f')
    if (last_date.day == yesterday_datetime.day 
        or last_date.month == yesterday_datetime.month 
        or last_date.year == yesterday_datetime.year):
      return True
    return False

  def check_work(self, last_worked, today):
    if (last_worked == ""):
      return True
    last_worked = datetime.strptime(last_worked, '%Y-%m-%d %H:%M:%S.%f')
    if (last_worked.year == today.year
         and last_worked.month == today.month
         and last_worked.day == today.day):
      return False
    elif (today.weekday() in [5, 6]):
      return False
    return True

  async def send_basic_embed(self, ctx, msg):
    embed = Embed(description=msg, color=self.COLOR)
    await ctx.send(embed=embed)

  def check_guild_id(self, guild_id, user_id):
    if guild_id not in db["economy"].keys():
      db["economy"][guild_id] = {}
    if user_id not in db["economy"][guild_id].keys():
      db["economy"][guild_id][user_id] = {
        "balance": 0,
        "inventory": {},
        "work": {
          "job": "",
          "income": 0,
          "total_days_worked": 0,
          "total_raises": 0,
          "last_worked": "",
          "next_salary": 0
        },
        "daily": {
          "last_claimed": "",
          "total_claimed": 0,
          "streak": 0
        }
      }

  @commands.command(name="daily", help="Daily Foca coins")
  async def daily(self, ctx):
    guild_id = str(ctx.guild.id)
    user_id = str(ctx.author.id)
    self.check_guild_id(guild_id, user_id)
    today_datetime, yesterday_datetime, time = self.get_dates()
    last_date = db["economy"][guild_id][user_id]["daily"]["last_claimed"]
    
    if self.check_day(today_datetime, last_date):
      if self.check_streak(yesterday_datetime, last_date):
        db["economy"][guild_id][user_id]["daily"]["streak"] += 1
      else:
        db["economy"][guild_id][user_id]["daily"]["streak"] = 1
      
      daily = randint(self.LOWER_DAILY, self.UPPER_DAILY)
      db["economy"][guild_id][user_id]["daily"]["last_claimed"] = str(today_datetime)
      db["economy"][guild_id][user_id]["daily"]["total_claimed"] += 1
      db["economy"][guild_id][user_id]["balance"] += daily
      embed = Embed(title="💸 Daily Claim",
                    description=f"**{ctx.author.display_name}** claim their daily: `{daily}`",
                    color=self.COLOR)
    else:
      embed = Embed(title="💸 Daily Claim",
                    description=f"**{ctx.author.display_name}** already claimed their daily",
                    color=self.COLOR)

    streak = db["economy"][guild_id][user_id]["daily"]["streak"]
    embed.add_field(name="Next claim in", value=f"`{time}`", inline=True)
    embed.add_field(name="Streak", value=f"`{streak}`", inline=True)
    await ctx.send(embed=embed)

  @commands.command(name="balance", aliases=["bal"], help="Sends Foca coins of user")
  async def balance(self, ctx):
    guild_id = str(ctx.guild.id)
    user_id = str(ctx.author.id)
    self.check_guild_id(guild_id, user_id)
    embed = Embed(title=f"⚖️ {ctx.author.display_name}'s Balance",
                  description=f"Foca coins: `{db['economy'][guild_id][user_id]['balance']}`",
                  color=self.COLOR)
    await ctx.send(embed=embed)
  
  @commands.command(name="slots", help="Slots game to bet [quantity]")
  async def slots(self, ctx, quantity=None):
    guild_id = str(ctx.guild.id)
    user_id = str(ctx.author.id)
    self.check_guild_id(guild_id, user_id)
    
    if quantity is None:
      await self.send_basic_embed(ctx, "❌ Quantity is required!")
    elif quantity.isdigit() == False or int(quantity) <= 0:
      await self.send_basic_embed(ctx, "❌ Quantity is not valid!")
    elif db["economy"][guild_id][user_id]["balance"] - int(quantity) < 0:
      await self.send_basic_embed(ctx, "❌ You don't have enought money to make that bet!")
    else:
      quantity = int(quantity)
      description = (f"Bet amount: `{quantity}`"
                    f"\nThree sevens: `{quantity*30}`" 
                    f"\nThree equal fruits: `{quantity*10}`"
                    f"\nTwo sevens: `{quantity*4}`"
                    f"\nOne seven: `{quantity}`")
      embed = Embed(title="🍒 Slots Game 🍒",
                    description=description,
                    color=self.COLOR)
      embed.add_field(name="PLAY", value="▶️", inline=True)
      embed.add_field(name="QUIT", value="❌", inline=True)
      embed.set_footer(text=f"Player: {ctx.author.name}")
      message = await ctx.send(embed=embed)
      await message.add_reaction("▶️")
      await message.add_reaction("❌")
      
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
        if str(reaction.emoji) == "❌":
          embed = Embed(description="🍒 Slots Game Finished 🍒",
                        color=self.COLOR)
          await message.clear_reactions()
          await message.edit(embed=embed)
        elif str(reaction.emoji) == "▶️":
          options = ["🍒", "🍉", "🍇", "🍊", "🍓", "7️⃣"]
          game = ["⬜", "⬜", "⬜"]
          db["economy"][guild_id][user_id]["balance"] -= quantity
          await message.clear_reactions()
          embed.clear_fields()
          await message.edit(embed=embed)
          await asyncio.sleep(1)
          embed.add_field(name="Slots", value=f"{''.join(game)}", inline=False)
          await message.edit(embed=embed)
          for slot in range(3):
            for spin in range(3):
              await asyncio.sleep(1)
              game[slot] = choice(options)
              embed.clear_fields()
              embed.add_field(name="Slots", value=f"{''.join(game)}", inline=False)
              await message.edit(embed=embed)

          if game.count("7️⃣") == 3:
            db["economy"][guild_id][user_id]["balance"] += quantity*30
            embed.add_field(name="Winner!", value=f"`{quantity*30}`", inline=False)
          elif game.count("7️⃣") == 2:
            db["economy"][guild_id][user_id]["balance"] += quantity*4
            embed.add_field(name="Winner!", value=f"`{quantity*4}`", inline=False)
          elif game.count("7️⃣") == 1:
            db["economy"][guild_id][user_id]["balance"] += quantity
            embed.add_field(name="Winner!", value=f"`{quantity}`", inline=False)
          elif (game.count("🍒") == 3 
                or game.count("🍉") == 3 
                or game.count("🍇") == 3 
                or game.count("🍊") == 3 
                or game.count("🍓") == 3):
            db["economy"][guild_id][user_id]["balance"] += quantity*10
            embed.add_field(name="Winner!", value=f"`{quantity*10}`", inline=False)
          else:
            embed.add_field(name="Lost", value=f"`{quantity}`", inline=False)
          await message.edit(embed=embed)

  @commands.command(name="roulette", help="Roulette game to bet [quantity]")
  async def roulette(self, ctx, quantity=None):
    guild_id = str(ctx.guild.id)
    user_id = str(ctx.author.id)
    self.check_guild_id(guild_id, user_id)
    if quantity is None:
      await self.send_basic_embed(ctx, "❌ Quantity is required!")
    elif quantity.isdigit() == False or int(quantity) <= 0:
      await self.send_basic_embed(ctx, "❌ Quantity is not valid!")
    elif db["economy"][guild_id][user_id]["balance"] - int(quantity) < 0:
      await self.send_basic_embed(ctx, "❌ You don't have enought money to make that bet!")
    else:
      quantity = int(quantity)
      description = (f"Bet amount: `{quantity}`"
                    f"\nRed: `{quantity*2}`"
                    f"\nBlack: `{quantity*2}`")
      embed = Embed(title="🔴 Roulette Game ⚫",
                    description=description,
                    color=self.COLOR)
      embed.add_field(name="PLAY", value="▶️", inline=True)
      embed.add_field(name="QUIT", value="❌", inline=True)
      embed.set_footer(text=f"Player: {ctx.author.name}")
      message = await ctx.send(embed=embed)
      await message.add_reaction("▶️")
      await message.add_reaction("❌")
      
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
        if str(reaction.emoji) == "❌":
          embed = Embed(description="🔴 Roulette Game Finished ⚫",
                        color=self.COLOR)
          await message.clear_reactions()
          await message.edit(embed=embed)
        elif str(reaction.emoji) == "▶️":
          db["economy"][guild_id][user_id]["balance"] -= quantity
          options = ["🔴", "⚫"]*18
          options.append("⚪")
          place = randint(0, 36)
          times_to_spin = randint(20, 60)
          
          chosen_color = "🔴"
          embed.clear_fields()
          embed.add_field(name="RED", value="🔴", inline=True)
          embed.add_field(name="BLACK", value="⚫", inline=True)
          embed.add_field(name="DEFAULT", value="🔴", inline=True)
          await message.edit(embed=embed)
          await message.clear_reactions()
          await message.add_reaction("⚫")
          await message.add_reaction("🔴")
          
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
            db["economy"][guild_id][user_id]["balance"] += quantity*2
            embed.add_field(name="Winner!", value=f"`{quantity*2}`")
          else:
            embed.add_field(name="Lost", value=f"`{quantity}`")
          await message.edit(embed=embed)

  @commands.command(name="job", aliases=["jobs"], help="Sends Foca's Job Bank")
  async def job(self, ctx):
    embed = Embed(title="💼 Foca's Job Bank",
                  color=self.COLOR)
    list_jobs = [job for job in self.JOBS.values()]
    pages = [list_jobs[i:i + self.JOBS_PAGINATION] for i in range(0, len(list_jobs), self.JOBS_PAGINATION)]
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
          embed = Embed(description="💼 Foca's Job Bank Closed",
                        color=self.COLOR)
          await message.edit(embed=embed)
          break
        
        await message.remove_reaction(str(reaction.emoji), user)
        self.pagination(pages, page, embed)
        await message.edit(embed=embed)
      except:
        await message.clear_reactions()
        embed = Embed(description="💼 Foca's Job Bank Closed due Time Out",
                      color=self.COLOR)
        await message.edit(embed=embed)
        break

  @commands.command(name="store", help="Sends Foca's Store")
  async def store(self, ctx):
    embed = Embed(title="🏪 Foca's Store",
                  color=self.COLOR)
    list_store = [item for item in self.STORE.values()]
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

  @commands.command(name="inventory", help="Sends user inventory")
  async def inventory(self, ctx):
    guild_id = str(ctx.guild.id)
    user_id = str(ctx.author.id)
    self.check_guild_id(guild_id, user_id)
    embed = Embed(title=f"🎒 {ctx.author.display_name}'s Inventory",
                  color=self.COLOR)
    list_items = [{**value, **self.STORE[key]} for key,value in db["economy"][guild_id][user_id]["inventory"].items()]
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

  @commands.command(name="apply", help="Applying for a job [job]")
  async def apply(self, ctx, *job):
    guild_id = str(ctx.guild.id)
    user_id = str(ctx.author.id)
    self.check_guild_id(guild_id, user_id)
    job_name = "_".join(job).lower()
    if job_name in self.JOBS.keys():
      if db["economy"][guild_id][user_id]["work"]["job"] == "":    
        applying_job = self.JOBS[job_name]
        needed, total = [int(value) for value in applying_job["interview_questions"].split("/")]
        count, corrects = 0, 0
        embed = Embed(title=f"📋 Interview questions for {applying_job['name']}",
                     description=f"Needed: {applying_job['interview_questions']}",
                     color=self.COLOR)
        embed.set_footer(text=f"Questions: {count}/{total}. Correct: {corrects}/{total}")
        message = await ctx.send(embed=embed)
        questions = self.QUESTIONS.copy()
        shuffle(questions)
        await message.add_reaction("🇦")
        await message.add_reaction("🇧")
        await message.add_reaction("🇨")
        await message.add_reaction("🇩")
        
        for _ in range(total):
          embed.clear_fields()
          question = questions.pop(0)
          answers = [question["right_answer"]] + question["wrong_answers"]
          shuffle(answers)
          optionA, optionB, optionC, optionD = answers
          value = (f"🇦 {optionA}"
                   f"\n🇧 {optionB}"
                   f"\n🇨 {optionC}"
                   f"\n🇩 {optionD}")
          embed.add_field(name=f"{question['question']}", value=value)
          await message.edit(embed=embed)
  
          def check(reaction, user):
            return (user == ctx.author 
                    and str(reaction.emoji) in ["🇦", "🇧", "🇨", "🇩"] 
                    and reaction.message.id == message.id)
          try:
            reaction, user = await self.CLIENT.wait_for("reaction_add", timeout=30.0, check=check)
  
            if str(reaction.emoji) == "🇦" and optionA == question["right_answer"]:
              corrects+=1
            elif str(reaction.emoji) == "🇧" and optionB == question["right_answer"]:
              corrects+=1          
            elif str(reaction.emoji) == "🇨" and optionC == question["right_answer"]:
              corrects+=1
            elif str(reaction.emoji) == "🇩" and optionD == question["right_answer"]:
              corrects+=1
              
            count+=1
            await message.remove_reaction(str(reaction.emoji), user)
            embed.set_footer(text=f"Questions: {count}/{total}. Correct: {corrects}/{total}")
  
            if corrects == needed:
              await message.clear_reactions()
              embed.clear_fields()
              embed.description = "✅ You succeed the interview!"
              db["economy"][guild_id][user_id]["work"]["job"] = job_name
              db["economy"][guild_id][user_id]["work"]["income"] = applying_job["starting_salary"]
              await message.edit(embed=embed)
              break
            elif corrects + (total - count) < needed:
              await message.clear_reactions()
              embed.clear_fields()
              embed.description = "❌ You failed the interview!"
              await message.edit(embed=embed)
              break
          except:
            await message.clear_reactions()
            embed.clear_fields()
            embed = Embed(description=f"❌ Interview ended due Time Out",
                          color=self.COLOR)
            await message.edit(embed=embed)
      else:
        await self.send_basic_embed(ctx, "❌ You already have a job!")
    else:
      await self.send_basic_embed(ctx, "❌ Job Not Found in Foca's Job Bank")

  @commands.command(name="resign", help="Resign of actual job")
  async def resign(self, ctx):
    guild_id = str(ctx.guild.id)
    user_id = str(ctx.author.id)
    self.check_guild_id(guild_id, user_id)

    if db["economy"][guild_id][user_id]["work"]["job"] != "":
      embed = Embed(description="❓ Are you sure you want to resign?",
                   color=self.COLOR)
      message = await ctx.send(embed=embed)
      await message.add_reaction("✅")
      await message.add_reaction("❌")
  
      def check(reaction, user):
        return (user == ctx.author 
                and str(reaction.emoji) in ["✅", "❌"] 
                and reaction.message.id == message.id)
      try:
        reaction, user = await self.CLIENT.wait_for("reaction_add", timeout=30.0, check=check)
        if str(reaction.emoji) == "✅":
          db["economy"][guild_id][user_id]["work"]["job"] = ""
          db["economy"][guild_id][user_id]["work"]["income"] = 0
          db["economy"][guild_id][user_id]["work"]["total_raises"] = 0
          embed.description = "✅ Resignation accepted"
        elif str(reaction.emoji) == "❌":
          embed.description = "❌ Resignation not submitted"
      except:
        embed.description = "❌ Resignation denied due Time Out"
      finally:
        await message.clear_reactions()
        await message.edit(embed=embed)
    else:
      await self.send_basic_embed(ctx, "❌ You don't have a job to quit")

  @commands.command(name="work", help="Work to earn currency")
  async def work(self, ctx):
    guild_id = str(ctx.guild.id)
    user_id = str(ctx.author.id)
    self.check_guild_id(guild_id, user_id)

    embed = Embed(title=f"💼 {ctx.author.display_name}'s Job",
                  description="You need 20 days of work to get paid",
                  color=self.COLOR)

    job_name = db["economy"][guild_id][user_id]["work"]["job"]
    job = self.JOBS[job_name]["name"] if job_name != "" else "None"
    
    income = db["economy"][guild_id][user_id]["work"]["income"]
    total_raises = db["economy"][guild_id][user_id]["work"]["total_raises"]
    
    embed.add_field(name="Job", value=f"`{job}`", inline=True)
    embed.add_field(name="Income", value=f"`{income}`", inline=True)
    embed.add_field(name="Total Raises", value=f"`{total_raises}`", inline=True)

    today_datetime, yesterday_datetime, time = self.get_dates()
    last_worked = db["economy"][guild_id][user_id]["work"]["last_worked"]
    if (job != "None" and self.check_work(last_worked, today_datetime)):
      worked = True
      db["economy"][guild_id][user_id]["work"]["total_days_worked"] += 1
      db["economy"][guild_id][user_id]["work"]["next_salary"] += 1
      db["economy"][guild_id][user_id]["work"]["last_worked"] = str(today_datetime)
      next_salary = db["economy"][guild_id][user_id]["work"]["next_salary"]
      if (next_salary == 20):
        db["economy"][guild_id][user_id]["work"]["next_salary"] = 0
        salary = db["economy"][guild_id][user_id]["work"]["income"]
        db["economy"][guild_id][user_id]["balance"] += salary
    else:
      worked = False
    last_worked = db["economy"][guild_id][user_id]["work"]["last_worked"]
    last_worked = last_worked if last_worked != "" else "None"
    next_salary = db["economy"][guild_id][user_id]["work"]["next_salary"]
    total_days_worked = db["economy"][guild_id][user_id]["work"]["total_days_worked"]
    embed.add_field(name="Total Days Worked", value=f"`{total_days_worked}`", inline=True)
    embed.add_field(name="Days Worked till Next Salary", value=f"`{next_salary}`", inline=True)
    embed.add_field(name="Last Worked", value=f"`{last_worked}`", inline=True)
    embed.add_field(name="Worked Now", value=f"`{worked}`", inline=True)
    await ctx.send(embed=embed)

  @commands.command(name="buy", help="Buy item of store [quantity][product]")
  async def buy(self, ctx, quantity=None, *product):
    guild_id = str(ctx.guild.id)
    user_id = str(ctx.author.id)
    self.check_guild_id(guild_id, user_id)

    if quantity is None:
      await self.send_basic_embed(ctx, "❌ Quantity is required!")
    elif quantity.isdigit() == False or int(quantity) <= 0:
      await self.send_basic_embed(ctx, "❌ Quantity is not valid!")
    elif len(product) == 0:
      await self.send_basic_embed(ctx, "❌ Product is Required!")
    elif "_".join(product).lower() not in self.STORE.keys():
      await self.send_basic_embed(ctx, "❌ Product Not Found in Store!")
    else:
      product_name = "_".join(product).lower()
      quantity = int(quantity)
      product = self.STORE[product_name]

      user_inventory = db["economy"][guild_id][user_id]["inventory"]
      if quantity > product["max_quantity"]:
        await self.send_basic_embed(ctx, "❌ Max quantity of Product Reached!")
      elif product_name in user_inventory.keys() and user_inventory[product_name]["quantity"] + quantity > product["max_quantity"]:
        await self.send_basic_embed(ctx, "❌ Max quantity of Product Reached!")
      elif db["economy"][guild_id][user_id]["balance"] < quantity * product["price"]:
        await self.send_basic_embed(ctx, "❌ Not enought money to buy product!")
      else:
        if product_name in user_inventory.keys():
          user_inventory[product_name]["quantity"] += quantity
        else:
          user_inventory[product_name] = {"quantity": quantity}
        
        db["economy"][guild_id][user_id]["inventory"] = user_inventory
        db["economy"][guild_id][user_id]["balance"] -= quantity*product["price"]

        job_name = db["economy"][guild_id][user_id]["work"]["job"]
        if (job_name != "" and product_name in self.JOBS[job_name]["items"]):
          if (db["economy"][guild_id][user_id]["work"]["income"] + product["job_increase"] >= self.JOBS[job_name]["max_salary"]):
            db["economy"][guild_id][user_id]["work"]["income"] = self.JOBS[job_name]["max_salary"]
          else:
            db["economy"][guild_id][user_id]["work"]["income"] += product["job_increase"]
          db["economy"][guild_id][user_id]["work"]["total_raises"] += 1
        
        embed = Embed(
          description=f"Bought: **{product['name']}**\nQuantity: **{quantity}** ",
          color=self.COLOR
        )
        await ctx.send(embed=embed)
