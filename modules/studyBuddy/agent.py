from google.adk.agents import Agent
from .tools import get_weather
from .sub_agents import greeting_agent, farewell_agent
from .prompts import return_instructions

import warnings
warnings.filterwarnings("ignore")

MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"

root_agent = Agent(
    name="study_buddy_agent_v1",
    model=MODEL_GEMINI_2_0_FLASH,
    description="The main coordinator agent. Handles study requests and delegates questions to specialists.",
    instruction=return_instructions(),
    #tools=[get_weather],
    sub_agents=[greeting_agent, farewell_agent]
    #output_key="last_weather_report"
)
