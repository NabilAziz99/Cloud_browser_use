# API Documentation

**Last updated:** [today's date will be filled in by user]

---

## Table of Contents
- [POST /api/v1/run-task](#post-apiv1run-task)
- [PUT /api/v1/stop-task/{task_id}](#put-apiv1stop-tasktask_id)
- [PUT /api/v1/pause-task/{task_id}](#put-apiv1pause-tasktask_id)
- [PUT /api/v1/resume-task/{task_id}](#put-apiv1resume-tasktask_id)
- [GET /api/v1/task/{task_id}/status](#get-apiv1tasktask_idstatus)
- [GET /api/v1/task/{task_id}](#get-apiv1tasktask_id)
- [GET /health](#get-health)

---

## POST /api/v1/run-task

Creates and starts a new automation task using the browser-use agent. Supports passing sensitive data securely.

### Headers
- `Authorization: Bearer <API_KEY>` (required)
- `Content-Type: application/json`

### Body (JSON)
| Field           | Type                | Required | Description                                                                 |
|-----------------|---------------------|----------|-----------------------------------------------------------------------------|
| `task`          | string              | Yes      | The task description for the agent.                                         |
| `model_provider`| string              | No       | LLM provider (default: `openai_chat`).                                      |
| `model_name`    | string              | No       | LLM model name (default: `gpt-4o`).                                         |
| `sensitive_data`| object (dict)       | No       | Dictionary of sensitive key-value pairs (e.g., usernames, passwords).        |

#### Example Request Body
```json
{
  "task": "go to x.com and login with x_name and x_password then write a post about the meaning of life",
  "model_provider": "openai_chat",
  "model_name": "gpt-4o",
  "sensitive_data": {
    "x_name": "magnus",
    "x_password": "12345678"
  }
}
```

#### Example CURL
```bash
curl -X POST http://localhost:8000/api/v1/run-task \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "go to x.com and login with x_name and x_password then write a post about the meaning of life",
    "model_provider": "openai_chat",
    "model_name": "gpt-4o",
    "sensitive_data": {
      "x_name": "magnus",
      "x_password": "12345678"
    }
  }'
```

### Success Response (HTTP 200)
```json
{
  "status": "success",
  "message": "Processing task: ...",
  "task_id": "<uuid>",
  "live_url": "<live_view_url or null>"
}
```

### Error States
- **401 Unauthorized:**
  ```json
  { "detail": "Invalid authentication credentials" }
  ```
- **500 Internal Server Error:**
  ```json
  { "detail": "Error processing task: <error message>" }
  ```
- **422 Unprocessable Entity:**
  ```json
  {
    "detail": [
      {
        "loc": ["body", "task"],
        "msg": "field required",
        "type": "value_error.missing"
      }
    ]
  }
  ```

#### Notes
- `sensitive_data` is optional. If provided, it should be a dictionary of key-value pairs (e.g., usernames, passwords) as described in [browser-use Sensitive Data Documentation](https://docs.browser-use.com/customize/sensitive-data).
- The agent will only see the keys as placeholders, not the actual values.

---

## PUT /api/v1/stop-task/{task_id}

Stops a running task.

### Path Parameter
- `task_id` (UUID): The ID of the task to stop.

#### Example CURL
```bash
curl -X PUT http://localhost:8000/api/v1/stop-task/<task_id> \
  -H "Authorization: Bearer <API_KEY>"
```

### Success Response (HTTP 200)
```json
{
  "status": "success",
  "message": "Task <task_id> stopped."
}
```

### Error States
- **404 Not Found:**
  ```json
  { "detail": "Task not found or already stopped." }
  ```
- **500 Internal Server Error:**
  ```json
  { "detail": "Error stopping task: <error message>" }
  ```

---

## PUT /api/v1/pause-task/{task_id}

Pauses a running task.

### Path Parameter
- `task_id` (UUID): The ID of the task to pause.

#### Example CURL
```bash
curl -X PUT http://localhost:8000/api/v1/pause-task/<task_id> \
  -H "Authorization: Bearer <API_KEY>"
```

### Success Response (HTTP 200)
```json
{
  "status": "success",
  "message": "Task <task_id> paused."
}
```

### Error States
- **404 Not Found:**
  ```json
  { "detail": "Task not found or already paused." }
  ```
- **500 Internal Server Error:**
  ```json
  { "detail": "Error pausing task: <error message>" }
  ```

---

## PUT /api/v1/resume-task/{task_id}

Resumes a paused task.

### Path Parameter
- `task_id` (UUID): The ID of the task to resume.

#### Example CURL
```bash
curl -X PUT http://localhost:8000/api/v1/resume-task/<task_id> \
  -H "Authorization: Bearer <API_KEY>"
```

### Success Response (HTTP 200)
```json
{
  "status": "success",
  "message": "Task <task_id> resumed."
}
```

### Error States
- **404 Not Found:**
  ```json
  { "detail": "Task not found or not paused." }
  ```
- **500 Internal Server Error:**
  ```json
  { "detail": "Error resuming task: <error message>" }
  ```

---

## GET /api/v1/task/{task_id}/status

Gets the current status of a task.

### Path Parameter
- `task_id` (UUID): The ID of the task to check.

#### Example CURL
```bash
curl -X GET http://localhost:8000/api/v1/task/<task_id>/status \
  -H "Authorization: Bearer <API_KEY>"
```

### Success Response (HTTP 200)
Returns a string status:
```json
"running" // or "created", "finished", "stopped", "paused", "failed"
```

### Error States
- **404 Not Found:**
  ```json
  { "detail": "Task <task_id> not found." }
  ```
- **500 Internal Server Error:**
  ```json
  { "detail": "Error getting task status: <error message>" }
  ```

---

## GET /api/v1/task/{task_id}

Gets comprehensive information about a task, including its current status, steps completed, output (if finished), and other metadata.

### Path Parameter
- `task_id` (UUID): The ID of the task to get details for.

#### Example CURL
```bash
curl -X GET http://localhost:8000/api/v1/task/<task_id> \
  -H "Authorization: Bearer <API_KEY>"
```

### Success Response (HTTP 200)
```json
{
  "id": "<task_id>",
  "task": "...",
  "output": "...",
  "status": "...",
  "created_at": "...",
  "finished_at": null,
  "steps": [
    {
      "id": "<step-uuid>",
      "step": 1,
      "evaluation_previous_goal": "...",
      "next_goal": "..."
    }
  ],
  "live_url": "<live_url>",
  "browser_data": null
}
```

### Error States
- **404 Not Found:**
  ```json
  { "detail": "Task <task_id> not found." }
  ```
- **500 Internal Server Error:**
  ```json
  { "detail": "Error getting task details: <error message>" }
  ```

---

## GET /health

Checks if the API is healthy.

#### Example CURL
```bash
curl -X GET http://localhost:8000/health
```

### Success Response (HTTP 200)
```json
{
  "status": "healthy"
}
``` 