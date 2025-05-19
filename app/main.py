from fastapi import FastAPI, Depends, HTTPException, Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import uvicorn
import os
import uuid
import logging
from typing import Dict, Optional, Any
import asyncio
from dotenv import load_dotenv

from app.services.browser.browser_agent import create_browser_agent
from app.services.task_manager import TaskManager, TaskStatus

# Load environment variables
load_dotenv()

# Get API key from environment
API_KEY = os.getenv("API_KEY", "default_insecure_key")

app = FastAPI()
security = HTTPBearer()


class FeedbackRequest(BaseModel):
    feedback: str

# Define our TaskRequest model
class TaskRequest(BaseModel):
    task: str
    model_provider: str = "openai_chat"
    model_name: str = "gpt-4o"
    sensitive_data: Optional[Dict[str, Any]] = None


# Verify token function
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    logging.info(f"Received token: {credentials.credentials}")
    logging.info(f"Expected token: {API_KEY}")
    logging.info(f"Match? {credentials.credentials == API_KEY}")

    if credentials.credentials != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return credentials.credentials

# Create a new task
@app.post("/api/v1/run-task")
async def run_task(request: TaskRequest, token: str = Depends(verify_token)):
    """
    Create and start a new automation task.
    """
    try:
        task_id, live_url = await TaskManager.create_task(
            task=request.task,
            model_provider=request.model_provider,
            model_name=request.model_name,
            sensitive_data=request.sensitive_data
        )

        return {
            "status": "success",
            "message": f"Processing task: {request.task}",
            "task_id": str(task_id),
            "live_url": live_url
        }
    except Exception as e:
        logging.error(f"Error processing task: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing task: {str(e)}")


# Stop a task - updated to use path parameter
@app.put("/api/v1/stop-task/{task_id}")
async def stop_agent(
        task_id: uuid.UUID = Path(..., description="The UUID of the task to stop"),
        token: str = Depends(verify_token)
):
    """
    Stop a running task.
    """
    try:
        if await TaskManager.stop_task(task_id):
            return {"status": "success", "message": f"Task {task_id} stopped."}
        else:
            raise HTTPException(status_code=404, detail="Task not found or already stopped.")
    except Exception as e:
        logging.error(f"Error stopping task: {e}")
        raise HTTPException(status_code=500, detail=f"Error stopping task: {str(e)}")


# Pause a task - updated to use path parameter
@app.put("/api/v1/pause-task/{task_id}")
async def pause_agent(
        task_id: uuid.UUID = Path(..., description="The UUID of the task to pause"),
        token: str = Depends(verify_token)
):
    """
    Pause a running task.
    """
    try:
        if await TaskManager.pause_task(task_id):
            return {"status": "success", "message": f"Task {task_id} paused."}
        else:
            raise HTTPException(status_code=404, detail="Task not found or already paused.")
    except Exception as e:
        logging.error(f"Error pausing task: {e}")
        raise HTTPException(status_code=500, detail=f"Error pausing task: {str(e)}")

    # Resume a task - updated to use path parameter


@app.put("/api/v1/resume-task/{task_id}")
async def resume_agent(
        task_id: uuid.UUID = Path(..., description="The UUID of the task to resume"),
        token: str = Depends(verify_token)
):
    """
    Resume a paused task.
    """
    try:
        if await TaskManager.resume_task(task_id):
            return {"status": "success", "message": f"Task {task_id} resumed."}
        else:
            raise HTTPException(status_code=404, detail="Task not found or not paused.")
    except Exception as e:
        logging.error(f"Error resuming task: {e}")
        raise HTTPException(status_code=500, detail=f"Error resuming task: {str(e)}")


# Add these endpoints to app/main.py

@app.get("/api/v1/task/{task_id}/status")
async def get_task_status_only(
        task_id: uuid.UUID = Path(..., description="The UUID of the task to check"),
        token: str = Depends(verify_token)
):
    """
    Get just the current status of a task.

    Returns a string representing the task status:
    - created: Task is initialized but not yet started
    - running: Task is currently executing
    - finished: Task has completed successfully
    - stopped: Task was manually stopped
    - paused: Task execution is temporarily paused
    - failed: Task encountered an error and could not complete
    """
    try:
        status = await TaskManager.get_task_status(task_id)
        return status
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found.")
    except Exception as e:
        logging.error(f"Error getting task status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting task status: {str(e)}")


@app.get("/api/v1/task/{task_id}")
async def get_task_details(
        task_id: uuid.UUID = Path(..., description="The UUID of the task to get details for"),
        token: str = Depends(verify_token)
):
    """
    Get comprehensive information about a task, including its current status,
    steps completed, output (if finished), and other metadata.
    """
    try:
        details = await TaskManager.get_task_details(task_id)
        return details
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found.")
    except Exception as e:
        logging.error(f"Error getting task details: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting task details: {str(e)}")
    
    
    

@app.post("/api/v1/task/{task_id}/human-feedback")
async def provide_human_feedback(
    task_id: uuid.UUID,
    feedback_request: FeedbackRequest,
    token: str = Depends(verify_token)
):
    """
    Provide human feedback to a paused agent and resume it.
    
    When an agent encounters a situation requiring human input,
    it pauses and waits for feedback. This endpoint allows providing
    that feedback and automatically resumes the agent.
    """
    try:
        # First add the feedback (synchronous operation)
        TaskManager.add_human_feedback(task_id, feedback_request.feedback)
        
        # Then resume the task (asynchronous operation)
        success = await TaskManager.resume_task(task_id)
        
        if not success:
            raise HTTPException(
                status_code=400, 
                detail=f"Could not resume task {task_id}. Feedback was recorded but task wasn't resumed."
            )
        
        return {
            "status": "success",
            "message": f"Feedback provided and agent resumed for task {task_id}",
            "task_id": str(task_id)
        }
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Error providing feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Error providing feedback: {str(e)}")

@app.get("/api/v1/task/{task_id}/pending-request")
async def get_pending_human_input_request(
    task_id: uuid.UUID,
    token: str = Depends(verify_token)
):
    """
    Get details about any pending human input request for a task.
    
    Returns information about what the agent is asking for,
    or null if there is no pending request.
    """
    from app.services.browser.controller_actions import pending_requests
    
    try:
        # First check if task exists
        if task_id not in TaskManager._running_agents:
            raise KeyError(f"Task {task_id} not found")
            
        # Then check if there's a pending request
        request_info = pending_requests.get(task_id)
        
        if not request_info:
            return {
                "has_pending_request": False,
                "request": None
            }
            
        return {
            "has_pending_request": True,
            "request": request_info
        }
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found.")
    except Exception as e:
        logging.error(f"Error getting pending request: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting pending request: {str(e)}")
    
    
    
    
    
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    print("--- Starting FastAPI server using Uvicorn ---")
    print(
        f"API Key loaded (check .env): {'*' * (len(API_KEY) - 4)}{API_KEY[-4:]}" if API_KEY != "default_insecure_key" else "Default Key")
    print("Access API Docs at: http://127.0.0.1:8000/docs")
    uvicorn.run(
        "app.main:app",  # Corresponds to: file_name:app_instance_name
        host="127.0.0.1",  # Listen on localhost
        port=8000,  # Standard port
        reload=True  # Enable auto-reload for development
    )