from random import randint, choice
from ..database import db

class Scratchcards:

  def pretty_game(self, game):
    return f"""🟦🟦🟦🟦🟦🟦🟦
🟦⬇🟦⬇🟦⬇🟦
🟦{game[0]}🟦{game[1]}🟦{game[2]}🟦
🟦⬆🟦⬆🟦⬆🟦
🟦🟦🟦🟦🟦🟦🟦
    """

  async def sc_animals(self, ctx, embed, message):
    embed.clear_fields()
    await message.clear_reactions()

    animals = ["🐶", "🐱", "🐰", "🐹"]
    h_game = [choice(animals) for _ in range(3)]
    game = ["💰", "💰", "💰"]

    embed.add_field(name="ANIMALS SCRATCHCARD", value=self.pretty_game(game), inline=False)
    await message.edit(embed=embed)

    for i in animals:
      await message.add_reaction(i)

    def check_animals(reaction, user):
          return (user == ctx.author
                  and str(reaction.emoji) in animals #!
                  and reaction.message.id == message.id)
    while True:
      try:
        reaction, user = await self.CLIENT.wait_for("reaction_add", timeout=15.0, check=check_animals)
        await message.remove_reaction(reaction, user)
        break
      except:
        continue

    chosen_animal = str(reaction.emoji)
    embed.add_field(name="Chosen animal", value=chosen_animal, inline=False)
    await message.edit(embed=embed)

    for i in range(3):
      await message.clear_reactions()
      await message.add_reaction("✂️")

      # wait to user input
      def check_animal_sc(reaction, user):
          return (user == ctx.author
                  and str(reaction.emoji) in ["✂️"]
                  and reaction.message.id == message.id)
      while True:
        try:
          reaction, user = await self.CLIENT.wait_for("reaction_add", timeout=15.0, check=check_animal_sc)
          await message.remove_reaction(reaction, user)
          break
        except:
          continue

      embed.clear_fields()
      game[i] = h_game[i]

      embed.add_field(name="ANIMALS SCRATCHCARD", value=self.pretty_game(game), inline=False)
      embed.add_field(name="Chosen animal", value=chosen_animal, inline=False)
      await message.edit(embed=embed)

    await message.clear_reactions()

    if h_game.count(chosen_animal) == 3:
      win = 1000
    elif h_game.count(chosen_animal) == 2:
      win = 500
    elif h_game.count(chosen_animal) == 1:
      win = 10
    if h_game.count(chosen_animal) != 0:
      with db:
        db.update_balance(str(ctx.author.id), win)
      embed.add_field(name="YOU WON", value=f"`{win}`", inline=False)
      await message.edit(embed=embed)

  async def sc_3row(self, ctx, embed, message):
    embed.clear_fields()
    game = ["💰", "💰", "💰"]
    options = ["⚽", "🏀", "🎾", "🏈", "⚾", "🏐", "🏉", "🎱", "🎳"]
    h_game = [choice(options) for _ in range(3)]

    for i in range(3):
      await message.clear_reactions()
      embed.add_field(name="3 IN A ROW SCRATCHCARD", value=self.pretty_game(game), inline=False)
      await message.edit(embed=embed)

      await message.add_reaction("✂️")

      # wait to user input
      def check_3row_sc(reaction, user):
          return (user == ctx.author
                  and str(reaction.emoji) in ["✂️"]
                  and reaction.message.id == message.id)
      while True:
        try:
          reaction, user = await self.CLIENT.wait_for("reaction_add", timeout=15.0, check=check_3row_sc)
          await message.remove_reaction(reaction, user)
          break
        except:
          continue

      embed.clear_fields()
      game[i] = h_game[i]

    await message.clear_reactions()
    embed.add_field(name="3 IN A ROW SCRATCHCARD", value=self.pretty_game(game), inline=False)
    await message.edit(embed=embed)

    if game[0] == game[1] and game[1] == game[2]:
      with db:
         db.update_balance(str(ctx.author.id), 5000)
      embed.add_field(name="YOU WON", value="`5000`", inline=False)
      await message.edit(embed=embed)

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
            with db:
              db.update_balance(str(ctx.author.id), 1)
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
        with db:
          db.update_balance(str(ctx.author.id), won)

        game = draw_game(matrix, marked_places)
        embed.clear_fields()
        embed.add_field(name="DIAMOND SCRATCHCARD", value=game, inline=False)
        embed.add_field(name="OPPORTUNITIES", value=f"{opportunities}", inline=False)
        embed.add_field(name="YOU WON", value=f"`{won}`", inline=False)
        await message.edit(embed=embed)
