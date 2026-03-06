from discord import Embed
import asyncio
from random import randint
from ..database import db

class Roulette:
    async def play_roulette(self, ctx, amount, user_id):
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
          with db:
            db.update_balance(user_id, -amount)
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
            with db:
              db.update_balance(user_id, amount*2)
            embed.add_field(name="Winner!", value=f"`{amount*2}`")
          else:
            embed.add_field(name="Lost", value=f"`{amount}`")
          await message.edit(embed=embed)