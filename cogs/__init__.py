from .Music import Music
from .General import General
from .Help import Help
from .Economy import Economy

cogs_list = [
  Music,
  General,
  Help,
  Economy
]

async def setup(client):
  for cog in cogs_list:
    await client.add_cog(cog(client))