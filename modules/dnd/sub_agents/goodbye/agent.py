from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from modules.dnd.sub_agents.goodbye.tools import say_goodbye

MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"

farewell_agent = None
try:
    farewell_agent = Agent(
        # Can use the same or a different model
        model=MODEL_GEMINI_2_0_FLASH, # Sticking with GPT for this example
        name="farewell_agent",
        instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message. "
                    "Use the 'say_goodbye' tool when the user indicates they are leaving or ending the conversation "
                    "(e.g., using words like 'bye', 'goodbye', 'thanks bye', 'see you'). "
                    "Do not perform any other actions.",
        description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.", # Crucial for delegation
        tools=[say_goodbye],
    )
    print(f"✅ Agent '{farewell_agent.name}' created using model '{MODEL_GEMINI_2_0_FLASH}'.")
except Exception as e:
    print(f"❌ Could not create Farewell agent. Check API Key ({MODEL_GEMINI_2_0_FLASH}). Error: {e}")