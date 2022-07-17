from .Kisslist import Kisslist
from .Messages import Messages
from .Music import Music

cogs_list = [
  Kisslist,
  Messages,
  Music
]

def setup(client):
  for cog in cogs_list:
    client.add_cog(cog(client))
