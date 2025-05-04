from .Music import Music
from .General import General
from .Help import Help
from .Economy import Economy
from .LLMAI import LLMAI
from .StudyBuddy import StudyBuddy

cogs_list = [
  Music,
  General,
  Help,
  Economy,
  LLMAI,
  StudyBuddy
]

async def setup(client):
  for cog in cogs_list:
    await client.add_cog(cog(client))