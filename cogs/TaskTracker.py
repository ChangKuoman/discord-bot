from discord.ext import commands
from discord import Embed
import re
from .utils import db

class TaskTracker(commands.Cog):
  """Task Tracker commands"""

  def __init__(self, client):
    self.CLIENT = client
    self.COLOR = 0x3480EB

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

    valid_users = []
    for user in assigned_to.split("|"):
      if user.startswith("<@") and user.endswith(">"):
        valid_users.append(user)
    if len(valid_users) == 0:
      embed.description = "Please mention a user to assign the task to."

    date_pattern = re.compile("((?:19|20)\\d\\d)-(0?[1-9]|1[012])-([12][0-9]|3[01]|0?[1-9])") # REGEX FOR YYYY-MM-DD
    if not date_pattern.match(date):
      embed.description = "Please provide a valid deadline for the task in the format YYYY-MM-DD."

    if embed.description:
      await ctx.send(embed=embed)
      return

    guild_name = str(ctx.guild.name)
    guild_id = str(ctx.guild.id)

    with db:
      db.guild_entry(guild_id, guild_name)
      id = db.add_task(guild_id, date, title)
      for user in valid_users:
        db.assign_task(id, user)

    embed.description = f"Task added! Deadline: {date}, Title: {title}"
    await ctx.send(embed=embed)

  @commands.command(name="tracker", help="Shows all tasks", aliases=["t", "tasks", "task"])
  async def tracker(self, ctx, arg=None):
    # $tracker

    guild_id = str(ctx.guild.id)

    text = ""
    values = []
    with db:
      if not db.project_exists(guild_id):
        text = "No tasks found for this server."
      elif arg == "all":
        values = db.get_all_tasks(guild_id)
      elif arg is None:
        values = db.get_in_progress_tasks(guild_id)
      elif arg.startswith("<@") and arg.endswith(">"):
        values = db.get_tasks_by_user(guild_id, arg)
      else:
          text = "Invalid argument."

    if len(values) > 0:
      for id, task, deadline, assigned_to in values:
        text += f"**ID:** {id} | **Task:** {task} | **Deadline:** {deadline} | **Assigned to:** {assigned_to}\n"
    else:
      text = "No tasks found for this server."

    embed = Embed(title="Task Tracker - Foca Bot",
                  description=text,
                  color=self.COLOR)
    # TODO: this needs to verify character limit AND paginate
    await ctx.send(embed=embed)

  @commands.command(name="tend", help="Ends a task")
  async def tend(self, ctx, task_id=None):
    # $tend

    guild_id = str(ctx.guild.id)
    if not task_id or not task_id.isdigit():
      text = "Please provide a valid task ID."
    else:

      task_id = int(task_id)
      author = str(ctx.author)
      date = str(ctx.message.created_at).split(" ")[0]
      with db:
        # ONLY FINISH A TASK IF USER IS IN THE SAME GUILD ID
        if not db.id_exists(task_id):
          text = "Task not found."
        elif not db.guild_id_match_task(task_id, guild_id):
          text = "Task not found."
        else:
          db.finish_task(task_id, author, date)
          text = f"Task {task_id} marked as finished by {ctx.author}."

    embed = Embed(title="Task Tracker - Foca Bot",
                  description=text,
                  color=self.COLOR)
    await ctx.send(embed=embed)