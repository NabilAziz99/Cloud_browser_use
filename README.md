# Browser Agent with Human-in-the-Loop

A sophisticated browser automation system that combines AI-powered web navigation with human assistance when needed. The system autonomously navigates web interfaces, detects task completion blockers, and seamlessly escalates to human operators for CAPTCHAs, authentication flows, or ambiguous requirements.

## 🌟 Key Features

- **Autonomous Web Navigation**: AI agents navigate complex web interfaces using natural language instructions
- **Intelligent Blocker Detection**: Automatically detects CAPTCHAs, authentication requirements, and form completion needs
- **Human-in-the-Loop**: Seamless escalation to human operators when automated navigation hits obstacles
- **Live Browser Sessions**: Real-time browser viewing through Anchor Browser integration
- **Adaptive Decision Making**: Agents evaluate task progress and determine when human intervention is needed
- **Pause/Resume Capabilities**: Maintains full context across human interventions for multi-step workflows
- **Slack Integration**: Receive notifications and provide feedback directly through Slack
- **Task Lifecycle Management**: Complete CRUD operations for managing automation tasks

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Slack Bot     │◄──►│   FastAPI API    │◄──►│  Browser Agent  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                         │
                                ▼                         ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  Task Manager    │    │ Anchor Browser  │
                       └──────────────────┘    └─────────────────┘
                                │                         │
                                ▼                         ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │ Agent Registry   │    │  Live Session   │
                       └──────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key
- Anchor Browser API key (optional, for remote browser sessions)
- Slack workspace and app (for Slack integration)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd browser-agent
   ```

2. **Install dependencies**
   ```bash
   pip install fastapi uvicorn browser-use langchain-openai python-dotenv httpx
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   # API Security
   API_KEY=your_secure_api_key_here
   
   # OpenAI Configuration
   OPENAI_API_KEY=your_openai_api_key_here
   
   # Anchor Browser (Optional - for remote browser sessions)
   ANCHOR_API_KEY=your_anchor_browser_api_key
   
   # Browser Configuration
   BROWSER_USE_HEADLESS=false
   CONTAINER=false
   
   # Slack Integration (if using)
   SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
   SLACK_SIGNING_SECRET=your_slack_signing_secret
   ```

## 🎯 Quick Start

### 1. Start the API Server

```bash
python -m app.main
```

The server will start on `http://127.0.0.1:8000`

Access the interactive API documentation at: `http://127.0.0.1:8000/docs`

### 2. Create Your First Task

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/run-task" \
  -H "Authorization: Bearer your_secure_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Go to amazon.com and search for wireless headphones",
    "model_provider": "openai_chat",
    "model_name": "gpt-4o"
  }'
```

### 3. Monitor Task Progress

```bash
# Get task status
curl -X GET "http://127.0.0.1:8000/api/v1/task/{task_id}/status" \
  -H "Authorization: Bearer your_secure_api_key_here"

# Get detailed task information
curl -X GET "http://127.0.0.1:8000/api/v1/task/{task_id}" \
  -H "Authorization: Bearer your_secure_api_key_here"
```

## 🤖 Human-in-the-Loop Workflow

### How It Works

1. **Agent Starts Task**: The browser agent begins executing the given task
2. **Obstacle Detection**: When the agent encounters a blocker (CAPTCHA, form field, etc.), it automatically pauses
3. **Human Notification**: The system notifies the human operator via Slack or API
4. **Live Session Access**: Human can view and interact with the live browser session
5. **Feedback Provision**: Human provides necessary input or completes the blocking step
6. **Automatic Resume**: Agent automatically resumes with the human feedback incorporated

### Example Scenario

```mermaid
sequenceDiagram
    participant Agent
    participant API
    participant Human
    participant Browser
    
    Agent->>Browser: Navigate to login page
    Agent->>Browser: Detect CAPTCHA
    Agent->>API: Pause task & request human help
    API->>Human: Send Slack notification with live URL
    Human->>Browser: Solve CAPTCHA via live session
    Human->>API: Submit "CAPTCHA solved" feedback
    API->>Agent: Resume with feedback
    Agent->>Browser: Continue with login flow
