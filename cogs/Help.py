from discord.ext import commands
from discord import Embed

class Help(commands.Cog):
  """Help commands"""

  def __init__(self, client):
    self.CLIENT = client
    self.COLOR = 0xD77BFF
    self.PREFIX = "$"

  @commands.command(name="help", help="Sends help for use of commands [None | cog | command][None | succommand]")
  async def help(self, ctx, msg_command=None, msg_subcommand=None):
    # $help
    if msg_command is None:
        embed = Embed(title="❓ Help",
                      description=f"Use {self.PREFIX}help <cog> to obtain more information",
                      color=self.COLOR)

        cogs_docs = "\n".join([f"`{cog}` {self.CLIENT.cogs[cog].__doc__}" for cog in self.CLIENT.cogs])

        embed.add_field(name='Cogs',
                        value=cogs_docs,
                        inline=False)
    # $help cog None
    elif msg_command in self.CLIENT.cogs and msg_subcommand is None:
        cog = self.CLIENT.get_cog(msg_command)
        description=f"Use {self.PREFIX}help <command> to obtain more information\n{self.CLIENT.cogs[msg_command].__doc__}"
        embed = Embed(title=f'❓ Cog - {cog.__cog_name__}',
                      description=description,
                      color=self.COLOR)

        for command in self.CLIENT.get_cog(msg_command).get_commands():
          all_aliases = "|".join([command.name, *command.aliases])
          embed.add_field(name=f"`{self.PREFIX}{all_aliases}`",
                          value=command.help,
                          inline=False)
    # $help group
    elif (msg_command in self.CLIENT.all_commands
          and isinstance(self.CLIENT.get_command(msg_command), commands.Group)
          and msg_subcommand is None):
      command = self.CLIENT.get_command(msg_command)

      embed = Embed(title=f"❓ Group - {command.name}",
                    description=f"Use {self.PREFIX}help <command> <subcommand> to obtain more information",
                    color=self.COLOR)
      for subcommand in command.walk_commands():
        all_aliases = "|".join([subcommand.name, *subcommand.aliases])
        embed.add_field(name=f"`{self.PREFIX}{command.name} {all_aliases}`",
                        value=subcommand.help,
                        inline=False)
    # $help group command
    elif (msg_command in self.CLIENT.all_commands
          and isinstance(self.CLIENT.get_command(msg_command), commands.Group)
          and msg_subcommand in self.CLIENT.get_command(msg_command).all_commands):
      command = self.CLIENT.get_command(msg_command)
      subcommand = self.CLIENT.get_command(msg_command).get_command(msg_subcommand)

      embed = Embed(title=f"❓ Group Command - {command.name} {subcommand.name}",
                    color=self.COLOR)

      embed.add_field(name="Help", value=f"`{subcommand.help}`", inline=False)
      aliases = "|".join(subcommand.aliases) if subcommand.aliases else None
      embed.add_field(name="Name", value=f"`{subcommand.name}`", inline=True)
      embed.add_field(name="Aliases", value=f"`{aliases}`", inline=True)
      embed.add_field(name="Parent", value=f"`{subcommand.parent}`", inline=True)
      embed.add_field(name="Cog", value=f"`{subcommand.cog.__cog_name__}`", inline=True)
    # $help command
    elif (msg_command in self.CLIENT.all_commands):
      command = self.CLIENT.get_command(msg_command)

      embed = Embed(title=f"❓ Command - {command.name}",
                    description=f"{command.help}",
                    color=self.COLOR)

      embed.add_field(name="Help", value=f"`{command.help}`", inline=False)
      aliases = "|".join(command.aliases) if command.aliases else None
      embed.add_field(name="Name", value=f"`{command.name}`", inline=True)
      embed.add_field(name="Aliases", value=f"`{aliases}`", inline=True)
      embed.add_field(name="Cog", value=f"`{command.cog.__cog_name__}`", inline=True)
    # $help error error
    else:
      embed = Embed(title="❓ Help",
                    description=f"❌ Command or cog not found",
                    color=self.COLOR)
    await ctx.send(embed=embed)