from discord.ext import commands
from discord import Embed
import shelve

class TaskTracker(commands.Cog):
  """Task Tracker commands"""

  def __init__(self, client):
    self.CLIENT = client
    self.COLOR = 0x3480EB
    self.db = shelve.open("assets/tasktracker/tasks", writeback=True)

  def __del__(self):
    self.db.close()

  @commands.command(name="tadd", help="Adds a new task")
  async def tadd(self, ctx, assigned_to, date, title0, *title1):
    # $tadd

    #TODO: send messages as cute embeds
    if not assigned_to or not date or not title0:
      await ctx.send("Please provide all the required arguments: assigned_to, date, title")
      return

    date = date.replace("/", "-")
    title = title0 + " " + " ".join(title1)

    if not assigned_to.startswith("<@") or not assigned_to.endswith(">"):
      await ctx.send("Please mention a user to assign the task to.")
      return

    # TODO: validate date format more
    if len(date.split("-")) != 3 or not all(part.isdigit() for part in date.split("-")):
      await ctx.send("Please provide a valid deadline for the task in the format YYYY-MM-DD.")
      return

    guild_name = str(ctx.guild.name)
    guild_id = str(ctx.guild.id)
    if guild_id not in self.db.keys():
      self.db[guild_id] = {'title': guild_name, 'tasks': {}, 'id': 1}

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

    await ctx.send(f"Task added! Assigned to: {assigned_to}, Deadline: {date}, Title: {title}")

  @commands.command(name="tracker", help="Shows all tasks", aliases=["t", "tasks"])
  async def tracker(self, ctx, arg=None):
    # $tracker

    guild_name = str(ctx.guild.name)
    guild_id = str(ctx.guild.id)
    if guild_id not in self.db.keys():
        self.db[guild_id] = {'title': guild_name, 'tasks': {}, 'id': 1}

    if args[0] == "all":
      self.db[guild_id]['tasks'] = dict(sorted(self.db[guild_id]['tasks'].items(), key=lambda item: item[1]['deadline']))

      await ctx.send(f"**{guild_name}**\n" + "\n".join([
          f"**{task_id}**. {task['title']} - Assigned to: {task['assigned_to']} - Deadline: {task['deadline']} - Status: {task['status']}"
          for task_id, task in self.db[guild_id]['tasks'].items()
      ]))
      return

    # TODO: this can be better
    self.db[guild_id]['tasks'] = {
        task_id: task for task_id, task in self.db[guild_id]['tasks'].items() if task['status'] == 'in progress'
    }
    if not self.db[guild_id]['tasks']:
        await ctx.send(f"**{guild_name}**\nNo tasks found!")
        return

    self.db[guild_id]['tasks'] = dict(sorted(self.db[guild_id]['tasks'].items(), key=lambda item: item[1]['deadline']))

    # TODO: this needs to verify character limit / maybe paginate
    await ctx.send(f"**{guild_name}**\n" + "\n".join([
        f"**{task_id}**. {task['title']} - Assigned to: {task['assigned_to']} - Deadline: {task['deadline']}"
        for task_id, task in self.db[guild_id]['tasks'].items()
    ]))

  @commands.command(name="tend", help="Ends a task")
  async def tend(self, ctx, task_id):
    # $tend

    guild_name = str(ctx.guild.name)
    guild_id = str(ctx.guild.id)
    if guild_id not in self.db.keys():
        self.db[guild_id] = {'title': guild_name, 'tasks': {}, 'id': 1}

    if not task_id.isdigit():
      await ctx.send("Please provide a valid task ID.")
      return

    task_id = int(task_id)

    if task_id not in self.db[guild_id]['tasks'].keys():
      await ctx.send("Task not found.")
      return
    self.db[guild_id]['tasks'][task_id]['status'] = 'finished'
    self.db[guild_id]['tasks'][task_id]['finished_by'] = str(ctx.author)
    self.db[guild_id]['tasks'][task_id]['finished_on'] = str(ctx.message.created_at).split(" ")[0]

    print(str(ctx.message.created_at).split(" ")[0])
    await ctx.send(f"Task {task_id} marked as finished by {ctx.author}.")