```

## 🔧 API Endpoints

### Task Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/run-task` | Create and start a new automation task |
| GET | `/api/v1/task/{task_id}` | Get comprehensive task details |
| GET | `/api/v1/task/{task_id}/status` | Get current task status |
| PUT | `/api/v1/pause-task/{task_id}` | Pause a running task |
| PUT | `/api/v1/resume-task/{task_id}` | Resume a paused task |
| PUT | `/api/v1/stop-task/{task_id}` | Stop a running task |

### Human Interaction

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/task/{task_id}/human-feedback` | Provide human feedback to resume task |
| GET | `/api/v1/task/{task_id}/pending-request` | Check for pending human input requests |

## 🎮 Controller Actions

The system includes several built-in controller actions that agents can trigger:

- **`done`**: Mark task as completed
- **`get_credentials`**: Request login credentials for a website
- **`get_form_data`**: Request form field values from human
- **`ask_human`**: Request help with CAPTCHAs or complex interactions
- **`human_handover`**: Transfer full control to human operator

## 💬 Slack Integration

### Setup

1. Create a Slack app in your workspace
2. Add the bot token and signing secret to your `.env` file
3. Configure your Slack bot to send notifications when agents need help

### Example Slack Message

```
🤖 Browser Agent Needs Help!

Task ID: 123e4567-e89b-12d3-a456-426614174000
Issue: CAPTCHA Challenge detected

What the agent is trying to do:
"Log into the customer portal to retrieve account information"

🌐 Live Browser: https://live.anchorbrowser.io/session/abc123

Reply with your feedback to resume the agent.
```

## 🎯 Example Use Cases

### 1. E-commerce Research
```json
{
  "task": "Go to shopify.com, create a free trial account, and explore the pricing plans",
  "model_provider": "openai_chat",
  "model_name": "gpt-4o"
}
```

### 2. Lead Generation
```json
{
  "task": "Search LinkedIn for AI startup founders in San Francisco and collect their contact information",
  "model_provider": "openai_chat",
  "model_name": "gpt-4o"
}
```

### 3. Data Entry
```json
{
  "task": "Fill out the contact form on example.com with the provided company information",
  "model_provider": "openai_chat",
  "model_name": "gpt-4o",
  "sensitive_data": {
    "company_name": "Acme Corp",
    "email": "contact@acme.com",
    "phone": "+1-555-0123"
  }
}
```

## 🔍 Task Status States

- **`created`**: Task is initialized but not yet started
- **`running`**: Task is currently executing
- **`paused`**: Task is waiting for human input
- **`finished`**: Task completed successfully
- **`stopped`**: Task was manually stopped
- **`failed`**: Task encountered an error

## 🛠️ Configuration

### Browser Configuration

```python
# Local browser (for development)
BROWSER_USE_HEADLESS=false
CONTAINER=false

# Container environment (for production)
BROWSER_USE_HEADLESS=true
CONTAINER=true
```

### Model Configuration

The system supports multiple LLM providers through the factory pattern:

```python
# Available models
"openai_chat" -> ChatOpenAI
# Add more providers by extending LLMFactory
```

## 📊 Monitoring and Debugging

### Logs

The system provides comprehensive logging:

```bash
# View real-time logs
tail -f app.log

# Filter for specific task
grep "Task ID: 123e4567" app.log
```

### Live Browser Sessions

When using Anchor Browser, you get:
- Real-time browser viewing
- Ability to interact during paused states
- Session recordings for debugging

## 🚨 Troubleshooting

### Common Issues

1. **Agent gets stuck**: Check if there's a pending human input request
2. **Browser crashes**: Verify browser arguments for your environment
3. **API authentication fails**: Ensure API_KEY is correctly set in `.env`
4. **Anchor Browser issues**: Verify ANCHOR_API_KEY and check service status

### Debug Mode

Enable verbose logging:

```python
logging.basicConfig(level=logging.DEBUG)
```

## 🔐 Security Considerations

- API authentication required for all endpoints
- Sensitive data handling for credentials and form data
- Browser session isolation
- Secure token management for Slack integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

[Add your license information here]

## 🆘 Support

For issues and questions:
- Create an issue in the repository
- Contact the development team via Slack
- Check the API documentation at `/docs`

---

**Built with ❤️ for seamless human-AI collaboration in web automation**
