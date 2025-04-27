from google.adk.agents import Agent
from .tools import say_hello
from .prompts import return_instructions

MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"

greeting_agent = None
try:
    greeting_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="greeting_agent",
        instruction=return_instructions(),
        description="Handles simple greetings and hellos using the 'say_hello' tool.", # Crucial for delegation
        tools=[say_hello],
    )
    print(f"✅ Agent '{greeting_agent.name}' created using model '{MODEL_GEMINI_2_0_FLASH}'.")
except Exception as e:
    print(f"❌ Could not create Greeting agent. Check API Key ({MODEL_GEMINI_2_0_FLASH}). Error: {e}")
