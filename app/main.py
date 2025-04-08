from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import uvicorn
from app.services.browser.browser_agent import execute_task # <-- Corrected import
import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
API_KEY = os.getenv("API_KEY", "default_insecure_key")


app = FastAPI()
security = HTTPBearer()

# Define our TaskRequest model
class TaskRequest(BaseModel):
    task: str
    model_provider: str
    model_name: str

# Verify token function
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return credentials.credentials

# Updated route function
@app.post("/api/v1/run-task")
async def run_task(request: TaskRequest, token: str = Depends(verify_token)):
    try:
        await execute_task(
            task=request.task,
            model_provider=request.model_provider,
            model_name=request.model_name
        )

        return {
            "status": "success",
            "message": f"Processing task: {request.task}",
        }
    except Exception as e:
        # Log the exception for debugging
        print(f"Error processing task: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing task: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    print("--- Starting FastAPI server using Uvicorn ---")
    print(f"API Key loaded (check .env): {'*' * (len(API_KEY) - 4)}{API_KEY[-4:]}" if API_KEY != "default_insecure_key" else "Default Key")
    print("Access API Docs at: http://127.0.0.1:8000/docs")
    uvicorn.run(
        "app.main:app",       # Corresponds to: file_name:app_instance_name
        host="127.0.0.1", # Listen on localhost
        port=8000,        # Standard port
        reload=True       # Enable auto-reload for development (watches for file changes)
    )

