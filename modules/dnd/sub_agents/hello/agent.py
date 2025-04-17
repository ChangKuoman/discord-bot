from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from modules.dnd.sub_agents.hello.tools import say_hello

MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"

greeting_agent = None
try:
    greeting_agent = Agent(
        # Using a potentially different/cheaper model for a simple task
        model=MODEL_GEMINI_2_0_FLASH,
        name="greeting_agent",
        instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting to the user. "
                    "Use the 'say_hello' tool to generate the greeting. "
                    "If the user provides their name, make sure to pass it to the tool. "
                    "Do not engage in any other conversation or tasks.",
        description="Handles simple greetings and hellos using the 'say_hello' tool.", # Crucial for delegation
        tools=[say_hello],
    )
    print(f"✅ Agent '{greeting_agent.name}' created using model '{MODEL_GEMINI_2_0_FLASH}'.")
except Exception as e:
    print(f"❌ Could not create Greeting agent. Check API Key ({MODEL_GEMINI_2_0_FLASH}). Error: {e}")
