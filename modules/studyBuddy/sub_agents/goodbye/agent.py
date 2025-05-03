from google.adk.agents import Agent
from .tools import say_goodbye
from .prompts import return_instructions

MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"

farewell_agent = None
try:
    farewell_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="farewell_agent",
        instruction=return_instructions(),
        description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.", # Crucial for delegation
        tools=[say_goodbye],
    )
    print(f"✅ Agent '{farewell_agent.name}' created using model '{MODEL_GEMINI_2_0_FLASH}'.")
except Exception as e:
    print(f"❌ Could not create Farewell agent. Check API Key ({MODEL_GEMINI_2_0_FLASH}). Error: {e}")