import uuid
import logging
from typing import Dict, Optional, Tuple
from browser_use import Agent
from app.services.task_states import TaskStatus

logger = logging.getLogger(__name__)

# Current task context - moved here to be accessible to both modules
current_task_id: Optional[uuid.UUID] = None

class AgentRegistry:
    """
    Thread-safe registry for agent instances that maintains bidirectional mapping
    between agents and task IDs.
    """
    _agents_by_task: Dict[uuid.UUID, Tuple[Agent, TaskStatus]] = {}
    _task_ids_by_agent: Dict[int, uuid.UUID] = {}  # Use object ID as key
    _current_agent: Optional[Agent] = None
    
    @classmethod
    def register_agent(cls, agent: Agent, task_id: uuid.UUID):
        """Register agent with bidirectional mapping"""
        cls._agents_by_task[task_id] = (agent, TaskStatus.RUNNING)
        cls._task_ids_by_agent[id(agent)] = task_id
        cls._current_agent = agent
        logger.info(f"[REGISTRY] Registered agent for task {task_id}")
    
    @classmethod
    def get_current_agent(cls) -> Optional[Agent]:
        """Get the most recently created agent"""
        return cls._current_agent
    
    @classmethod
    def get_agent_by_task(cls, task_id: uuid.UUID) -> Optional[Agent]:
        """Get agent by task ID"""
        agent_tuple = cls._agents_by_task.get(task_id)
        if agent_tuple:
            return agent_tuple[0]
        return None
    
    @classmethod
    def get_task_id_for_agent(cls, agent: Agent) -> Optional[uuid.UUID]:
        """Get task ID for agent in O(1) time"""
        return cls._task_ids_by_agent.get(id(agent))
    
    @classmethod
    def update_agent_status(cls, task_id: uuid.UUID, status: TaskStatus) -> bool:
        """Update the status of an agent"""
        if task_id in cls._agents_by_task:
            agent, _ = cls._agents_by_task[task_id]
            cls._agents_by_task[task_id] = (agent, status)
            logger.info(f"[REGISTRY] Updated task {task_id} status to {status.value}")
            return True
        return False
    
    @classmethod
    def unregister_agent(cls, task_id: uuid.UUID):
        """Clean up both mappings when unregistering"""
        if task_id in cls._agents_by_task:
            agent, _ = cls._agents_by_task[task_id]
            del cls._agents_by_task[task_id]
            
            # Also clean up the reverse mapping
            if id(agent) in cls._task_ids_by_agent:
                del cls._task_ids_by_agent[id(agent)]
            
            # Update current agent if it was this one
            if cls._current_agent == agent:
                cls._current_agent = None
                
            logger.info(f"[REGISTRY] Unregistered agent for task {task_id}")