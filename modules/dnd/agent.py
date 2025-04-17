# === IMPORTS ===

import os
import asyncio
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm # For multi-model support
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types # For creating message Content/Parts

from tools import get_weather # Import the tool function

import warnings
# Ignore all warnings
warnings.filterwarnings("ignore")

# === AGENT ===

MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"

weather_agent = Agent(
    name="weather_agent_v1",
    model=MODEL_GEMINI_2_0_FLASH, # Can be a string for Gemini or a LiteLlm object
    description="Provides weather information for specific cities.",
    instruction="You are a helpful weather assistant. "
                "When the user asks for the weather in a specific city, "
                "use the 'get_weather' tool to find the information. "
                "If the tool returns an error, inform the user politely. "
                "If the tool is successful, present the weather report clearly.",
    tools=[get_weather], # Pass the function directly
)

# === SESSION ===

session_service = InMemorySessionService()

# Define constants for identifying the interaction context
APP_NAME = "weather_tutorial_app"
USER_ID = "user_1"
SESSION_ID = "session_001" # Using a fixed ID for simplicity

# Create the specific session where the conversation will happen
session = session_service.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID
)

# === RUNNER ===

# Key Concept: Runner orchestrates the agent execution loop.
runner = Runner(
    agent=weather_agent, # The agent we want to run
    app_name=APP_NAME,   # Associates runs with our app
    session_service=session_service # Uses our session manager
)

# agent interaction

async def call_agent_async(query: str, runner, user_id, session_id):
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

# === RUN ===
async def run_conversation():
    res = await call_agent_async("What is the weather like in London?",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID)
    print(res) # Expecting a successful weather report
    res = await call_agent_async("How about Paris?",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID) # Expecting the tool's error message
    print(res)
    res = await call_agent_async("Tell me the weather in Lima",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID)
    print(res) # Expecting the tool's error message
# Execute the conversation using await in an async context (like Colab/Jupyter)
asyncio.run(run_conversation())
