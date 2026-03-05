from discord.ext import commands
from .database import db

# decorator
def whitelisted_only():
    async def predicate(ctx):

        if await ctx.bot.is_owner(ctx.author):
            return True

        if db.is_whitelisted(ctx.author.id):
            return True

        # TODO: make cute embed
        await ctx.send("❌ You are not authorized to use this command.")
        return False

    return commands.check(predicate)