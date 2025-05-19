
import uuid
from enum import Enum
from typing import Dict, Tuple, Optional, Any

class TaskStatus(Enum):
    """Status enum for agent tasks"""
    CREATED = "created"    # Task is initialized but not yet started
    RUNNING = "running"    # Task is currently executing
    FINISHED = "finished"  # Task has completed successfully
    STOPPED = "stopped"    # Task was manually stopped
    PAUSED = "paused"      # Task execution is temporarily paused
    FAILED = "failed"      # Task encountered an error and could not complete