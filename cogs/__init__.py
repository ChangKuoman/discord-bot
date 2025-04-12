from .Music import Music
from .General import General
from .Help import Help
from .Economy import Economy
from .LLMAI import LLMAI

cogs_list = [
  Music,
  General,
  Help,
  Economy,
  LLMAI
]

async def setup(client):
  for cog in cogs_list:
    await client.add_cog(cog(client))