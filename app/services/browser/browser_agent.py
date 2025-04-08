from langchain_openai import ChatOpenAI
from browser_use import Agent, Browser
from browser_use.browser.browser import BrowserConfig
import asyncio
from dotenv import load_dotenv
from app.services.llm_factory import LLMFactory
from app.services.browser.anchor_browser import create_anchor_browser_session
import os

# Load environment variables
load_dotenv()

# Get Anchor API key
ANCHOR_API_KEY = os.getenv("ANCHOR_API_KEY")

async def execute_task(task: str, model_provider: str = "openai_chat", model_name: str = "gpt-4o"):
    # Create a new Anchor Browser session
    session_id = create_anchor_browser_session()
    
    if not session_id:
        print("Failed to create Anchor Browser session")
        browser_config = BrowserConfig(headless=False)
    else:
        print(f"Using Anchor Browser session: {session_id}")
        # Use the correct connection format for Anchor Browser
        browser_config = BrowserConfig(
            cdp_url=f"wss://connect.anchorbrowser.io?apiKey={ANCHOR_API_KEY}&sessionId={session_id}"
        )
    
    # Initialize browser with config
    browser = Browser(config=browser_config)
    
    # Pass browser to agent
    agent = Agent(
        task=task,
        llm=LLMFactory.create_llm(model_provider, model_name=model_name),
        browser=browser
    )
    
    # Run the agent
    await agent.run()

if __name__ == "__main__":
    asyncio.run(execute_task("Search for latest Nvidia news"))