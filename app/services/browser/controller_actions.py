#!/usr/bin/env python
# app/services/browser/controller_actions.py

import logging
import uuid
from typing import Optional, Dict, Any
from browser_use import ActionResult
from app.services.task_states import TaskStatus

logger = logging.getLogger(__name__)

# Store request context for pending human input requests
pending_requests: Dict[uuid.UUID, Dict[str, Any]] = {}

async def request_human_input(
    prompt: str,
    agent_context: Optional[str] = None,
    input_type: str = "text"
) -> ActionResult:
    """
    Generic function for requesting human input.
    
    Args:
        prompt: The question or message to ask the human
        agent_context: Optional context about what the agent is trying to do
        input_type: Type of input expected (text, choice, etc.)
        
    Returns:
        ActionResult with information about the paused state
    """
    # Import here to avoid circular dependencies
    from app.services.browser.agent_registry import AgentRegistry
    
    # Get current agent and task ID
    agent = AgentRegistry.get_current_agent()
    if not agent:
        logger.error("[HUMAN INPUT] No active agent found")
        return ActionResult(extracted_content="Error: No active agent found")
    
    # Find task ID for this agent
    task_id = AgentRegistry.get_task_id_for_agent(agent)
    if not task_id:
        logger.error("[HUMAN INPUT] Cannot find task ID for agent")
        return ActionResult(extracted_content="Error: Cannot find task ID")
    
    # Generate a unique request ID
    request_id = str(uuid.uuid4())
    
    # Store request information
    pending_requests[task_id] = {
        "request_id": request_id,
        "prompt": prompt,
        "context": agent_context,
        "input_type": input_type,
        "timestamp": None,  # You could add a timestamp here
    }
    
    # Import TaskManager locally to avoid circular imports
    from app.services.task_manager import TaskManager
    
    # Update agent status in registry and pause the agent
    try:
        logger.info(f"[HUMAN INPUT] Pausing task {task_id} for human input: {prompt}")
        # Update status in registry first
        AgentRegistry.update_agent_status(task_id, TaskStatus.PAUSED)
        
        # Then pause via TaskManager
        await TaskManager.pause_task(task_id)
        
        return ActionResult(
            extracted_content=f"Waiting for human input. Request ID: {request_id}. Prompt: {prompt}"
        )
    except Exception as e:
        logger.error(f"[HUMAN INPUT] Error pausing task: {e}")
        return ActionResult(extracted_content=f"Error requesting human input: {str(e)}")

async def done(text: str) -> ActionResult:
    """Action for marking a task as completed."""
    logger.info(f"[ACTION] Task Completed | Detail: {text}")
    return ActionResult(is_done=True, extracted_content=text)




# This function was created for testing purposes, I found it easier to test using a derterministic event like visit website X and if does I would request human feedback, then other event like waiting for the agent to be stuck. 
async def apple_hello(text: str) -> ActionResult:
    """Action that demonstrates requesting human input when on Apple website."""
    logger.info(f"[ACTION] Apple Hello | Received text: {text}")
    
    # Use the generic human input request function
    return await request_human_input(
        prompt="We're on the Apple website! What would you like me to do next?",
        agent_context="The agent is on apple.com and needs further instructions.",
        input_type="text"
    )

async def get_credentials(website_url: str) -> ActionResult:
    """Action for retrieving credentials for a website."""
    creds = "username: test@provision.ai and password: test123"
    logger.info(f"[ACTION] Get Credentials | Website: {website_url} | Credentials Provided: {creds}")
    return ActionResult(extracted_content=creds)

async def get_form_data(form_field: str) -> ActionResult:
    """Action for getting form field information from human."""
    logger.info(f"[ACTION] Help me fill the form | Form Field: {form_field}")
    
    # Use the generic human input request function
    return await request_human_input(
        prompt=f"Please provide a value for this form field: {form_field}",
        agent_context=f"The agent needs input for a form field: {form_field}",
        input_type="text"
    )

async def ask_human(question: str) -> ActionResult:
    """Action for requesting human input when stuck at a captcha."""
    logger.info(f"[ACTION] Stuck at Captcha | Question: {question}")
    
    # Use the generic human input request function
    return await request_human_input(
        prompt=f"CAPTCHA Challenge: {question}",
        agent_context="The agent is stuck at a CAPTCHA and needs human assistance.",
        input_type="text"
    )

async def human_handover(request: str) -> ActionResult:
    """Action for requesting human takeover of the session."""
    logger.info(f"[ACTION] Human Handover | Request: {request}")
    
    # Use the generic human input request function
    return await request_human_input(
        prompt=f"The agent needs your help: {request}",
        agent_context="The agent has explicitly requested human assistance.",
        input_type="text"
    )