#!/usr/bin/env python
# browser_agent.py
#
# Changes:
# - Refactored for maintainability: split long functions into helpers, improved type hints and docstrings, organized imports, and standardized logging messages. No logic was changed.

import argparse
import asyncio
import logging
import os
from typing import Any, Optional, Tuple
from dotenv import load_dotenv
from browser_use import Agent, Browser, Controller, ActionResult
from browser_use.browser.browser import BrowserConfig
from app.services.browser.anchor_browser import create_anchor_browser_session
from app.services.llm_factory import LLMFactory

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

controller = Controller()

def _log_and_return_action(action: str, detail: str, is_done: bool = False) -> ActionResult:
    """Helper to log and return an ActionResult."""
    logger.info(f"[ACTION] {action} | Detail: {detail}")
    return ActionResult(is_done=is_done, extracted_content=detail)

@controller.registry.action("Task has been completed")
async def done(text: str) -> ActionResult:
    """Action for marking a task as completed."""
    return _log_and_return_action("Task Completed", text, is_done=True)

@controller.registry.action("Get credentials for a website")
async def get_credentials(website_url: str) -> ActionResult:
    """Action for retrieving credentials for a website."""
    creds = "username:  test@provision.ai and password: test123"
    logger.info(f"[ACTION] Get Credentials | Website: {website_url} | Credentials Provided: {creds}")
    return ActionResult(extracted_content=creds)

@controller.registry.action("Need information to fill out a form field")
async def get_form_data(form_field: str) -> ActionResult:
    logger.info(f"[ACTION] Help me fill the form | Form Field: {form_field}")
    return ActionResult(extracted_content=input(f'\n{form_field}\nInput: '))

@controller.registry.action("Stuck at captcha ")
async def ask_human(question: str) -> ActionResult:
    """Action for requesting human input when stuck at a captcha."""
    logger.info(f"[ACTION] Stuck at Captcha | Question: {question}")
    return ActionResult(extracted_content=input(f'\n{question}\nInput: '))

@controller.registry.action("Request human to takeover the session to unblock on a step")
async def human_handover(request: str) -> ActionResult:
    """Action for requesting human takeover of the session."""
    logger.info(f"[ACTION] Human Handover | Request: {request}")
    return ActionResult(extracted_content=input(f'\n{request}\nInput: '))

def _is_container_environment() -> bool:
    """Check if running inside a container environment."""
    return os.environ.get("CONTAINER", "").lower() == "true" or os.path.exists("/.dockerenv")

def _get_browser_args(is_container: bool) -> list[str]:
    """Get browser arguments based on environment."""
    browser_args = [
        "--disable-dev-shm-usage",
        "--no-sandbox",
        "--disable-setuid-sandbox"
    ]
    if is_container:
        browser_args.extend([
            "--disable-gpu",
            "--disable-software-rasterizer",
            "--single-process"
        ])
    return browser_args

def _create_browser_config(is_container: bool) -> BrowserConfig:
    """Create a BrowserConfig object based on environment."""
    headless = os.environ.get("BROWSER_USE_HEADLESS", "true").lower() == "true"
    browser_args = _get_browser_args(is_container)
    logger.info(f"[BROWSER] Creating browser config | Headless: {headless} | Args: {browser_args}")
    return BrowserConfig(
        headless=headless,
        extra_chromium_args=browser_args
    )

def _create_agent(task: str, model_provider: str, model_name: str, browser: Browser, sensitive_data: Any = None) -> Agent:
    """Helper to create an Agent instance."""
    logger.info(f"[AGENT] Creating agent | Task: {task} | Model: {model_provider}/{model_name}")
    return Agent(
        task=task,
        llm=LLMFactory.create_llm(model_provider, model_name=model_name),
        browser=browser,
        sensitive_data=sensitive_data,
        controller=controller
    )

async def create_browser_agent(
    task: str,
    model_provider: str = "openai_chat",
    model_name: str = "gpt-4o",
    sensitive_data: Any = None
) -> Tuple[Agent, Optional[str]]:
    """
    Create a browser agent, preferring Anchor Browser if available, otherwise fallback to local browser.
    Returns a tuple of (Agent, live_view_url or None).
    """
    try:
        logger.info("[AGENT] Attempting to create Anchor Browser session...")
        session_id, cdp_url, live_view_url = await create_anchor_browser_session()
        if session_id and cdp_url:
            logger.info(f"[AGENT] Using Anchor Browser session | Session ID: {session_id}")
            browser_config = BrowserConfig(
                cdp_url=cdp_url,
                extra_chromium_args=[
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-gpu",
                    "--disable-software-rasterizer"
                ]
            )
            browser = Browser(config=browser_config)
            agent = _create_agent(task, model_provider, model_name, browser, sensitive_data)
            return agent, live_view_url
    except Exception as e:
        logger.error(f"[AGENT] Error creating Anchor Browser session: {e}", exc_info=True)
    # Fallback to local browser
    is_container = _is_container_environment()
    if is_container:
        logger.info("[AGENT] Running in container environment, configuring browser accordingly...")
    browser_config = _create_browser_config(is_container)
    browser = Browser(config=browser_config)
    agent = _create_agent(task, model_provider, model_name, browser, sensitive_data)
    return agent, None

async def run(task: str, model_provider: str = "openai_chat", model_name: str = "gpt-4o") -> None:
    """Run a single LLM task and print the result."""
    logger.info(f"[RUN] Running LLM task | Task: {task} | Model: {model_provider}/{model_name}")
    llm = LLMFactory.create_llm(model_provider, model_name=model_name)
    result = llm.invoke(task)
    print(result.content)

async def run_agent(task: str, model_provider: str, model_name: str) -> Any:
    """Run the browser agent with the specified task."""
    try:
        logger.info(f"[RUN_AGENT] Starting agent run | Task: {task} | Model: {model_provider}/{model_name}")
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
        print(f"\n🚀 Starting agent execution...")
        print(f"{'=' * 80}\n")
        result = await agent.run()
        print(f"\n{'=' * 80}")
        print(f"✅ Agent execution complete")
        print(f"Final output: {result.final_result()}")
        print(f"{'=' * 80}\n")
        logger.info(f"[RUN_AGENT] Agent execution complete | Task: {task}")
        return result
    except Exception as e:
        logger.error(f"[RUN_AGENT] Error running agent: {e}", exc_info=True)
        print(f"\n❌ Error running agent: {e}")
        raise

def main() -> None:
    """Parse command line arguments and run the agent."""
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