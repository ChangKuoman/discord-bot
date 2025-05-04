from random import randint

class Scratchcards:
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
            self.db[str(ctx.author.id)]["balance"] += 1
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
        self.db[str(ctx.author.id)]["balance"] += won

        game = draw_game(matrix, marked_places)
        embed.clear_fields()
        embed.add_field(name="DIAMOND SCRATCHCARD", value=game, inline=False)
        embed.add_field(name="OPPORTUNITIES", value=f"{opportunities}", inline=False)
        embed.add_field(name="YOU WON", value=f"`{won}`", inline=False)
        await message.edit(embed=embed)
