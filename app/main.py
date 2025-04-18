from fastapi import FastAPI, Depends, HTTPException, Path, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware  # We'll try the official middleware again
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import os
import uuid
import logging
from typing import Dict
import asyncio
from dotenv import load_dotenv

from app.services.browser.browser_agent import create_browser_agent
from app.services.task_manager import TaskManager, TaskStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get API key from environment
API_KEY = os.getenv("API_KEY", "default_insecure_key")

# Create the app
app = FastAPI()

# Add CORS middleware - try official version first
try:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("Added FastAPI CORS middleware")
except Exception as e:
    logger.error(f"Failed to add FastAPI CORS middleware: {e}")


    # If the official middleware fails, we'll use our custom one

    @app.middleware("http")
    async def custom_cors_middleware(request: Request, call_next):
        # Handle preflight OPTIONS requests specially
        if request.method == "OPTIONS":
            response = JSONResponse(content={})
        else:
            response = await call_next(request)

        # Add CORS headers to all responses
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Accept"

        logger.info(f"Added CORS headers with custom middleware to {request.method} request")
        return response


    logger.info("Added custom CORS middleware as fallback")

# Security
security = HTTPBearer()


# Define our TaskRequest model
class TaskRequest(BaseModel):
    task: str
    model_provider: str = "openai_chat"
    model_name: str = "gpt-4o"


# Add an OPTIONS handler for all paths to handle preflight requests
@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    """Handle OPTIONS requests for CORS preflight"""
    return {}


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
            model_name=request.model_name
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


# Stop a task - support both PUT and POST
@app.put("/api/v1/stop-task/{task_id}")
@app.post("/api/v1/stop-task/{task_id}")
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


# Pause a task - support both PUT and POST
@app.put("/api/v1/pause-task/{task_id}")
@app.post("/api/v1/pause-task/{task_id}")
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


# Resume a task - support both PUT and POST
@app.put("/api/v1/resume-task/{task_id}")
@app.post("/api/v1/resume-task/{task_id}")
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


# Get task status
@app.get("/api/v1/task/{task_id}/status")
async def get_task_status_only(
        task_id: uuid.UUID = Path(..., description="The UUID of the task to check"),
        token: str = Depends(verify_token)
):
    """
    Get just the current status of a task.
    """
    try:
        status = await TaskManager.get_task_status(task_id)
        return status
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found.")
    except Exception as e:
        logging.error(f"Error getting task status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting task status: {str(e)}")


# Get task details
@app.get("/api/v1/task/{task_id}")
async def get_task_details(
        task_id: uuid.UUID = Path(..., description="The UUID of the task to get details for"),
        token: str = Depends(verify_token)
):
    """
    Get comprehensive information about a task.
    """
    try:
        details = await TaskManager.get_task_details(task_id)
        return details
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found.")
    except Exception as e:
        logging.error(f"Error getting task details: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting task details: {str(e)}")


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print("--- Starting FastAPI server using Uvicorn ---")
    print(
        f"API Key loaded (check .env): {'*' * (len(API_KEY) - 4)}{API_KEY[-4:]}" if API_KEY != "default_insecure_key" else "Default Key")
    print(f"Server running on port: {port}")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",  # Using 0.0.0.0 instead of 127.0.0.1 for broader access
        port=port,
        reload=False  # Disable reload in production
    )