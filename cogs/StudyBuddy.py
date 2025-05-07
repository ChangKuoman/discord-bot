from discord.ext import commands
import discord
from modules import study_buddy_agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

class StudyBuddy(commands.Cog):
  """Commands for studying using AI agents."""

  def __init__(self, client):
    self.CLIENT = client
    self.COLOR = 0xcb1aee
    self.FILE_PATH = "assets/downloads/studyBuddy/"

    session_service = InMemorySessionService()

    APP_NAME = "study_buddy_app"
    self.USER_ID = "user_1"
    self.SESSION_ID = "session_001"

    session = session_service.create_session(
        app_name=APP_NAME,
        user_id=self.USER_ID,
        session_id=self.SESSION_ID
    )

    # === RUNNER ===
    self.runner = Runner(
        agent=study_buddy_agent, # The agent we want to run
        app_name=APP_NAME,   # Associates runs with our app
        session_service=session_service # Uses our session manager
    )

  async def call_agent_async(self, query: str, runner, user_id, session_id):
        print(f"Calling agent with query: {query}")
        content = types.Content(role='user', parts=[types.Part(text=query)])
        final_response_text = "Agent did not produce a final response." # Default

        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):

            if event.is_final_response():
                if event.content and event.content.parts:
                    # Assuming text response in the first part
                    final_response_text = event.content.parts[0].text
                elif event.actions and event.actions.escalate: # Handle potential errors/escalations
                    final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
                break # Stop processing events once the final response is found

        return final_response_text

  @commands.command(name="study", aliases=["stu"], help="Study command")
  async def study(self, ctx, *msg):
    msg = " ".join(msg)

    if ctx.message.attachments:
        attachment_list = []
        for attachment in ctx.message.attachments:
            if attachment.filename.endswith(".pdf"):
                await attachment.save(f"{self.FILE_PATH}{attachment.filename}")
                attachment_list.append(f"{self.FILE_PATH}{attachment.filename}")

        query = f"Read this file(s): {', '.join(attachment_list)}. {msg}"
    else:
        query = msg

    res = await self.call_agent_async(query=query,
                            runner=self.runner,
                            user_id=self.USER_ID,
                            session_id=self.SESSION_ID)
    embed = discord.Embed(
      title="Study Buddy Foca-AI",
      description=res,
      color=self.COLOR
    )
    await ctx.send(embed=embed)
