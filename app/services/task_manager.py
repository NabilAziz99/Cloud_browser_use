import asyncio
import logging
import uuid
from typing import Dict, Optional

from browser_use.agent.service import Agent
from app.services.browser.browser_agent import create_browser_agent


from enum import Enum

class TaskStatus(Enum):
    CREATED = "created"    # Task is initialized but not yet started
    RUNNING = "running"    # Task is currently executing
    FINISHED = "finished"  # Task has completed successfully
    STOPPED = "stopped"    # Task was manually stopped
    PAUSED = "paused"      # Task execution is temporarily paused
    FAILED = "failed"      # Task encountered an error and could not complete

class TaskManager:
    _running_agents: Dict[uuid.UUID, tuple[Agent, TaskStatus]] = {}
    _running_tasks: Dict[uuid.UUID, asyncio.Task] = {}  # Fixed name (was _running_task in your code)
    _live_urls: Dict[uuid.UUID, str] = {}


    @classmethod
    async def create_task(cls, task: str, model_provider: str = "openai_chat", model_name: str = "gpt-4o", sensitive_data=None) -> tuple[
        uuid.UUID, str]:
        """
        Create a new task and return its ID and live URL for monitoring.

        Returns:
            tuple: (task_id, live_url) where live_url may be None if not available
        """
        task_id = uuid.uuid4()

        # Create the browser agent and get the live URL
        agent, live_url = await create_browser_agent(
            task=task,
            model_provider=model_provider,
            model_name=model_name,
            sensitive_data=sensitive_data
        )

        # Store the agent and its status
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

                logging.info(f"Task {task_id} stopped successfully")
                return True
            else:
                logging.warning(f"Cannot stop task {task_id} - current status: {status}")
                return False
        else:
            logging.warning(f"Task {task_id} not found.")
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
                # Call the agent's pause method
                agent.pause()

                # Wait briefly for the agent to process the pause flag
                await asyncio.sleep(0.2)

                # Update the task status
                cls._running_agents[task_id] = (agent, TaskStatus.PAUSED)
                logging.info(f"Task {task_id} paused successfully")
                return True
            else:
                logging.warning(f"Cannot pause task {task_id} - current status: {status}")
                return False
        else:
            logging.warning(f"Task {task_id} not found.")
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
                # Call the agent's resume method
                agent.resume()

                # Wait briefly for the agent to process the resume flag
                await asyncio.sleep(0.2)

                # Update the task status
                cls._running_agents[task_id] = (agent, TaskStatus.RUNNING)
                logging.info(f"Task {task_id} resumed successfully")
                return True
            else:
                logging.warning(f"Cannot resume task {task_id} - current status: {status}")
                return False
        else:
            logging.warning(f"Task {task_id} not found.")
            return False


    @classmethod
    async def get_task_details(cls, task_id: uuid.UUID) -> dict:
        """
        Get task details including live URL.
        """
        if task_id not in cls._running_agents:
            raise KeyError(f"Task with ID {task_id} not found")

        agent, status = cls._running_agents[task_id]

        # Get the live URL
        live_url = cls._live_urls.get(task_id)

        # Basic implementation for now
        return {
            "id": str(task_id),
            "task": agent.task,
            "status": status.value,
            "live_url": live_url
    }

    # Update this method in app/services/task_manager.py

    @classmethod
    async def get_task_details(cls, task_id: uuid.UUID) -> dict:
        """
        Get comprehensive task details including live URL, steps, output and status.
        """
        if task_id not in cls._running_agents:
            raise KeyError(f"Task with ID {task_id} not found")

        agent, status = cls._running_agents[task_id]

        # Get the live URL
        live_url = cls._live_urls.get(task_id)

        # Get creation timestamp
        created_at = None
        # Get finished timestamp if available
        finished_at = None

        # Get steps information if available
        steps = []
        if hasattr(agent.state, "history") and agent.state.history.history:
            for i, history_item in enumerate(agent.state.history.history):
                if history_item.model_output:
                    steps.append({
                        "id": str(uuid.uuid4()),  # Generate a unique ID for each step
                        "step": i + 1,
                        "evaluation_previous_goal": history_item.model_output.current_state.evaluation_previous_goal,
                        "next_goal": history_item.model_output.current_state.next_goal
                    })

        # Get output if task is finished
        output = None
        if status == TaskStatus.FINISHED and agent.state.history.is_done():
            output = agent.state.history.final_result()

        # Get browser data if available (cookies, etc.)
        browser_data = None
        # You would need to implement logic to extract browser data here

        return {
            "id": str(task_id),
            "task": agent.task,
            "output": output,
            "status": status.value,
            "created_at": created_at or "2023-11-07T05:31:56Z",  # Placeholder - implement actual timestamp
            "finished_at": finished_at,
            "steps": steps,
            "live_url": live_url,
            "browser_data": browser_data
        }