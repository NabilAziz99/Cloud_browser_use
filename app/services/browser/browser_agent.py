#!/usr/bin/env python
# test_browser_agent.py

import asyncio
import argparse
import os
import urllib.parse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import from your existing modules
from app.services.browser.anchor_browser import create_anchor_browser_session
from app.services.llm_factory import LLMFactory
from browser_use import Agent, Browser
from browser_use.browser.browser import BrowserConfig



async def create_browser_agent(task, model_provider: str = "openai_chat", model_name: str = "gpt-4o") -> tuple[Agent, str]:
    # Create a new Anchor Browser session
    session_id, cdp_url, live_view_url = await create_anchor_browser_session()

    if not session_id:
        print("Failed to create Anchor Browser session - exiting")
        raise RuntimeError("Could not create Anchor Browser session")
    else:
        print(f"Using Anchor Browser session: {session_id}")
        browser_config = BrowserConfig(cdp_url=cdp_url)

    # Initialize browser with config
    browser = Browser(config=browser_config)
    agent = Agent(
        task=task,
        llm=LLMFactory.create_llm(model_provider, model_name=model_name),
        browser=browser
    )

    return agent, live_view_url

async def run(task, model_provider: str = "openai_chat", model_name: str = "gpt-4o") :
    llm = LLMFactory.create_llm(model_provider, model_name=model_name)
    result = llm.invoke(task)
    print(result.content)


async def run_agent(task, model_provider, model_name):
    """Run the browser agent with the specified task"""
    # Get both the agent, CDP URL, and live view URL
    agent, live_view_url = await create_browser_agent(
        task=task,
        model_provider=model_provider,
        model_name=model_name
    )



    print(f"\n{'=' * 80}")
    print(f"Task: {task}")
    print(f"Model: {model_provider}/{model_name}")

    if live_view_url:
        print(f"\n🌐 Live Browser URL: {live_view_url}")
        print(
            f"📋 Embed with: <iframe src=\"{live_view_url}\" sandbox=\"allow-same-origin allow-scripts\" allow=\"clipboard-read; clipboard-write\" style=\"border: 0px; width: 100%; height: 600px;\"></iframe>")

    # Rest of the function remains the same
    # ...
    print(f"\n🚀 Starting agent execution...")
    print(f"{'=' * 80}\n")

    try:
        # Run the agent with the specified maximum steps
        result = await agent.run()

        # Print the final result
        print(f"\n{'=' * 80}")
        print(f"✅ Agent execution complete")
        print(f"Final output: {result.final_result()}")
        print(f"{'=' * 80}\n")

        return result
    except KeyboardInterrupt:
        print("\n\n⚠️ Agent execution interrupted by user")
        return None


def main():
    """Parse command line arguments and run the agent"""
    parser = argparse.ArgumentParser(description="Test Browser Agent")
    parser.add_argument("task", help="The task to execute")
    parser.add_argument("--provider", default="openai_chat", help="Model provider (default: openai_chat)")
    parser.add_argument("--model", default="gpt-4o", help="Model name (default: gpt-4o)")
    args = parser.parse_args()

    asyncio.run(run(
        task=args.task,
        model_provider=args.provider,
        model_name=args.model,
    ))


if __name__ == "__main__":
    main()