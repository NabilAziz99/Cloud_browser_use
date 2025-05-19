#!/usr/bin/env python
# app/services/task_manager.py

import asyncio
import logging
import uuid
from typing import Dict, Optional, Tuple, Any

from app.services.task_states import TaskStatus
from browser_use.agent.service import Agent

# Configure logging
logger = logging.getLogger(__name__)

class TaskManager:
    """
    Manages tasks running in the system, providing task lifecycle operations.
    """
    _running_agents: Dict[uuid.UUID, Tuple[Agent, TaskStatus]] = {}
    _running_tasks: Dict[uuid.UUID, asyncio.Task] = {}
    _live_urls: Dict[uuid.UUID, str] = {}  # Added missing definition here

    @classmethod
    async def create_task(cls, task: str, model_provider: str = "openai_chat", model_name: str = "gpt-4o", sensitive_data=None) -> Tuple[
        uuid.UUID, str]:
        """
        Create a new task and return its ID and live URL for monitoring.

        Returns:
            tuple: (task_id, live_url) where live_url may be None if not available
        """
        task_id = uuid.uuid4()

        # Import here to avoid circular import
        from app.services.browser.browser_agent import create_browser_agent
        
        # Create the browser agent and get the live URL
        agent, live_url = await create_browser_agent(
            task=task,
            task_id=task_id,  # Pass the task_id
            model_provider=model_provider,
            model_name=model_name,
            sensitive_data=sensitive_data
        )

        # Store the agent and its status directly
        cls._running_agents[task_id] = (agent, TaskStatus.CREATED)
        
        # Store the live URL if available
        if live_url:
            cls._live_urls[task_id] = live_url

        # Create a task but DO NOT await it
        task_obj = asyncio.create_task(cls._run_agent_task(agent, task_id))
        cls._running_tasks[task_id] = task_obj

        # Update status to RUNNING
        cls._running_agents[task_id] = (agent, TaskStatus.RUNNING)

        # Return both the task ID and the live URL
        return task_id, live_url

    @classmethod
    async def _run_agent_task(cls, agent, task_id):
        """Run the agent and manage task status transitions"""
        try:
            # Status should already be RUNNING when this starts
            await agent.run()
            # Update to FINISHED on successful completion
            if task_id in cls._running_agents:
                agent, _ = cls._running_agents[task_id]
                cls._running_agents[task_id] = (agent, TaskStatus.FINISHED)
        except Exception as e:
            # Update to FAILED on error
            if task_id in cls._running_agents:
                agent, _ = cls._running_agents[task_id]
                cls._running_agents[task_id] = (agent, TaskStatus.FAILED)
            logging.error(f"Error in agent task {task_id}: {e}")

    @classmethod
    async def stop_task(cls, task_id: uuid.UUID) -> bool:
        """
        Stop a running task.

        Args:
            task_id (uuid.UUID): The ID of the task to stop

        Returns:
            bool: True if the task was successfully stopped, False otherwise
        """
        if task_id in cls._running_agents:
            # Extract agent and current status from the tuple
            agent, status = cls._running_agents[task_id]
            task = cls._running_tasks.get(task_id)
            # Only attempt to stop if not already stopped or finished
            if status not in [TaskStatus.STOPPED, TaskStatus.FINISHED, TaskStatus.FAILED]:
                # Call the agent's stop method
                agent.stop()

                # Update the task status to STOPPED
                cls._running_agents[task_id] = (agent, TaskStatus.STOPPED)

                # Wait briefly for the agent to process the stop flag
                await asyncio.sleep(0.4)

                # Optionally cancel the task if it's still running
                if task and not task.done():
                    task.cancel()
                    try:
                        await asyncio.wait_for(task, timeout=1.0)
                    except (asyncio.CancelledError, asyncio.TimeoutError):
                        pass

                logger.info(f"Task {task_id} stopped successfully")
                return True
            else:
                logger.warning(f"Cannot stop task {task_id} - current status: {status}")
                return False
        else:
            logger.warning(f"Task {task_id} not found.")
            return False

    @classmethod
    async def get_task_status(cls, task_id: uuid.UUID) -> str:
        """
        Get the status of a task.

        Args:
            task_id (uuid.UUID): The ID of the task to check

        Returns:
            str: The current status of the task

        Raises:
            KeyError: If the task ID is not found
        """
        if task_id in cls._running_agents:
            # The _running_agents dictionary stores tuples of (Agent, TaskStatus)
            _, status = cls._running_agents[task_id]
            return status.value
        else:
            # Task ID not found in our tracking system
            raise KeyError(f"Task with ID {task_id} not found")

    @classmethod
    async def pause_task(cls, task_id: uuid.UUID) -> bool:
        """
        Pause a running task.

        Args:
            task_id (uuid.UUID): The ID of the task to pause

        Returns:
            bool: True if the task was successfully paused, False otherwise
        """
        if task_id in cls._running_agents:
            agent, status = cls._running_agents[task_id]

            # Only pause if the task is currently running
            if status == TaskStatus.RUNNING:
                try:
                    # Call the agent's pause method
                    agent.pause()

                    # Wait briefly for the agent to process the pause flag
                    await asyncio.sleep(0.2)

                    # Update the task status
                    cls._running_agents[task_id] = (agent, TaskStatus.PAUSED)
                    
                    # Also update the registry if available
                    from app.services.browser.agent_registry import AgentRegistry
                    AgentRegistry.update_agent_status(task_id, TaskStatus.PAUSED)
                    
                    logger.info(f"Task {task_id} paused successfully")
                    return True
                except Exception as e:
                    logger.error(f"Error pausing task {task_id}: {e}")
                    return False
            else:
                logger.warning(f"Cannot pause task {task_id} - current status: {status}")
                return False
        else:
            logger.warning(f"Task {task_id} not found.")
            return False

    @classmethod
    async def resume_task(cls, task_id: uuid.UUID) -> bool:
        """
        Resume a paused task.

        Args:
            task_id (uuid.UUID): The ID of the task to resume

        Returns:
            bool: True if the task was successfully resumed, False otherwise
        """
        if task_id in cls._running_agents:
            agent, status = cls._running_agents[task_id]

            # Only resume if the task is currently paused
            if status == TaskStatus.PAUSED:
                try:
                    # Call the agent's resume method
                    agent.resume()

                    # Wait briefly for the agent to process the resume flag
                    await asyncio.sleep(0.2)

                    # Update the task status
                    cls._running_agents[task_id] = (agent, TaskStatus.RUNNING)
                    
                    # Also update the registry if available
                    from app.services.browser.agent_registry import AgentRegistry
                    AgentRegistry.update_agent_status(task_id, TaskStatus.RUNNING)
                    
                    logger.info(f"Task {task_id} resumed successfully")
                    return True
                except Exception as e:
                    logger.error(f"Error resuming task {task_id}: {e}")
                    return False
            else:
                logger.warning(f"Cannot resume task {task_id} - current status: {status}")
                return False
        else:
            logger.warning(f"Task {task_id} not found.")
            return False

