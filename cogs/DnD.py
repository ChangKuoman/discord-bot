from discord.ext import commands
import discord
from modules import dnd_agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

class DnD(commands.Cog):
  """Commands for DnD roleplaying game."""

  def __init__(self, client):
    self.CLIENT = client
    self.COLOR = 0xcb1aee

    # initializes the setup for agent ai
    session_service = InMemorySessionService()

    # Define constants for identifying the interaction context
    APP_NAME = "weather_tutorial_app"
    self.USER_ID = "user_1"
    self.SESSION_ID = "session_001" # Using a fixed ID for simplicity

    # Create the specific session where the conversation will happen
    session = session_service.create_session(
        app_name=APP_NAME,
        user_id=self.USER_ID,
        session_id=self.SESSION_ID
    )

    # === RUNNER ===

    # Key Concept: Runner orchestrates the agent execution loop.
    self.runner = Runner(
        agent=dnd_agent, # The agent we want to run
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

  @commands.command(name="d", help="Dnd test command")
  async def d(self, ctx, *msg):
    msg = " ".join(msg)
    res = await self.call_agent_async(query=msg,
                            runner=self.runner,
                            user_id=self.USER_ID,
                            session_id=self.SESSION_ID)
    embed = discord.Embed(
      title="Foca-AI DnD",
      description=res,
      color=self.COLOR
    )
    await ctx.send(embed=embed)
