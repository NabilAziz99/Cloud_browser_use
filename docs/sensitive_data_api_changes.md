# Sensitive Data API Changes

**Last updated:** [today's date will be filled in by user]

## Overview

These changes add support for securely passing sensitive data (such as usernames and passwords) to the agent via the API, in accordance with the [browser-use documentation](https://docs.browser-use.com/customize/sensitive-data).

## Changes Made

- **API Model (`main.py`)**: The `TaskRequest` model now includes an optional `sensitive_data` field (dictionary).
- **API Endpoint (`main.py`)**: The `/api/v1/run-task` endpoint accepts and forwards `sensitive_data` to the backend.
- **Task Manager (`task_manager.py`)**: `TaskManager.create_task` now accepts and forwards `sensitive_data`.
- **Browser Agent (`browser_agent.py`)**: `create_browser_agent` now accepts and passes `sensitive_data` to the `Agent` constructor.

## API Usage Example

**Request Body:**
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

- The agent will see only the keys (e.g., `x_name`, `x_password`) as placeholders, not the actual values.
- The sensitive values are only used at execution time, not exposed to the LLM.

## Security Note
- Avoid logging the contents of `sensitive_data`.
- The model will not see the actual sensitive values, but vision models may still see them if visible on the page ([see docs](https://docs.browser-use.com/customize/sensitive-data)).

---

**For more details, see:** [browser-use Sensitive Data Documentation](https://docs.browser-use.com/customize/sensitive-data) 