# Add this method to your TaskManager class

    @classmethod
    def add_human_feedback(cls, task_id: uuid.UUID, feedback: str) -> bool:
        """
        Add human feedback to a paused task and prepare it for resuming.
        
        Args:
            task_id: The UUID of the task to receive feedback
            feedback: The feedback string to provide to the agent
                
        Returns:
            bool: True if feedback was successfully added
                
        Raises:
            KeyError: If task not found
            ValueError: If task is not in PAUSED status
        """
        if task_id not in cls._running_agents:
            logging.error(f"Cannot add feedback - Task with ID {task_id} not found")
            raise KeyError(f"Task with ID {task_id} not found")
        
        agent, status = cls._running_agents[task_id]
        if status != TaskStatus.PAUSED:
            logging.error(f"Cannot add feedback - Task {task_id} is not paused (status: {status.value})")
            raise ValueError(f"Task must be in PAUSED status to receive feedback, current status: {status.value}")
        
        # Clear any pending request information
        from app.services.browser.controller_actions import pending_requests
        if task_id in pending_requests:
            # Optionally log what request is being fulfilled
            request_info = pending_requests.pop(task_id)
            logging.info(f"Fulfilling human input request for task {task_id}. Request: {request_info['prompt']}")
        
        # Add the feedback to the agent
        try:
            logging.info(f"Adding human feedback to task {task_id}: {feedback[:50]}...")
            agent.add_new_task(feedback)
            return True
        except Exception as e:
            logging.error(f"Error adding feedback to task {task_id}: {e}")
            raise


    # TODO: Currently its creating an new ID for each step every single api while, which makes it inconsisten
    @classmethod
    async def get_task_details(cls, task_id: uuid.UUID) -> dict:
        """
        Get comprehensive task details including live URL, steps, output and status.
        """
        try:
            logging.info(f"Attempting to get details for task {task_id}")
            
            if task_id not in cls._running_agents:
                logging.warning(f"Task {task_id} not found in _running_agents")
                raise KeyError(f"Task with ID {task_id} not found")

            agent, status = cls._running_agents[task_id]
            logging.info(f"Found agent for task {task_id} with status {status.value}")

            # Get the live URL (initialize if needed)
            if not hasattr(cls, "_live_urls"):
                cls._live_urls = {}
            live_url = cls._live_urls.get(task_id)

            # Basic response that should always work
            details = {
                "id": str(task_id),
                "task": getattr(agent, "task", "Unknown task"),
                "status": status.value,
                "created_at": "2023-11-07T05:31:56Z",  # Placeholder
                "finished_at": None,
                "steps": [],
                "output": None,
                "live_url": live_url,
                "browser_data": None
            }

            # Try to get steps information - with full exception handling
            try:
                if hasattr(agent, "state"):
                    if hasattr(agent.state, "history") and agent.state.history:
                        if hasattr(agent.state.history, "history") and agent.state.history.history:
                            for i, history_item in enumerate(agent.state.history.history):
                                step = {
                                    "id": str(uuid.uuid4()),  # Generate a unique ID for each step
                                    "step": i + 1,
                                    "evaluation_previous_goal": "N/A",
                                    "next_goal": "N/A"
                                }
                                
                                if hasattr(history_item, "model_output") and history_item.model_output:
                                    if hasattr(history_item.model_output, "current_state"):
                                        current_state = history_item.model_output.current_state
                                        if hasattr(current_state, "evaluation_previous_goal"):
                                            step["evaluation_previous_goal"] = current_state.evaluation_previous_goal
                                        if hasattr(current_state, "next_goal"):
                                            step["next_goal"] = current_state.next_goal
                                
                                details["steps"].append(step)
            except Exception as e:
                logging.error(f"Error getting step details for task {task_id}: {e}")
                # Continue without failing the whole request

            # Get output if task is finished - with exception handling
            try:
                if status == TaskStatus.FINISHED:
                    if hasattr(agent, "state") and hasattr(agent.state, "history"):
                        if hasattr(agent.state.history, "is_done") and agent.state.history.is_done():
                            if hasattr(agent.state.history, "final_result"):
                                details["output"] = agent.state.history.final_result()
            except Exception as e:
                logging.error(f"Error getting output for task {task_id}: {e}")
                # Continue without failing the whole request

            return details
        except Exception as e:
            logging.error(f"Unexpected error in get_task_details for task {task_id}: {e}", exc_info=True)
            raise