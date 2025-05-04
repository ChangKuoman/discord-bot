from discord import Embed
import asyncio
from random import choice

class Slots:
    async def play_slots(self, ctx, amount, user_id):
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
          self.db[user_id]["balance"] -= amount
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
            self.db[user_id]["balance"] += amount
          embed.add_field(name=text_to_send, value=f"`{amount}`", inline=False)
          await message.edit(embed=embed)