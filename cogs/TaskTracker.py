from datetime import date

from discord.ext import commands
from discord import Embed
import re
from .utils import db

class TaskTracker(commands.Cog):
  """Task Tracker commands"""

  def __init__(self, client):
    self.CLIENT = client
    self.COLOR = 0x3480EB
    self.DATE_PATTERN = re.compile("((?:19|20)\\d\\d)-(0?[1-9]|1[012])-([12][0-9]|3[01]|0?[1-9])") # REGEX FOR YYYY-MM-DD

  def _valid_user(self, arg):
    return arg.startswith("<@") and arg.endswith(">")

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

    if not self.DATE_PATTERN.match(date):
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
      elif self._valid_user(arg):
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

  @commands.command(name="tchange", help="Changes a task.")
  async def tchange(self, ctx, action=None, id=None, arg=None, *more):
    # $tchange

    if not action or not id or not arg:
      text = "Please provide an action, id and argument."
    else:
      with db:
        # checks id exist and id corresponds to the guild id of the server
        if not db.id_exists(id):
          text = "Task not found."
        elif not db.guild_id_match_task(id, str(ctx.guild.id)):
          text = "Task not found."

        # ACTIONS TO CHANGE TASKS ATTRIBUTES
        elif action == "task":
          new_task_name = arg + " " + " ".join(more)
          if db.change_task_name(id, new_task_name):
            text = f"Task name changed to {new_task_name}."
          else:
            text = "Failed to change task name."
        elif action == "deadline":
          arg = arg.replace("/", "-")
          if not self.DATE_PATTERN.match(arg):
            text = "Please provide a valid deadline for the task in the format YYYY-MM-DD."
          elif db.change_task_deadline(id, arg):
            text = f"Task deadline changed to {arg}."
          else:
              text = "Failed to change task deadline."
        elif action == "add":
          # FIXME: is adding more than PK is supposed to allow
          if not self._valid_user(arg):
            text = "Please mention a user to assign the task to."
          elif db.assign_task(id, arg):
            text = f"User {arg} assigned to task {id}."
          else:
            text = "Failed to assign user to task."
        elif action == "remove":
          if not self._valid_user(arg):
            text = "Please mention a user to remove from the task."
          elif db.remove_assigned_user(id, arg):
            text = f"User {arg} removed from task {id}."
          else:
            text = "Failed to remove user from task."
        else:
          text = "Invalid action."

    embed = Embed(title="Task Tracker - Foca Bot",
                  description=text,
                  color=self.COLOR)
    await ctx.send(embed=embed)


  @commands.command(name="tname", help="Changes a the name of the project.")
  async def tname(self, ctx, new_name=None):
    # $tname

    # TODO: name for project is not displayed anywhere
    guild_id = str(ctx.guild.id)
    if not new_name:
      text = "Please provide a new name for the project."
    else:
      with db:
        if not db.project_exists(guild_id):
          text = "Project not found."
        elif db.change_project_name(guild_id, new_name):
          text = f"Project name changed to {new_name}."
        else:
          text = "Failed to change project name."

    embed = Embed(title="Task Tracker - Foca Bot",
                  description=text,
                  color=self.COLOR)
    await ctx.send(embed=embed)