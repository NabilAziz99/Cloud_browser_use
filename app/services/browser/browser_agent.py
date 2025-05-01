#!/usr/bin/env python
# browser_agent.py
#
# Changes:
# - Updated create_browser_agent to accept a sensitive_data parameter and pass it to the Agent constructor.
#
# This allows sensitive data to be securely passed to the agent for use in tasks, as per browser-use documentation.

import asyncio
import argparse
import os
import logging
import urllib.parse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import from your existing modules
from app.services.browser.anchor_browser import create_anchor_browser_session
from app.services.llm_factory import LLMFactory
from browser_use import Agent, Browser, Controller, ActionResult
from browser_use.browser.browser import BrowserConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

controller = Controller()
@controller.registry.action("Task has been completed")
async def done(text: str) -> ActionResult:
    logger.info(f"** Done with task: {text}")
    return ActionResult(is_done=True, extracted_content=text)

@controller.registry.action("Get credentials for a website")
async def get_credentials(website_url: str) -> ActionResult:
    logger.info(f"** Get Credentials: {website_url}")
    return ActionResult(extracted_content="username: obaid@magicallyhq.com and password: Ppak1408!!")

@controller.registry.action("Stuck at captcha")
async def ask_human(question: str) -> ActionResult:
    logger.info(f"** Asking human: {question}")
    return ActionResult(extracted_content=input(f'\n{question}\nInput: '))

@controller.registry.action("Request human to takeover the session to unblock on a step")
async def human_handover(request: str) -> ActionResult:
    logger.info(f"Asking human: {request}")
    return ActionResult(extracted_content=input(f'\n{request}\nInput: '))

async def create_browser_agent(task, model_provider: str = "openai_chat", model_name: str = "gpt-4o", sensitive_data=None) -> tuple[
    Agent, str]:
    # First try to create an Anchor Browser session
    try:
        logger.info("Attempting to create Anchor Browser session...")
        session_id, cdp_url, live_view_url = await create_anchor_browser_session()

        if session_id and cdp_url:
            logger.info(f"Using Anchor Browser session: {session_id}")
            browser_config = BrowserConfig(
                cdp_url=cdp_url,
                # Add container-friendly browser args - these will be passed to local browser if used
                extra_chromium_args=[
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-gpu",
                    "--disable-software-rasterizer"
                ]
            )

            # Initialize browser with config
            browser = Browser(config=browser_config)
            agent = Agent(
                task=task,
                llm=LLMFactory.create_llm(model_provider, model_name=model_name),
                browser=browser,
                sensitive_data=sensitive_data,
                controller=controller
            )

            return agent, live_view_url
    except Exception as e:
        logger.error(f"Error creating Anchor Browser session: {e}")
        # If we can't use Anchor Browser, we'll try to create a local browser below

    # If we get here, we couldn't use Anchor Browser
    # Check if we're in a container environment
    is_container = os.environ.get("CONTAINER", "").lower() == "true" or os.path.exists("/.dockerenv")

    if is_container:
        logger.info("Running in container environment, configuring browser accordingly...")

    # Configure local browser with appropriate settings
    headless = os.environ.get("BROWSER_USE_HEADLESS", "true").lower() == "true"
    browser_args = [
        "--disable-dev-shm-usage",
        "--no-sandbox",
        "--disable-setuid-sandbox"
    ]

    if is_container:
        browser_args.extend([
            "--disable-gpu",
            "--disable-software-rasterizer",
            "--single-process"  # Try this if you have memory issues
        ])

    logger.info(f"Creating local browser with args: {browser_args}")
    browser_config = BrowserConfig(
        headless=headless,
        extra_chromium_args=browser_args
    )

    # Initialize browser with config
    browser = Browser(config=browser_config)
    agent = Agent(
        task=task,
        llm=LLMFactory.create_llm(model_provider, model_name=model_name),
        browser=browser,
        sensitive_data=sensitive_data,
        controller=controller
    )

    # No live view URL for local browser
    return agent, None


async def run(task, model_provider: str = "openai_chat", model_name: str = "gpt-4o"):
    llm = LLMFactory.create_llm(model_provider, model_name=model_name)
    result = llm.invoke(task)
    print(result.content)


async def run_agent(task, model_provider, model_name):
    """Run the browser agent with the specified task"""
    try:
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
        print(f"\n🚀 Starting agent execution...")
        print(f"{'=' * 80}\n")

        # Run the agent with the specified maximum steps
        result = await agent.run()

        # Print the final result
        print(f"\n{'=' * 80}")
        print(f"✅ Agent execution complete")
        print(f"Final output: {result.final_result()}")
        print(f"{'=' * 80}\n")

        return result
    except Exception as e:
        logger.error(f"Error running agent: {e}", exc_info=True)
        print(f"\n❌ Error running agent: {e}")
        raise


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