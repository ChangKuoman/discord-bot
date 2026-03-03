from discord.ext import commands
from discord import Embed
import shelve
import re

class TaskTracker(commands.Cog):
  """Task Tracker commands"""

  def __init__(self, client):
    self.CLIENT = client
    self.COLOR = 0x3480EB
    self.db = shelve.open("data/tasks", writeback=True)

  def __del__(self):
    self.db.close()

  def create_guild_entry(self, guild_id, guild_name):
    if guild_id not in self.db.keys():
      self.db[guild_id] = {'title': guild_name, 'tasks': {}, 'id': 1}

  @commands.command(name="tadd", help="Adds a new task")
  async def tadd(self, ctx, assigned_to=None, date=None, title0=None, *title1):
    # $tadd

    embed = Embed(title="Task Tracker - Foca Bot",
                  description="",
                  color=self.COLOR)

    if not assigned_to or not date or not title0:
      embed.description = "Please provide all the required arguments: assigned_to, date, title"

    date = date.replace("/", "-")
    title = title0 + " " + " ".join(title1)

    if not assigned_to.startswith("<@") or not assigned_to.endswith(">"):
      embed.description = "Please mention a user to assign the task to."

    date_pattern = re.compile("((?:19|20)\\d\\d)-(0?[1-9]|1[012])-([12][0-9]|3[01]|0?[1-9])") # REGEX FOR YYYY-MM-DD
    if not date_pattern.match(date):
      embed.description = "Please provide a valid deadline for the task in the format YYYY-MM-DD."

    if embed.description:
      await ctx.send(embed=embed)
      return

    guild_name = str(ctx.guild.name)
    guild_id = str(ctx.guild.id)
    self.create_guild_entry(guild_id, guild_name)

    current_id = self.db[guild_id]['id']
    self.db[guild_id]['tasks'][current_id] = {
        'assigned_to': assigned_to,
        'deadline': date,
        'title': title,
        'status': 'in progress',
        'finished_by': None,
        'finished_on': None
    }
    self.db[guild_id]['id'] += 1

    embed.description = f"Task added! Assigned to: {assigned_to}, Deadline: {date}, Title: {title}"
    await ctx.send(embed=embed)

  @commands.command(name="tracker", help="Shows all tasks", aliases=["t", "tasks"])
  async def tracker(self, ctx, arg=None):
    # $tracker

    guild_name = str(ctx.guild.name)
    guild_id = str(ctx.guild.id)
    self.create_guild_entry(guild_id, guild_name)

    # this section will sort and filter
    return_dict = self.db[guild_id]['tasks']
    if arg == "all":
      # returns all completed and in progress tasks sorted by deadline
      return_dict = dict(sorted(self.db[guild_id]['tasks'].items(), key=lambda item: item[1]['deadline']))
    elif arg is None:
      # returns all in progress tasks sorted by deadline
      return_dict = dict(sorted(
        {task_id: task for task_id, task in self.db[guild_id]['tasks'].items() if task['status'] == 'in progress'}.items(),
        key=lambda item: item[1]['deadline']
      ))
    elif arg.startswith("<@") and arg.endswith(">"):
      # returns all tasks assigned to a specific user (NOT sorted)
      return_dict = {task_id: task for task_id, task in self.db[guild_id]['tasks'].items() if task['assigned_to'] == arg}
    else:
      # returns all in progress tasks sorted by deadline
      return_dict = dict(sorted(
        {task_id: task for task_id, task in self.db[guild_id]['tasks'].items() if task['status'] == 'in progress'}.items(),
        key=lambda item: item[1]['deadline']
      ))

    if not return_dict:
      embed = Embed(title="Task Tracker - Foca Bot",
                    description=f"No tasks found! Try another command")
      await ctx.send(embed=embed)
      return

    # TODO: this needs to verify character limit / maybe paginate
    await ctx.send(f"**{guild_name}**\n" + "\n".join([
        f"**{task_id}**. {task['title']} - Assigned to: {task['assigned_to']} - Deadline: {task['deadline']} - Status: {task['status']}"
        for task_id, task in return_dict.items()
    ]))

  @commands.command(name="tend", help="Ends a task")
  async def tend(self, ctx, task_id=None):
    # $tend

    guild_name = str(ctx.guild.name)
    guild_id = str(ctx.guild.id)
    self.create_guild_entry(guild_id, guild_name)

    if not task_id or not task_id.isdigit() or int(task_id) not in self.db[guild_id]['tasks'].keys():
      embed = Embed(title="Task Tracker - Foca Bot",
                    description=f"Please provide a valid task ID.")
      await ctx.send(embed=embed)
      return

    task_id = int(task_id)

    self.db[guild_id]['tasks'][task_id]['status'] = 'finished'
    self.db[guild_id]['tasks'][task_id]['finished_by'] = str(ctx.author)
    self.db[guild_id]['tasks'][task_id]['finished_on'] = str(ctx.message.created_at).split(" ")[0]

    embed = Embed(title="Task Tracker - Foca Bot",
                  description=f"Task {task_id} marked as finished by {ctx.author}.",
                  color=self.COLOR)
    await ctx.send(embed=embed)