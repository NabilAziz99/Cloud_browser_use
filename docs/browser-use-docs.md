└── docs
    ├── README.md
    ├── cloud
        ├── implementation.mdx
        └── quickstart.mdx
    ├── customize
        ├── agent-settings.mdx
        ├── browser-settings.mdx
        ├── custom-functions.mdx
        ├── hooks.mdx
        ├── output-format.mdx
        ├── real-browser.mdx
        ├── sensitive-data.mdx
        ├── supported-models.mdx
        └── system-prompt.mdx
    ├── development.mdx
    ├── development
        ├── contribution-guide.mdx
        ├── evaluations.mdx
        ├── local-setup.mdx
        ├── n8n-integration.mdx
        ├── observability.mdx
        ├── roadmap.mdx
        └── telemetry.mdx
    ├── favicon.svg
    ├── images
        ├── browser-use.png
        ├── checks-passed.png
        └── laminar.png
    ├── introduction.mdx
    ├── logo
        ├── dark.svg
        └── light.svg
    ├── mint.json
    └── quickstart.mdx


/docs/README.md:
--------------------------------------------------------------------------------
 1 | # Docs
 2 | 
 3 | The official documentation for Browser Use. The docs are published to [Browser Use Docs](https://docs.browser-use.com).
 4 | 
 5 | ### Development
 6 | 
 7 | Install the [Mintlify CLI](https://www.npmjs.com/package/mintlify) to preview the documentation changes locally. To install, use the following command
 8 | 
 9 | ```
10 | npm i -g mintlify
11 | ```
12 | 
13 | Run the following command at the root of your documentation (where mint.json is)
14 | 
15 | ```
16 | mintlify dev
17 | ```
18 | 


--------------------------------------------------------------------------------
/docs/cloud/implementation.mdx:
--------------------------------------------------------------------------------
  1 | ---
  2 | title: "Implementing the API"
  3 | description: "Learn how to implement the Browser Use API in Python"
  4 | icon: "code"
  5 | ---
  6 | 
  7 | This guide shows how to implement common API patterns using Python. We'll create a complete example that creates and monitors a browser automation task.
  8 | 
  9 | ## Basic Implementation
 10 | 
 11 | For all settings see [Run Task](cloud/api-v10/run-task).
 12 | 
 13 | Here's a simple implementation using Python's `requests` library to stream the task steps:
 14 | 
 15 | ```python
 16 | import json
 17 | import time
 18 | 
 19 | import requests
 20 | 
 21 | API_KEY = 'your_api_key_here'
 22 | BASE_URL = 'https://api.browser-use.com/api/v1'
 23 | HEADERS = {'Authorization': f'Bearer {API_KEY}'}
 24 | 
 25 | 
 26 | def create_task(instructions: str):
 27 | 	"""Create a new browser automation task"""
 28 | 	response = requests.post(f'{BASE_URL}/run-task', headers=HEADERS, json={'task': instructions})
 29 | 	return response.json()['id']
 30 | 
 31 | 
 32 | def get_task_status(task_id: str):
 33 | 	"""Get current task status"""
 34 | 	response = requests.get(f'{BASE_URL}/task/{task_id}/status', headers=HEADERS)
 35 | 	return response.json()
 36 | 
 37 | 
 38 | def get_task_details(task_id: str):
 39 | 	"""Get full task details including output"""
 40 | 	response = requests.get(f'{BASE_URL}/task/{task_id}', headers=HEADERS)
 41 | 	return response.json()
 42 | 
 43 | 
 44 | def wait_for_completion(task_id: str, poll_interval: int = 2):
 45 | 	"""Poll task status until completion"""
 46 | 	count = 0
 47 | 	unique_steps = []
 48 | 	while True:
 49 | 		details = get_task_details(task_id)
 50 | 		new_steps = details['steps']
 51 | 		# use only the new steps that are not in unique_steps.
 52 | 		if new_steps != unique_steps:
 53 | 			for step in new_steps:
 54 | 				if step not in unique_steps:
 55 | 					print(json.dumps(step, indent=4))
 56 | 			unique_steps = new_steps
 57 | 		count += 1
 58 | 		status = details['status']
 59 | 
 60 | 		if status in ['finished', 'failed', 'stopped']:
 61 | 			return details
 62 | 		time.sleep(poll_interval)
 63 | 
 64 | 
 65 | def main():
 66 | 	task_id = create_task('Open https://www.google.com and search for openai')
 67 | 	print(f'Task created with ID: {task_id}')
 68 | 	task_details = wait_for_completion(task_id)
 69 | 	print(f"Final output: {task_details['output']}")
 70 | 
 71 | 
 72 | if __name__ == '__main__':
 73 | 	main()
 74 | 
 75 | ```
 76 | 
 77 | ## Task Control Example
 78 | 
 79 | Here's how to implement task control with pause/resume functionality:
 80 | 
 81 | ```python
 82 | def control_task():
 83 |     # Create a new task
 84 |     task_id = create_task("Go to google.com and search for Browser Use")
 85 | 
 86 |     # Wait for 5 seconds
 87 |     time.sleep(5)
 88 | 
 89 |     # Pause the task
 90 |     requests.put(f"{BASE_URL}/pause-task?task_id={task_id}", headers=HEADERS)
 91 |     print("Task paused! Check the live preview.")
 92 | 
 93 |     # Wait for user input
 94 |     input("Press Enter to resume...")
 95 | 
 96 |     # Resume the task
 97 |     requests.put(f"{BASE_URL}/resume-task?task_id={task_id}", headers=HEADERS)
 98 | 
 99 |     # Wait for completion
100 |     result = wait_for_completion(task_id)
101 |     print(f"Task completed with output: {result['output']}")
102 | ```
103 | 
104 | ## Structured Output Example
105 | 
106 | Here's how to implement a task with structured JSON output:
107 | 
108 | ```python
109 | import json
110 | import os
111 | import time
112 | import requests
113 | from pydantic import BaseModel
114 | from typing import List
115 | 
116 | 
117 | API_KEY = os.getenv("API_KEY")
118 | BASE_URL = 'https://api.browser-use.com/api/v1'
119 | HEADERS = {
120 |     "Authorization": f"Bearer {API_KEY}",
121 |     "Content-Type": "application/json"
122 | }
123 | 
124 | 
125 | # Define output schema using Pydantic
126 | class SocialMediaCompany(BaseModel):
127 |     name: str
128 |     market_cap: float
129 |     headquarters: str
130 |     founded_year: int
131 | 
132 | 
133 | class SocialMediaCompanies(BaseModel):
134 |     companies: List[SocialMediaCompany]
135 | 
136 | 
137 | def create_structured_task(instructions: str, schema: dict):
138 |     """Create a task that expects structured output"""
139 |     payload = {
140 |         "task": instructions,
141 |         "structured_output_json": json.dumps(schema)
142 |     }
143 |     response = requests.post(f"{BASE_URL}/run-task", headers=HEADERS, json=payload)
144 |     response.raise_for_status()
145 |     return response.json()["id"]
146 | 
147 | 
148 | def wait_for_task_completion(task_id: str, poll_interval: int = 5):
149 |     """Poll task status until it completes"""
150 |     while True:
151 |         response = requests.get(f"{BASE_URL}/task/{task_id}/status", headers=HEADERS)
152 |         response.raise_for_status()
153 |         status = response.json()
154 |         if status == "finished":
155 |             break
156 |         elif status in ["failed", "stopped"]:
157 |             raise RuntimeError(f"Task {task_id} ended with status: {status}")
158 |         print("Waiting for task to finish...")
159 |         time.sleep(poll_interval)
160 | 
161 | 
162 | def fetch_task_output(task_id: str):
163 |     """Retrieve the final task result"""
164 |     response = requests.get(f"{BASE_URL}/task/{task_id}", headers=HEADERS)
165 |     response.raise_for_status()
166 |     return response.json()["output"]
167 | 
168 | 
169 | def main():
170 |     schema = SocialMediaCompanies.model_json_schema()
171 |     task_id = create_structured_task(
172 |         "Get me the top social media companies by market cap",
173 |         schema
174 |     )
175 |     print(f"Task created with ID: {task_id}")
176 | 
177 |     wait_for_task_completion(task_id)
178 |     print("Task completed!")
179 | 
180 |     output = fetch_task_output(task_id)
181 |     print("Raw output:", output)
182 | 
183 |     try:
184 |         parsed = SocialMediaCompanies.model_validate_json(output)
185 |         print("Parsed output:")
186 |         print(parsed)
187 |     except Exception as e:
188 |         print(f"Failed to parse structured output: {e}")
189 | 
190 | 
191 | if __name__ == "__main__":
192 |     main()
193 | ```
194 | 
195 | <Note>
196 |   Remember to handle your API key securely and implement proper error handling
197 |   in production code.
198 | </Note>
199 | 


--------------------------------------------------------------------------------
/docs/cloud/quickstart.mdx:
--------------------------------------------------------------------------------
  1 | ---
  2 | title: "Quickstart"
  3 | description: "Learn how to get started with the Browser Use Cloud API"
  4 | icon: "cloud"
  5 | ---
  6 | 
  7 | The Browser Use Cloud API lets you create and manage browser automation agents programmatically. Each agent can execute tasks and provide real-time feedback through a live preview URL.
  8 | 
  9 | ## Prerequisites
 10 | 
 11 | <Note>
 12 |   You need an active subscription and an API key from
 13 |   [cloud.browser-use.com/billing](https://cloud.browser-use.com/billing)
 14 | </Note>
 15 | 
 16 | ## Pricing
 17 | 
 18 | The Browser Use Cloud API is priced at <b>$0.05 per step</b> that the agent executes.
 19 | 
 20 | <Note>
 21 |   Since Browser Use can execute multiple steps at the same time, the price for
 22 |   filling out forms is much lower than other services.
 23 | </Note>
 24 | 
 25 | ## Creating Your First Agent
 26 | 
 27 | Create a new browser automation task by providing instructions in natural language:
 28 | 
 29 | ```bash
 30 | curl -X POST https://api.browser-use.com/api/v1/run-task \
 31 |   -H "Authorization: Bearer your_api_key_here" \
 32 |   -H "Content-Type: application/json" \
 33 |   -d '{
 34 |     "task": "Go to google.com and search for Browser Use"
 35 |   }'
 36 | ```
 37 | 
 38 | The API returns a task ID that you can use to manage the task and check the live preview URL.
 39 | 
 40 | <Note>
 41 |   The task response includes a `live_url` that you can embed in an iframe to
 42 |   watch and control the agent in real-time.
 43 | </Note>
 44 | 
 45 | ## Managing Tasks
 46 | 
 47 | Control running tasks with these operations:
 48 | 
 49 | <AccordionGroup>
 50 |   <Accordion title="Pause/Resume Tasks">
 51 |     Temporarily pause task execution with [`/api/v1/pause-task`](/cloud/api-v1/pause-task) and resume with
 52 |     [`/api/v1/resume-task`](/cloud/api-v1/resume-task). Useful for manual inspection or intervention.
 53 |   </Accordion>
 54 | 
 55 |   <Accordion title="Stop Tasks">
 56 |     Permanently stop a task using [`/api/v1/stop-task`](/cloud/api-v1/stop-task). The task cannot be
 57 |     resumed after being stopped.
 58 |   </Accordion>
 59 | </AccordionGroup>
 60 | 
 61 | For detailed API documentation, see the tabs on the left, which include the full coverage of the API.
 62 | 
 63 | ## Building your own client (OpenAPI)
 64 | 
 65 | <Note>
 66 |   We recommend this only if you don't need control and only need to run simple
 67 |   tasks.
 68 | </Note>
 69 | 
 70 | The best way to build your own client is to use our [OpenAPI specification](http://api.browser-use.com/openapi.json) to generate a type-safe client library.
 71 | 
 72 | ### Python
 73 | 
 74 | Use [openapi-python-client](https://github.com/openapi-generators/openapi-python-client) to generate a modern Python client:
 75 | 
 76 | ```bash
 77 | # Install the generator
 78 | pipx install openapi-python-client --include-deps
 79 | 
 80 | # Generate the client
 81 | openapi-python-client generate --url http://api.browser-use.com/openapi.json
 82 | ```
 83 | 
 84 | This will create a Python package with full type hints, modern dataclasses, and async support.
 85 | 
 86 | ### TypeScript/JavaScript
 87 | 
 88 | For TypeScript projects, use [openapi-typescript](https://www.npmjs.com/package/openapi-typescript) to generate type definitions:
 89 | 
 90 | ```bash
 91 | # Install the generator
 92 | npm install -D openapi-typescript
 93 | 
 94 | # Generate the types
 95 | npx openapi-typescript http://api.browser-use.com/openapi.json -o browser-use-api.ts
 96 | ```
 97 | 
 98 | This will create TypeScript definitions you can use with your preferred HTTP client.
 99 | 
100 | <Note>
101 |   Need help? Contact our support team at support@browser-use.com or join our
102 |   [Discord community](https://link.browser-use.com/discord)
103 | </Note>
104 | 


--------------------------------------------------------------------------------
/docs/customize/agent-settings.mdx:
--------------------------------------------------------------------------------
  1 | ---
  2 | title: "Agent Settings"
  3 | description: "Learn how to configure the agent"
  4 | icon: "gear"
  5 | ---
  6 | 
  7 | ## Overview
  8 | 
  9 | The `Agent` class is the core component of Browser Use that handles browser automation. Here are the main configuration options you can use when initializing an agent.
 10 | 
 11 | ## Basic Settings
 12 | 
 13 | ```python
 14 | from browser_use import Agent
 15 | from langchain_openai import ChatOpenAI
 16 | 
 17 | agent = Agent(
 18 |     task="Search for latest news about AI",
 19 |     llm=ChatOpenAI(model="gpt-4o"),
 20 | )
 21 | ```
 22 | 
 23 | ### Required Parameters
 24 | 
 25 | - `task`: The instruction for the agent to execute
 26 | - `llm`: A LangChain chat model instance. See <a href="/customize/supported-models">LangChain Models</a> for supported models.
 27 | 
 28 | ## Agent Behavior
 29 | 
 30 | Control how the agent operates:
 31 | 
 32 | ```python
 33 | agent = Agent(
 34 |     task="your task",
 35 |     llm=llm,
 36 |     controller=custom_controller,  # For custom tool calling
 37 |     use_vision=True,              # Enable vision capabilities
 38 |     save_conversation_path="logs/conversation"  # Save chat logs
 39 | )
 40 | ```
 41 | 
 42 | ### Behavior Parameters
 43 | 
 44 | - `controller`: Registry of functions the agent can call. Defaults to base Controller. See <a href="/customize/custom-functions">Custom Functions</a> for details.
 45 | - `use_vision`: Enable/disable vision capabilities. Defaults to `True`.
 46 |   - When enabled, the model processes visual information from web pages
 47 |   - Disable to reduce costs or use models without vision support
 48 |   - For GPT-4o, image processing costs approximately 800-1000 tokens (~$0.002 USD) per image (but this depends on the defined screen size)
 49 | - `save_conversation_path`: Path to save the complete conversation history. Useful for debugging.
 50 | - `override_system_message`: Completely replace the default system prompt with a custom one.
 51 | - `extend_system_message`: Add additional instructions to the default system prompt.
 52 | 
 53 | <Note>
 54 |   Vision capabilities are recommended for better web interaction understanding,
 55 |   but can be disabled to reduce costs or when using models without vision
 56 |   support.
 57 | </Note>
 58 | 
 59 | ## (Reuse) Browser Configuration
 60 | 
 61 | You can configure how the agent interacts with the browser. To see more `Browser` options refer to the <a href="/customize/browser-settings">Browser Settings</a> documentation.
 62 | 
 63 | ### Reuse Existing Browser
 64 | 
 65 | `browser`: A Browser Use Browser instance. When provided, the agent will reuse this browser instance and automatically create new contexts for each `run()`.
 66 | 
 67 | ```python
 68 | from browser_use import Agent, Browser
 69 | from browser_use.browser.context import BrowserContext
 70 | 
 71 | # Reuse existing browser
 72 | browser = Browser()
 73 | agent = Agent(
 74 |     task=task1,
 75 |     llm=llm,
 76 |     browser=browser  # Browser instance will be reused
 77 | )
 78 | 
 79 | await agent.run()
 80 | 
 81 | # Manually close the browser
 82 | await browser.close()
 83 | ```
 84 | 
 85 | <Note>
 86 |   Remember: in this scenario the `Browser` will not be closed automatically.
 87 | </Note>
 88 | 
 89 | ### Reuse Existing Browser Context
 90 | 
 91 | `browser_context`: A Playwright browser context. Useful for maintaining persistent sessions. See <a href="/customize/persistent-browser">Persistent Browser</a> for more details.
 92 | 
 93 | ```python
 94 | from browser_use import Agent, Browser
 95 | from patchright.async_api import BrowserContext
 96 | 
 97 | # Use specific browser context (preferred method)
 98 | async with await browser.new_context() as context:
 99 |     agent = Agent(
100 |         task=task2,
101 |         llm=llm,
102 |         browser_context=context  # Use persistent context
103 |     )
104 | 
105 |     # Run the agent
106 |     await agent.run()
107 | 
108 |     # Pass the context to the next agent
109 |     next_agent = Agent(
110 |         task=task2,
111 |         llm=llm,
112 |         browser_context=context
113 |     )
114 | 
115 |     ...
116 | 
117 | await browser.close()
118 | ```
119 | 
120 | For more information about how browser context works, refer to the [Playwright
121 | documentation](https://playwright.dev/docs/api/class-browsercontext).
122 | 
123 | <Note>
124 |   You can reuse the same context for multiple agents. If you do nothing, the
125 |   browser will be automatically created and closed on `run()` completion.
126 | </Note>
127 | 
128 | ## Running the Agent
129 | 
130 | The agent is executed using the async `run()` method:
131 | 
132 | - `max_steps` (default: `100`)
133 |   Maximum number of steps the agent can take during execution. This prevents infinite loops and helps control execution time.
134 | 
135 | ## Agent History
136 | 
137 | The method returns an `AgentHistoryList` object containing the complete execution history. This history is invaluable for debugging, analysis, and creating reproducible scripts.
138 | 
139 | ```python
140 | # Example of accessing history
141 | history = await agent.run()
142 | 
143 | # Access (some) useful information
144 | history.urls()              # List of visited URLs
145 | history.screenshots()       # List of screenshot paths
146 | history.action_names()      # Names of executed actions
147 | history.extracted_content() # Content extracted during execution
148 | history.errors()           # Any errors that occurred
149 | history.model_actions()     # All actions with their parameters
150 | ```
151 | 
152 | The `AgentHistoryList` provides many helper methods to analyze the execution:
153 | 
154 | - `final_result()`: Get the final extracted content
155 | - `is_done()`: Check if the agent completed successfully
156 | - `has_errors()`: Check if any errors occurred
157 | - `model_thoughts()`: Get the agent's reasoning process
158 | - `action_results()`: Get results of all actions
159 | 
160 | <Note>
161 |   For a complete list of helper methods and detailed history analysis
162 |   capabilities, refer to the [AgentHistoryList source
163 |   code](https://github.com/browser-use/browser-use/blob/main/browser_use/agent/views.py#L111).
164 | </Note>
165 | 
166 | ## Run initial actions without LLM
167 | With [this example](https://github.com/browser-use/browser-use/blob/main/examples/features/initial_actions.py) you can run initial actions without the LLM.
168 | Specify the action as a dictionary where the key is the action name and the value is the action parameters. You can find all our actions in the [Controller](https://github.com/browser-use/browser-use/blob/main/browser_use/controller/service.py) source code.
169 | ```python
170 | 
171 | initial_actions = [
172 | 	{'open_tab': {'url': 'https://www.google.com'}},
173 | 	{'open_tab': {'url': 'https://en.wikipedia.org/wiki/Randomness'}},
174 | 	{'scroll_down': {'amount': 1000}},
175 | ]
176 | agent = Agent(
177 | 	task='What theories are displayed on the page?',
178 | 	initial_actions=initial_actions,
179 | 	llm=llm,
180 | )
181 | ```
182 | 
183 | ## Run with message context
184 | 
185 | You can configure the agent and provide a separate message to help the LLM understand the task better.
186 | 
187 | ```python
188 | from langchain_openai import ChatOpenAI
189 | 
190 | agent = Agent(
191 |     task="your task",
192 |     message_context="Additional information about the task",
193 |     llm = ChatOpenAI(model='gpt-4o')
194 | )
195 | ```
196 | 
197 | ## Run with planner model
198 | 
199 | You can configure the agent to use a separate planner model for high-level task planning:
200 | 
201 | ```python
202 | from langchain_openai import ChatOpenAI
203 | 
204 | # Initialize models
205 | llm = ChatOpenAI(model='gpt-4o')
206 | planner_llm = ChatOpenAI(model='o3-mini')
207 | 
208 | agent = Agent(
209 |     task="your task",
210 |     llm=llm,
211 |     planner_llm=planner_llm,           # Separate model for planning
212 |     use_vision_for_planner=False,      # Disable vision for planner
213 |     planner_interval=4                 # Plan every 4 steps
214 | )
215 | ```
216 | 
217 | ### Planner Parameters
218 | 
219 | - `planner_llm`: A LangChain chat model instance used for high-level task planning. Can be a smaller/cheaper model than the main LLM.
220 | - `use_vision_for_planner`: Enable/disable vision capabilities for the planner model. Defaults to `True`.
221 | - `planner_interval`: Number of steps between planning phases. Defaults to `1`.
222 | 
223 | Using a separate planner model can help:
224 | - Reduce costs by using a smaller model for high-level planning
225 | - Improve task decomposition and strategic thinking
226 | - Better handle complex, multi-step tasks
227 | 
228 | <Note>
229 |   The planner model is optional. If not specified, the agent will not use the planner model.
230 | </Note>
231 | 
232 | ### Optional Parameters
233 | 
234 | - `message_context`: Additional information about the task to help the LLM understand the task better.
235 | - `initial_actions`: List of initial actions to run before the main task.
236 | - `max_actions_per_step`: Maximum number of actions to run in a step. Defaults to `10`.
237 | - `max_failures`: Maximum number of failures before giving up. Defaults to `3`.
238 | - `retry_delay`: Time to wait between retries in seconds when rate limited. Defaults to `10`.
239 | - `generate_gif`: Enable/disable GIF generation. Defaults to `False`. Set to `True` or a string path to save the GIF.
240 | ## Memory Management
241 | 
242 | Browser Use includes a procedural memory system using [Mem0](https://mem0.ai) that automatically summarizes the agent's conversation history at regular intervals to optimize context window usage during long tasks.
243 | 
244 | ```python
245 | from browser_use.agent.memory import MemoryConfig
246 | 
247 | agent = Agent(
248 |     task="your task",
249 |     llm=llm,
250 |     enable_memory=True,
251 |     memory_config=MemoryConfig(
252 |         agent_id="my_custom_agent",
253 |         memory_interval=15
254 |     )
255 | )
256 | ```
257 | 
258 | ### Memory Parameters
259 | 
260 | - `enable_memory`: Enable/disable the procedural memory system. Defaults to `True`.
261 | - `memory_config`: A `MemoryConfig` Pydantic model instance (required). Dictionary format is not supported.
262 | 
263 | ### Using MemoryConfig
264 | 
265 | You must configure the memory system using the `MemoryConfig` Pydantic model for a type-safe approach:
266 | 
267 | ```python
268 | from browser_use.agent.memory import MemoryConfig
269 | 
270 | agent = Agent(
271 |     task=task_description,
272 |     llm=llm,
273 |     memory_config=MemoryConfig(
274 |         agent_id="my_agent",
275 |         memory_interval=15,
276 |         embedder_provider="openai",
277 |         embedder_model="text-embedding-3-large",
278 |         embedder_dims=1536,
279 |     )
280 | )
281 | ```
282 | 
283 | The `MemoryConfig` model provides these configuration options:
284 | 
285 | #### Memory Settings
286 | - `agent_id`: Unique identifier for the agent (default: `"browser_use_agent"`)
287 | - `memory_interval`: Number of steps between memory summarization (default: `10`)
288 | 
289 | #### Embedder Settings
290 | - `embedder_provider`: Provider for embeddings (`'openai'`, `'gemini'`, `'ollama'`, or `'huggingface'`)
291 | - `embedder_model`: Model name for the embedder
292 | - `embedder_dims`: Dimensions for the embeddings
293 | 
294 | #### Vector Store Settings
295 | - `vector_store_provider`: Provider for vector storage (currently only `'faiss'` is supported)
296 | - `vector_store_base_path`: Path for storing vector data (e.g. /tmp/mem0)
297 | 
298 | The model automatically sets appropriate defaults based on the LLM being used:
299 | - For `ChatOpenAI`: Uses OpenAI's `text-embedding-3-small` embeddings
300 | - For `ChatGoogleGenerativeAI`: Uses Gemini's `models/text-embedding-004` embeddings
301 | - For `ChatOllama`: Uses Ollama's `nomic-embed-text` embeddings
302 | - Default: Uses Hugging Face's `all-MiniLM-L6-v2` embeddings
303 | 
304 | <Note>
305 |   Always pass a properly constructed `MemoryConfig` object to the `memory_config` parameter. 
306 |   Dictionary-based configuration is no longer supported.
307 | </Note>
308 | 
309 | ### How Memory Works
310 | 
311 | When enabled, the agent periodically compresses its conversation history into concise summaries:
312 | 
313 | 1. Every `memory_interval` steps, the agent reviews its recent interactions
314 | 2. It creates a procedural memory summary using the same LLM as the agent
315 | 3. The original messages are replaced with the summary, reducing token usage
316 | 4. This process helps maintain important context while freeing up the context window
317 | 
318 | ### Disabling Memory
319 | 
320 | If you want to disable the memory system (for debugging or for shorter tasks), set `enable_memory` to `False`:
321 | 
322 | ```python
323 | agent = Agent(
324 |     task="your task",
325 |     llm=llm,
326 |     enable_memory=False
327 | )
328 | ```
329 | 
330 | <Note>
331 |   Disabling memory may be useful for debugging or short tasks, but for longer
332 |   tasks, it can lead to context window overflow as the conversation history
333 |   grows. The memory system helps maintain performance during extended sessions.
334 | </Note>
335 | 


--------------------------------------------------------------------------------
/docs/customize/browser-settings.mdx:
--------------------------------------------------------------------------------
  1 | ---
  2 | title: "Browser Settings"
  3 | description: "Configure browser behavior and context settings"
  4 | icon: "globe"
  5 | ---
  6 | 
  7 | Browser Use allows you to customize the browser's behavior through two main configuration classes: `BrowserConfig` and `BrowserContextConfig`. These settings control everything from headless mode to proxy settings and page load behavior.
  8 | 
  9 | <Note>
 10 |   We are currently working on improving how browser contexts are managed. The
 11 |   system will soon transition to a "1 agent, 1 browser, 1 context" model for
 12 |   better stability and developer experience.
 13 | </Note>
 14 | 
 15 | # Browser Configuration
 16 | 
 17 | The `BrowserConfig` class controls the core browser behavior and connection settings.
 18 | 
 19 | ```python
 20 | from browser_use import BrowserConfig
 21 | 
 22 | # Basic configuration
 23 | config = BrowserConfig(
 24 |     headless=False,
 25 |     disable_security=False
 26 | )
 27 | 
 28 | browser = Browser(config=config)
 29 | 
 30 | agent = Agent(
 31 |     browser=browser,
 32 |     # ...
 33 | )
 34 | ```
 35 | 
 36 | ## Core Settings
 37 | 
 38 | - **headless** (default: `False`)
 39 |   Runs the browser without a visible UI. Note that some websites may detect headless mode.
 40 | 
 41 | - **disable_security** (default: `False`)
 42 |   Disables browser security features. While this can fix certain functionality issues (like cross-site iFrames), it should be used cautiously, especially when visiting untrusted websites.
 43 | 
 44 | ### Additional Settings
 45 | 
 46 | - **extra_browser_args** (default: `[]`)
 47 |   Additional arguments are passed to the browser at launch. See the [full list of available arguments](https://github.com/browser-use/browser-use/blob/main/browser_use/browser/browser.py#L180).
 48 | 
 49 | - **proxy** (default: `None`)
 50 |   Standard Playwright proxy settings for using external proxy services.
 51 | 
 52 | - **new_context_config** (default: `BrowserContextConfig()`)
 53 |   Default settings for new browser contexts. See Context Configuration below.
 54 | 
 55 | <Note>
 56 |   For web scraping tasks on sites that restrict automated access, we recommend
 57 |   using external browser or proxy providers for better reliability.
 58 | </Note>
 59 | 
 60 | ## Alternative Initialization
 61 | 
 62 | These settings allow you to connect to external browser providers or use a local Chrome instance.
 63 | 
 64 | ### External Browser Provider (wss)
 65 | 
 66 | Connect to cloud-based browser services for enhanced reliability and proxy capabilities.
 67 | 
 68 | ```python
 69 | config = BrowserConfig(
 70 |     wss_url="wss://your-browser-provider.com/ws"
 71 | )
 72 | ```
 73 | 
 74 | - **wss_url** (default: `None`)
 75 |   WebSocket URL for connecting to external browser providers (e.g., [anchorbrowser.io](https://anchorbrowser.io), steel.dev, browserbase.com, browserless.io, [TestingBot](https://testingbot.com/support/ai/integrations/browser-use)).
 76 | 
 77 | <Note>
 78 |   This overrides local browser settings and uses the provider's configuration.
 79 |   Refer to their documentation for settings.
 80 | </Note>
 81 | 
 82 | ### External Browser Provider (cdp)
 83 | 
 84 | Connect to cloud or local Chrome instances using Chrome DevTools Protocol (CDP) for use with tools like `headless-shell` or `browserless`.
 85 | 
 86 | ```python
 87 | config = BrowserConfig(
 88 |     cdp_url="http://localhost:9222"
 89 | )
 90 | ```
 91 | 
 92 | - **cdp_url** (default: `None`)
 93 |   URL for connecting to a Chrome instance via CDP. Commonly used for debugging or connecting to locally running Chrome instances.
 94 | 
 95 | ### Local Chrome Instance (binary)
 96 | 
 97 | Connect to your existing Chrome installation to access saved states and cookies.
 98 | 
 99 | ```python
100 | config = BrowserConfig(
101 |     browser_binary_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
102 | )
103 | ```
104 | 
105 | - **browser_binary_path** (default: `None`)
106 |   Path to connect to an existing Browser installation. Particularly useful for workflows requiring existing login states or browser preferences.
107 | 
108 | <Note>This will overwrite other browser settings.</Note>
109 | 
110 | # Context Configuration
111 | 
112 | The `BrowserContextConfig` class controls settings for individual browser contexts.
113 | 
114 | ```python
115 | from browser_use.browser.context import BrowserContextConfig
116 | 
117 | config = BrowserContextConfig(
118 |     cookies_file="path/to/cookies.json",
119 |     wait_for_network_idle_page_load_time=3.0,
120 |     window_width=1280,
121 |     window_height=1100,
122 |     locale='en-US',
123 |     user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
124 |     highlight_elements=True,
125 |     viewport_expansion=500,
126 |     allowed_domains=['google.com', 'wikipedia.org'],
127 | )
128 | 
129 | browser = Browser()
130 | context = BrowserContext(browser=browser, config=config)
131 | 
132 | 
133 | async def run_search():
134 | 	agent = Agent(
135 | 		browser_context=context,
136 | 		task='Your task',
137 | 		llm=llm)
138 | ```
139 | 
140 | ## Configuration Options
141 | 
142 | ### Page Load Settings
143 | 
144 | - **minimum_wait_page_load_time** (default: `0.5`)
145 |   Minimum time to wait before capturing page state for LLM input.
146 | 
147 | - **wait_for_network_idle_page_load_time** (default: `1.0`)
148 |   Time to wait for network activity to cease. Increase to 3-5s for slower websites. This tracks essential content loading, not dynamic elements like videos.
149 | 
150 | - **maximum_wait_page_load_time** (default: `5.0`)
151 |   Maximum time to wait for page load before proceeding.
152 | 
153 | ### Display Settings
154 | 
155 | - **window_width** (default: `1280`) and **window_height** (default: `1100`)
156 |   Browser window dimensions. The default size is optimized for general use cases and interaction with common UI elements like cookie banners.
157 | 
158 | - **locale** (default: `None`)
159 |   Specify user locale, for example en-GB, de-DE, etc. Locale will affect the navigator. Language value, Accept-Language request header value as well as number and date formatting rules. If not provided, defaults to the system default locale.
160 | 
161 | - **highlight_elements** (default: `True`)
162 |   Highlight interactive elements on the screen with colorful bounding boxes.
163 | 
164 | - **viewport_expansion** (default: `500`)
165 |   Viewport expansion in pixels. With this you can control how much of the page is included in the context of the LLM. Setting this parameter controls the highlighting of elements:
166 |   - `-1`: All elements from the entire page will be included, regardless of visibility (highest token usage but most complete).
167 |   - `0`: Only elements which are currently visible in the viewport will be included.
168 |   - `500` (default): Elements in the viewport plus an additional 500 pixels in each direction will be included, providing a balance between context and token usage.
169 | 
170 | ### Restrict URLs
171 | 
172 | - **allowed_domains** (default: `None`)
173 |   List of allowed domains that the agent can access. If None, all domains are allowed.
174 |   Example: ['google.com', 'wikipedia.org'] - Here the agent will only be able to access google and wikipedia.
175 | 
176 | ### Debug and Recording
177 | 
178 | - **save_recording_path** (default: `None`)
179 |   Directory path for saving video recordings.
180 | 
181 | - **trace_path** (default: `None`)
182 |   Directory path for saving trace files. Files are automatically named as `{trace_path}/{context_id}.zip`.
183 | 
184 | - **save_playwright_script_path** (default: `None`)
185 |   BETA: Filename to save a replayable playwright python script to containing the steps the agent took.
186 | 


--------------------------------------------------------------------------------
/docs/customize/custom-functions.mdx:
--------------------------------------------------------------------------------
  1 | ---
  2 | title: "Custom Functions"
  3 | description: "Extend default agent and write custom function calls"
  4 | icon: "function"
  5 | ---
  6 | 
  7 | ## Basic Function Registration
  8 | 
  9 | Functions can be either `sync` or `async`. Keep them focused and single-purpose.
 10 | 
 11 | ```python
 12 | from browser_use import Controller, ActionResult
 13 | # Initialize the controller
 14 | controller = Controller()
 15 | 
 16 | @controller.action('Ask user for information')
 17 | def ask_human(question: str) -> str:
 18 |     answer = input(f'\n{question}\nInput: ')
 19 |     return ActionResult(extracted_content=answer)
 20 | ```
 21 | 
 22 | <Note>
 23 |   Basic `Controller` has all basic functionality you might need to interact with
 24 |   the browser already implemented.
 25 | </Note>
 26 | 
 27 | ```python
 28 | # ... then pass controller to the agent
 29 | agent = Agent(
 30 |     task=task,
 31 |     llm=llm,
 32 |     controller=controller
 33 | )
 34 | ```
 35 | 
 36 | <Note>
 37 |   Keep the function name and description short and concise. The Agent use the
 38 |   function solely based on the name and description. The stringified output of
 39 |   the action is passed to the Agent.
 40 | </Note>
 41 | 
 42 | ## Browser-Aware Functions
 43 | 
 44 | For actions that need browser access, simply add the `browser` parameter inside the function parameters:
 45 | 
 46 | <Note>
 47 |   Please note that browser-use’s `Browser` class is a wrapper class around
 48 |   Playwright’s `Browser`. The `Browser.playwright_browser` attr can be used
 49 |   to directly access the Playwright browser object if needed.
 50 | </Note>
 51 | 
 52 | ```python
 53 | from browser_use import Browser, Controller, ActionResult
 54 | 
 55 | controller = Controller()
 56 | @controller.action('Open website')
 57 | async def open_website(url: str, browser: Browser):
 58 |     page = await browser.get_current_page()
 59 |     await page.goto(url)
 60 |     return ActionResult(extracted_content='Website opened')
 61 | ```
 62 | 
 63 | ## Structured Parameters with Pydantic
 64 | 
 65 | For complex actions, you can define parameter schemas using Pydantic models:
 66 | 
 67 | ```python
 68 | from pydantic import BaseModel
 69 | from typing import Optional
 70 | from browser_use import Controller, ActionResult, Browser
 71 | 
 72 | controller = Controller()
 73 | 
 74 | class JobDetails(BaseModel):
 75 |     title: str
 76 |     company: str
 77 |     job_link: str
 78 |     salary: Optional[str] = None
 79 | 
 80 | @controller.action(
 81 |     'Save job details which you found on page',
 82 |     param_model=JobDetails
 83 | )
 84 | async def save_job(params: JobDetails, browser: Browser):
 85 |     print(f"Saving job: {params.title} at {params.company}")
 86 | 
 87 |     # Access browser if needed
 88 |     page = browser.get_current_page()
 89 |     await page.goto(params.job_link)
 90 | ```
 91 | 
 92 | ## Using Custom Actions with multiple agents
 93 | 
 94 | You can use the same controller for multiple agents.
 95 | 
 96 | ```python
 97 | controller = Controller()
 98 | 
 99 | # ... register actions to the controller
100 | 
101 | agent = Agent(
102 |     task="Go to website X and find the latest news",
103 |     llm=llm,
104 |     controller=controller
105 | )
106 | 
107 | # Run the agent
108 | await agent.run()
109 | 
110 | agent2 = Agent(
111 |     task="Go to website Y and find the latest news",
112 |     llm=llm,
113 |     controller=controller
114 | )
115 | 
116 | await agent2.run()
117 | ```
118 | 
119 | <Note>
120 |   The controller is stateless and can be used to register multiple actions and
121 |   multiple agents.
122 | </Note>
123 | 
124 | 
125 | 
126 | ## Exclude functions
127 | If you want less actions to be used by the agent, you can exclude them from the controller.
128 | ```python
129 | controller = Controller(exclude_actions=['open_tab', 'search_google'])
130 | ```
131 | 
132 | 
133 | For more examples like file upload or notifications, visit [examples/custom-functions](https://github.com/browser-use/browser-use/tree/main/examples/custom-functions).
134 | 


--------------------------------------------------------------------------------
/docs/customize/hooks.mdx:
--------------------------------------------------------------------------------
  1 | ---
  2 | title: "Lifecycle Hooks"
  3 | description: "Customize agent behavior with lifecycle hooks"
  4 | icon: "Wrench"
  5 | author: "Carlos A. Planchón"
  6 | ---
  7 | 
  8 | # Using Agent Lifecycle Hooks
  9 | 
 10 | Browser-Use provides lifecycle hooks that allow you to execute custom code at specific points during the agent's execution. These hooks enable you to capture detailed information about the agent's actions, modify behavior, or integrate with external systems.
 11 | 
 12 | ## Available Hooks
 13 | 
 14 | Currently, Browser-Use provides the following hooks:
 15 | 
 16 | | Hook | Description | When it's called |
 17 | | ---- | ----------- | ---------------- |
 18 | | `on_step_start` | Executed at the beginning of each agent step | Before the agent processes the current state and decides on the next action |
 19 | | `on_step_end` | Executed at the end of each agent step | After the agent has executed the action for the current step |
 20 | 
 21 | ## Using Hooks
 22 | 
 23 | Hooks are passed as parameters to the `agent.run()` method. Each hook should be a callable function that accepts the agent instance as its parameter.
 24 | 
 25 | ### Basic Example
 26 | 
 27 | ```python
 28 | from browser_use import Agent
 29 | from langchain_openai import ChatOpenAI
 30 | 
 31 | 
 32 | async def my_step_hook(agent):
 33 |     # inside a hook you can access all the state and methods under the Agent object:
 34 |     #   agent.settings, agent.state, agent.task
 35 |     #   agent.controller, agent.llm, agent.browser, agent.browser_context
 36 |     #   agent.pause(), agent.resume(), agent.add_new_task(...), etc.
 37 |     
 38 |     current_page = await agent.browser_context.get_current_page()
 39 |     
 40 |     visit_log = agent.state.history.urls()
 41 |     current_url = current_page.url
 42 |     previous_url = visit_log[-2] if len(visit_log) >= 2 else None
 43 |     print(f"Agent was last on URL: {previous_url} and is now on {current_url}")
 44 |     
 45 |     # You also have direct access to the playwright Page and Browser Context
 46 |     #   https://playwright.dev/python/docs/api/class-page
 47 | 
 48 |     # Example: listen for events on the page, interact with the DOM, run JS directly, etc.
 49 |     await current_page.on('domcontentloaded', async lambda: print('page navigated to a new url...'))
 50 |     await current_page.locator("css=form > input[type=submit]").click()
 51 |     await current_page.evaluate('() => alert(1)')
 52 |     await agent.browser_context.session.context.add_init_script('/* some JS to run on every page */')
 53 |     
 54 |     # Example: monitor or intercept all network requests
 55 |     async def handle_request(route):
 56 | 		# Print, modify, block, etc. do anything to the requests here
 57 |         #   https://playwright.dev/python/docs/network#handle-requests
 58 | 		print(route.request, route.request.headers)
 59 | 		await route.continue_(headers=route.request.headers)
 60 | 	await current_page.route("**/*", handle_route)
 61 | 
 62 |     # Example: pause agent execution and resume it based on some custom code
 63 |     if '/completed' in current_url:
 64 |         agent.pause()
 65 |         Path('result.txt').write_text(await current_page.content()) 
 66 |         input('Saved "completed" page content to result.txt, press [Enter] to resume...')
 67 |         agent.resume()
 68 |     
 69 | agent = Agent(
 70 |     task="Search for the latest news about AI",
 71 |     llm=ChatOpenAI(model="gpt-4o"),
 72 | )
 73 | 
 74 | await agent.run(
 75 |     on_step_start=my_step_hook,
 76 |     # on_step_end=...
 77 |     max_steps=10
 78 | )
 79 | ```
 80 | 
 81 | ## Complete Example: Agent Activity Recording System
 82 | 
 83 | This comprehensive example demonstrates a complete implementation for recording and saving Browser-Use agent activity, consisting of both server and client components.
 84 | 
 85 | ### Setup Instructions
 86 | 
 87 | To use this example, you'll need to:
 88 | 
 89 | 1. Set up the required dependencies:
 90 |    ```bash
 91 |    pip install fastapi uvicorn prettyprinter pyobjtojson dotenv browser-use langchain-openai
 92 |    ```
 93 | 
 94 | 2. Create two separate Python files:
 95 |    - `api.py` - The FastAPI server component
 96 |    - `client.py` - The Browser-Use agent with recording hook
 97 | 
 98 | 3. Run both components:
 99 |    - Start the API server first: `python api.py`
100 |    - Then run the client: `python client.py`
101 | 
102 | ### Server Component (api.py)
103 | 
104 | The server component handles receiving and storing the agent's activity data:
105 | 
106 | ```python
107 | #!/usr/bin/env python3
108 | 
109 | #
110 | # FastAPI API to record and save Browser-Use activity data.
111 | # Save this code to api.py and run with `python api.py`
112 | # 
113 | 
114 | import json
115 | import base64
116 | from pathlib import Path
117 | 
118 | from fastapi import FastAPI, Request
119 | import prettyprinter
120 | import uvicorn
121 | 
122 | prettyprinter.install_extras()
123 | 
124 | # Utility function to save screenshots
125 | def b64_to_png(b64_string: str, output_file):
126 |     """
127 |     Convert a Base64-encoded string to a PNG file.
128 |     
129 |     :param b64_string: A string containing Base64-encoded data
130 |     :param output_file: The path to the output PNG file
131 |     """
132 |     with open(output_file, "wb") as f:
133 |         f.write(base64.b64decode(b64_string))
134 | 
135 | # Initialize FastAPI app
136 | app = FastAPI()
137 | 
138 | 
139 | @app.post("/post_agent_history_step")
140 | async def post_agent_history_step(request: Request):
141 |     data = await request.json()
142 |     prettyprinter.cpprint(data)
143 | 
144 |     # Ensure the "recordings" folder exists using pathlib
145 |     recordings_folder = Path("recordings")
146 |     recordings_folder.mkdir(exist_ok=True)
147 | 
148 |     # Determine the next file number by examining existing .json files
149 |     existing_numbers = []
150 |     for item in recordings_folder.iterdir():
151 |         if item.is_file() and item.suffix == ".json":
152 |             try:
153 |                 file_num = int(item.stem)
154 |                 existing_numbers.append(file_num)
155 |             except ValueError:
156 |                 # In case the file name isn't just a number
157 |                 pass
158 | 
159 |     if existing_numbers:
160 |         next_number = max(existing_numbers) + 1
161 |     else:
162 |         next_number = 1
163 | 
164 |     # Construct the file path
165 |     file_path = recordings_folder / f"{next_number}.json"
166 | 
167 |     # Save the JSON data to the file
168 |     with file_path.open("w") as f:
169 |         json.dump(data, f, indent=2)
170 | 
171 |     # Optionally save screenshot if needed
172 |     # if "website_screenshot" in data and data["website_screenshot"]:
173 |     #     screenshot_folder = Path("screenshots")
174 |     #     screenshot_folder.mkdir(exist_ok=True)
175 |     #     b64_to_png(data["website_screenshot"], screenshot_folder / f"{next_number}.png")
176 | 
177 |     return {"status": "ok", "message": f"Saved to {file_path}"}
178 | 
179 | if __name__ == "__main__":
180 |     print("Starting Browser-Use recording API on http://0.0.0.0:9000")
181 |     uvicorn.run(app, host="0.0.0.0", port=9000)
182 | ```
183 | 
184 | ### Client Component (client.py)
185 | 
186 | The client component runs the Browser-Use agent with a recording hook:
187 | 
188 | ```python
189 | #!/usr/bin/env python3
190 | 
191 | #
192 | # Client to record and save Browser-Use activity.
193 | # Save this code to client.py and run with `python client.py`
194 | #
195 | 
196 | import asyncio
197 | import requests
198 | from dotenv import load_dotenv
199 | from pyobjtojson import obj_to_json
200 | from langchain_openai import ChatOpenAI
201 | from browser_use import Agent
202 | 
203 | # Load environment variables (for API keys)
204 | load_dotenv()
205 | 
206 | 
207 | def send_agent_history_step(data):
208 |     """Send the agent step data to the recording API"""
209 |     url = "http://127.0.0.1:9000/post_agent_history_step"
210 |     response = requests.post(url, json=data)
211 |     return response.json()
212 | 
213 | 
214 | async def record_activity(agent_obj):
215 |     """Hook function that captures and records agent activity at each step"""
216 |     website_html = None
217 |     website_screenshot = None
218 |     urls_json_last_elem = None
219 |     model_thoughts_last_elem = None
220 |     model_outputs_json_last_elem = None
221 |     model_actions_json_last_elem = None
222 |     extracted_content_json_last_elem = None
223 | 
224 |     print('--- ON_STEP_START HOOK ---')
225 |     
226 |     # Capture current page state
227 |     website_html = await agent_obj.browser_context.get_page_html()
228 |     website_screenshot = await agent_obj.browser_context.take_screenshot()
229 | 
230 |     # Make sure we have state history
231 |     if hasattr(agent_obj, "state"):
232 |         history = agent_obj.state.history
233 |     else:
234 |         history = None
235 |         print("Warning: Agent has no state history")
236 |         return
237 | 
238 |     # Process model thoughts
239 |     model_thoughts = obj_to_json(
240 |         obj=history.model_thoughts(),
241 |         check_circular=False
242 |     )
243 |     if len(model_thoughts) > 0:
244 |         model_thoughts_last_elem = model_thoughts[-1]
245 | 
246 |     # Process model outputs
247 |     model_outputs = agent_obj.state.history.model_outputs()
248 |     model_outputs_json = obj_to_json(
249 |         obj=model_outputs,
250 |         check_circular=False
251 |     )
252 |     if len(model_outputs_json) > 0:
253 |         model_outputs_json_last_elem = model_outputs_json[-1]
254 | 
255 |     # Process model actions
256 |     model_actions = agent_obj.state.history.model_actions()
257 |     model_actions_json = obj_to_json(
258 |         obj=model_actions,
259 |         check_circular=False
260 |     )
261 |     if len(model_actions_json) > 0:
262 |         model_actions_json_last_elem = model_actions_json[-1]
263 | 
264 |     # Process extracted content
265 |     extracted_content = agent_obj.state.history.extracted_content()
266 |     extracted_content_json = obj_to_json(
267 |         obj=extracted_content,
268 |         check_circular=False
269 |     )
270 |     if len(extracted_content_json) > 0:
271 |         extracted_content_json_last_elem = extracted_content_json[-1]
272 | 
273 |     # Process URLs
274 |     urls = agent_obj.state.history.urls()
275 |     urls_json = obj_to_json(
276 |         obj=urls,
277 |         check_circular=False
278 |     )
279 |     if len(urls_json) > 0:
280 |         urls_json_last_elem = urls_json[-1]
281 | 
282 |     # Create a summary of all data for this step
283 |     model_step_summary = {
284 |         "website_html": website_html,
285 |         "website_screenshot": website_screenshot,
286 |         "url": urls_json_last_elem,
287 |         "model_thoughts": model_thoughts_last_elem,
288 |         "model_outputs": model_outputs_json_last_elem,
289 |         "model_actions": model_actions_json_last_elem,
290 |         "extracted_content": extracted_content_json_last_elem
291 |     }
292 | 
293 |     print("--- MODEL STEP SUMMARY ---")
294 |     print(f"URL: {urls_json_last_elem}")
295 |     
296 |     # Send data to the API
297 |     result = send_agent_history_step(data=model_step_summary)
298 |     print(f"Recording API response: {result}")
299 | 
300 | 
301 | async def run_agent():
302 |     """Run the Browser-Use agent with the recording hook"""
303 |     agent = Agent(
304 |         task="Compare the price of gpt-4o and DeepSeek-V3",
305 |         llm=ChatOpenAI(model="gpt-4o"),
306 |     )
307 |     
308 |     try:
309 |         print("Starting Browser-Use agent with recording hook")
310 |         await agent.run(
311 |             on_step_start=record_activity,
312 |             max_steps=30
313 |         )
314 |     except Exception as e:
315 |         print(f"Error running agent: {e}")
316 | 
317 | 
318 | if __name__ == "__main__":
319 |     # Check if API is running
320 |     try:
321 |         requests.get("http://127.0.0.1:9000")
322 |         print("Recording API is available")
323 |     except:
324 |         print("Warning: Recording API may not be running. Start api.py first.")
325 |     
326 |     # Run the agent
327 |     asyncio.run(run_agent())
328 | ```
329 | 
330 | ### Working with the Recorded Data
331 | 
332 | After running the agent, you'll find the recorded data in the `recordings` directory. Here's how you can use this data:
333 | 
334 | 1. **View recorded sessions**: Each JSON file contains a snapshot of agent activity for one step
335 | 2. **Extract screenshots**: You can modify the API to save screenshots separately
336 | 3. **Analyze agent behavior**: Use the recorded data to study how the agent navigates websites
337 | 
338 | ### Extending the Example
339 | 
340 | You can extend this recording system in several ways:
341 | 
342 | 1. **Save screenshots separately**: Uncomment the screenshot saving code in the API
343 | 2. **Add a web dashboard**: Create a simple web interface to view recorded sessions
344 | 3. **Add session IDs**: Modify the API to group steps by agent session
345 | 4. **Add filtering**: Implement filters to record only specific types of actions
346 | 
347 | ## Data Available in Hooks
348 | 
349 | When working with agent hooks, you have access to the entire agent instance. Here are some useful data points you can access:
350 | 
351 | - `agent.state.history.model_thoughts()`: Reasoning from Browser Use's model.
352 | - `agent.state.history.model_outputs()`: Raw outputs from the Browsre Use's model.
353 | - `agent.state.history.model_actions()`: Actions taken by the agent
354 | - `agent.state.history.extracted_content()`: Content extracted from web pages
355 | - `agent.state.history.urls()`: URLs visited by the agent
356 | - `agent.browser_context.get_page_html()`: Current page HTML
357 | - `agent.browser_context.take_screenshot()`: Screenshot of the current page
358 | 
359 | ## Tips for Using Hooks
360 | 
361 | - **Avoid blocking operations**: Since hooks run in the same execution thread as the agent, try to keep them efficient or use asynchronous patterns.
362 | - **Handle exceptions**: Make sure your hook functions handle exceptions gracefully to prevent interrupting the agent's main flow.
363 | - **Consider storage needs**: When capturing full HTML and screenshots, be mindful of storage requirements.
364 | 
365 | Contribution by Carlos A. Planchón.
366 | 


--------------------------------------------------------------------------------
/docs/customize/output-format.mdx:
--------------------------------------------------------------------------------
 1 | ---
 2 | title: "Output Format"
 3 | description: "The default is text. But you can define a structured output format to make post-processing easier."
 4 | icon: "code"
 5 | ---
 6 | 
 7 | ## Custom output format
 8 | With [this example](https://github.com/browser-use/browser-use/blob/main/examples/features/custom_output.py) you can define what output format the agent should return to you.
 9 | 
10 | ```python
11 | from pydantic import BaseModel
12 | # Define the output format as a Pydantic model
13 | class Post(BaseModel):
14 | 	post_title: str
15 | 	post_url: str
16 | 	num_comments: int
17 | 	hours_since_post: int
18 | 
19 | 
20 | class Posts(BaseModel):
21 | 	posts: List[Post]
22 | 
23 | 
24 | controller = Controller(output_model=Posts)
25 | 
26 | 
27 | async def main():
28 | 	task = 'Go to hackernews show hn and give me the first  5 posts'
29 | 	model = ChatOpenAI(model='gpt-4o')
30 | 	agent = Agent(task=task, llm=model, controller=controller)
31 | 
32 | 	history = await agent.run()
33 | 
34 | 	result = history.final_result()
35 | 	if result:
36 | 		parsed: Posts = Posts.model_validate_json(result)
37 | 
38 | 		for post in parsed.posts:
39 | 			print('\n--------------------------------')
40 | 			print(f'Title:            {post.post_title}')
41 | 			print(f'URL:              {post.post_url}')
42 | 			print(f'Comments:         {post.num_comments}')
43 | 			print(f'Hours since post: {post.hours_since_post}')
44 | 	else:
45 | 		print('No result')
46 | 
47 | 
48 | if __name__ == '__main__':
49 | 	asyncio.run(main())
50 | ```
51 | 


--------------------------------------------------------------------------------
/docs/customize/real-browser.mdx:
--------------------------------------------------------------------------------
 1 | ---
 2 | title: "Connect to your Browser"
 3 | description: "With this you can connect to your real browser, where you are logged in with all your accounts."
 4 | icon: "computer"
 5 | ---
 6 | 
 7 | ## Overview
 8 | 
 9 | You can connect the agent to your real Chrome browser instance, allowing it to access your existing browser profile with all your logged-in accounts and settings. This is particularly useful when you want the agent to interact with services where you're already authenticated.
10 | 
11 | <Note>
12 |   First make sure to close all running Chrome instances.
13 | </Note>
14 | 
15 | ## Basic Configuration
16 | 
17 | To connect to your real Chrome browser, you'll need to specify the path to your Chrome executable when creating the Browser instance:
18 | 
19 | ```python
20 | from browser_use import Agent, Browser, BrowserConfig
21 | from langchain_openai import ChatOpenAI
22 | import asyncio
23 | # Configure the browser to connect to your Chrome instance
24 | browser = Browser(
25 |     config=BrowserConfig(
26 |         # Specify the path to your Chrome executable
27 |         browser_binary_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',  # macOS path
28 |         # For Windows, typically: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
29 |         # For Linux, typically: '/usr/bin/google-chrome'
30 |     )
31 | )
32 | 
33 | # Create the agent with your configured browser
34 | agent = Agent(
35 |     task="Your task here",
36 |     llm=ChatOpenAI(model='gpt-4o'),
37 |     browser=browser,
38 | )
39 | 
40 | async def main():
41 |     await agent.run()
42 | 
43 |     input('Press Enter to close the browser...')
44 |     await browser.close()
45 | 
46 | if __name__ == '__main__':
47 |     asyncio.run(main())
48 | ```
49 | 
50 | 
51 | <Note>
52 |   When using your real browser, the agent will have access to all your logged-in sessions. Make sure to ALWAYS review the task you're giving to the agent and ensure it aligns with your security requirements!
53 | </Note>
54 | 


--------------------------------------------------------------------------------
/docs/customize/sensitive-data.mdx:
--------------------------------------------------------------------------------
 1 | ---
 2 | title: "Sensitive Data"
 3 | description: "Handle sensitive information securely by preventing the model from seeing actual passwords."
 4 | icon: "shield"
 5 | ---
 6 | 
 7 | ## Handling Sensitive Data
 8 | 
 9 | When working with sensitive information like passwords, you can use the `sensitive_data` parameter to prevent the model from seeing the actual values while still allowing it to reference them in its actions.
10 | 
11 | Make sure to always set [`allowed_domains`](https://docs.browser-use.com/customize/browser-settings#restrict-urls) to restrict the domains the Agent is allowed to visit when working with sensitive data or logins.
12 | 
13 | Here's an example of how to use sensitive data:
14 | 
15 | ```python
16 | from dotenv import load_dotenv
17 | from langchain_openai import ChatOpenAI
18 | from browser_use import Agent
19 | 
20 | load_dotenv()
21 | 
22 | # Initialize the model
23 | llm = ChatOpenAI(
24 |     model='gpt-4o',
25 |     temperature=0.0,
26 | )
27 | 
28 | # Define sensitive data
29 | # The model will only see the keys (x_name, x_password) but never the actual values
30 | sensitive_data = {'x_name': 'magnus', 'x_password': '12345678'}
31 | 
32 | # Use the placeholder names in your task description
33 | task = 'go to x.com and login with x_name and x_password then write a post about the meaning of life'
34 | 
35 | # Pass the sensitive data to the agent
36 | agent = Agent(
37 |     task=task,
38 |     llm=llm,
39 |     sensitive_data=sensitive_data,
40 |     browser=Browser(
41 |         config=BrowserConfig(
42 |             allowed_domains=['example.com'],  # domains that the agent should be restricted to
43 |         ),
44 |     )
45 | )
46 | 
47 | async def main():
48 |     await agent.run()
49 | 
50 | if __name__ == '__main__':
51 |     asyncio.run(main())
52 | ```
53 | 
54 | In this example:
55 | 1. The model only sees `x_name` and `x_password` as placeholders.
56 | 2. When the model wants to use your password it outputs x_password - and we replace it with the actual value.
57 | 3. When your password is visible on the current page, we replace it in the LLM input - so that the model never has it in its state.
58 | 4. The agent will be prevented from going to any site not on `example.com` to protect from prompt injection attacks and jailbreaks
59 | 
60 | ### Missing or Empty Values
61 | 
62 | When working with sensitive data, keep these details in mind:
63 | 
64 | - If a key referenced by the model (`<secret>key_name</secret>`) is missing from your `sensitive_data` dictionary, a warning will be logged but the substitution tag will be preserved.
65 | - If you provide an empty value for a key in the `sensitive_data` dictionary, it will be treated the same as a missing key.
66 | - The system will always attempt to process all valid substitutions, even if some keys are missing or empty.
67 | 
68 | Warning: Vision models still see the image of the page - where the sensitive data might be visible.
69 | 
70 | This approach ensures that sensitive information remains secure while still allowing the agent to perform tasks that require authentication.
71 | 


--------------------------------------------------------------------------------
/docs/customize/supported-models.mdx:
--------------------------------------------------------------------------------
  1 | ---
  2 | title: "Supported Models"
  3 | description: "Guide to using different LangChain chat models with Browser Use"
  4 | icon: "robot"
  5 | ---
  6 | 
  7 | ## Overview
  8 | 
  9 | Browser Use supports various LangChain chat models. Here's how to configure and use the most popular ones. The full list is available in the [LangChain documentation](https://python.langchain.com/docs/integrations/chat/).
 10 | 
 11 | ## Model Recommendations
 12 | 
 13 | We have yet to test performance across all models. Currently, we achieve the best results using GPT-4o with an 89% accuracy on the [WebVoyager Dataset](https://browser-use.com/posts/sota-technical-report). DeepSeek-V3 is 30 times cheaper than GPT-4o. Gemini-2.0-exp is also gaining popularity in the community because it is currently free.
 14 | We also support local models, like Qwen 2.5, but be aware that small models often return the wrong output structure-which lead to parsing errors. We believe that local models will improve significantly this year.
 15 | 
 16 | 
 17 | <Note>
 18 |   All models require their respective API keys. Make sure to set them in your
 19 |   environment variables before running the agent.
 20 | </Note>
 21 | 
 22 | ## Supported Models
 23 | 
 24 | All LangChain chat models, which support tool-calling are available. We will document the most popular ones here.
 25 | 
 26 | ### OpenAI
 27 | 
 28 | OpenAI's GPT-4o models are recommended for best performance.
 29 | 
 30 | ```python
 31 | from langchain_openai import ChatOpenAI
 32 | from browser_use import Agent
 33 | 
 34 | # Initialize the model
 35 | llm = ChatOpenAI(
 36 |     model="gpt-4o",
 37 |     temperature=0.0,
 38 | )
 39 | 
 40 | # Create agent with the model
 41 | agent = Agent(
 42 |     task="Your task here",
 43 |     llm=llm
 44 | )
 45 | ```
 46 | 
 47 | Required environment variables:
 48 | 
 49 | ```bash .env
 50 | OPENAI_API_KEY=
 51 | ```
 52 | 
 53 | ### Anthropic
 54 | 
 55 | 
 56 | ```python
 57 | from langchain_anthropic import ChatAnthropic
 58 | from browser_use import Agent
 59 | 
 60 | # Initialize the model
 61 | llm = ChatAnthropic(
 62 |     model_name="claude-3-5-sonnet-20240620",
 63 |     temperature=0.0,
 64 |     timeout=100, # Increase for complex tasks
 65 | )
 66 | 
 67 | # Create agent with the model
 68 | agent = Agent(
 69 |     task="Your task here",
 70 |     llm=llm
 71 | )
 72 | ```
 73 | 
 74 | And add the variable:
 75 | 
 76 | ```bash .env
 77 | ANTHROPIC_API_KEY=
 78 | ```
 79 | 
 80 | ### Azure OpenAI
 81 | 
 82 | ```python
 83 | from langchain_openai import AzureChatOpenAI
 84 | from browser_use import Agent
 85 | from pydantic import SecretStr
 86 | import os
 87 | 
 88 | # Initialize the model
 89 | llm = AzureChatOpenAI(
 90 |     model="gpt-4o",
 91 |     api_version='2024-10-21',
 92 |     azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT', ''),
 93 |     api_key=SecretStr(os.getenv('AZURE_OPENAI_KEY', '')),
 94 | )
 95 | 
 96 | # Create agent with the model
 97 | agent = Agent(
 98 |     task="Your task here",
 99 |     llm=llm
100 | )
101 | ```
102 | 
103 | Required environment variables:
104 | 
105 | ```bash .env
106 | AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
107 | AZURE_OPENAI_KEY=
108 | ```
109 | 
110 | 
111 | ### Gemini
112 | 
113 | ```python
114 | from langchain_google_genai import ChatGoogleGenerativeAI
115 | from browser_use import Agent
116 | from dotenv import load_dotenv
117 | 
118 | # Read GEMINI_API_KEY into env
119 | load_dotenv()
120 | 
121 | # Initialize the model
122 | llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp')
123 | 
124 | # Create agent with the model
125 | agent = Agent(
126 |     task="Your task here",
127 |     llm=llm
128 | )
129 | ```
130 | 
131 | Required environment variables:
132 | 
133 | ```bash .env
134 | GEMINI_API_KEY=
135 | ```
136 | 
137 | 
138 | ### DeepSeek-V3
139 | The community likes DeepSeek-V3 for its low price, no rate limits, open-source nature, and good performance.
140 | The example is available [here](https://github.com/browser-use/browser-use/blob/main/examples/models/deepseek.py).
141 | 
142 | ```python
143 | from langchain_openai import ChatOpenAI
144 | from browser_use import Agent
145 | from pydantic import SecretStr
146 | from dotenv import load_dotenv
147 | 
148 | load_dotenv()
149 | api_key = os.getenv("DEEPSEEK_API_KEY")
150 | 
151 | # Initialize the model
152 | llm=ChatOpenAI(base_url='https://api.deepseek.com/v1', model='deepseek-chat', api_key=SecretStr(api_key))
153 | 
154 | # Create agent with the model
155 | agent = Agent(
156 |     task="Your task here",
157 |     llm=llm,
158 |     use_vision=False
159 | )
160 | ```
161 | 
162 | Required environment variables:
163 | 
164 | ```bash .env
165 | DEEPSEEK_API_KEY=
166 | ```
167 | 
168 | ### DeepSeek-R1
169 | We support DeepSeek-R1. Its not fully tested yet, more and more functionality will be added, like e.g. the output of it'sreasoning content.
170 | The example is available [here](https://github.com/browser-use/browser-use/blob/main/examples/models/deepseek-r1.py).
171 | It does not support vision. The model is open-source so you could also use it with Ollama, but we have not tested it.
172 | ```python
173 | from langchain_openai import ChatOpenAI
174 | from browser_use import Agent
175 | from pydantic import SecretStr
176 | from dotenv import load_dotenv
177 | 
178 | load_dotenv()
179 | api_key = os.getenv("DEEPSEEK_API_KEY")
180 | 
181 | # Initialize the model
182 | llm=ChatOpenAI(base_url='https://api.deepseek.com/v1', model='deepseek-reasoner', api_key=SecretStr(api_key))
183 | 
184 | # Create agent with the model
185 | agent = Agent(
186 |     task="Your task here",
187 |     llm=llm,
188 |     use_vision=False
189 | )
190 | ```
191 | 
192 | Required environment variables:
193 | 
194 | ```bash .env
195 | DEEPSEEK_API_KEY=
196 | ```
197 | 
198 | ### Ollama
199 | Many users asked for local models. Here they are.
200 | 
201 | 1. Download Ollama from [here](https://ollama.ai/download)
202 | 2. Run `ollama pull model_name`. Pick a model which supports tool-calling from [here](https://ollama.com/search?c=tools)
203 | 3. Run `ollama start`
204 | 
205 | ```python
206 | from langchain_ollama import ChatOllama
207 | from browser_use import Agent
208 | from pydantic import SecretStr
209 | 
210 | 
211 | # Initialize the model
212 | llm=ChatOllama(model="qwen2.5", num_ctx=32000)
213 | 
214 | # Create agent with the model
215 | agent = Agent(
216 |     task="Your task here",
217 |     llm=llm
218 | )
219 | ```
220 | 
221 | Required environment variables: None!
222 | 
223 | ### Novita AI
224 | [Novita AI](https://novita.ai) is an LLM API provider that offers a wide range of models. Note: choose a model that supports function calling.
225 | 
226 | ```python
227 | from langchain_openai import ChatOpenAI
228 | from browser_use import Agent
229 | from pydantic import SecretStr
230 | from dotenv import load_dotenv
231 | import os
232 | 
233 | load_dotenv()
234 | api_key = os.getenv("NOVITA_API_KEY")
235 | 
236 | # Initialize the model
237 | llm = ChatOpenAI(base_url='https://api.novita.ai/v3/openai', model='deepseek/deepseek-v3-0324', api_key=SecretStr(api_key))
238 | 
239 | # Create agent with the model
240 | agent = Agent(
241 |     task="Your task here",
242 |     llm=llm,
243 |     use_vision=False
244 | )
245 | ```
246 | 
247 | Required environment variables:
248 | 
249 | ```bash .env
250 | NOVITA_API_KEY=
251 | ```
252 | ### X AI
253 | [X AI](https://x.ai) is an LLM API provider that offers a wide range of models. Note: choose a model that supports function calling.
254 | 
255 | ```python
256 | from langchain_openai import ChatOpenAI
257 | from browser_use import Agent
258 | from pydantic import SecretStr
259 | from dotenv import load_dotenv
260 | import os
261 | 
262 | load_dotenv()
263 | api_key = os.getenv("GROK_API_KEY")
264 | 
265 | # Initialize the model
266 | llm = ChatOpenAI(
267 |     base_url='https://api.x.ai/v1',
268 |     model='grok-3-beta',
269 |     api_key=SecretStr(api_key)
270 | )
271 | 
272 | # Create agent with the model
273 | agent = Agent(
274 |     task="Your task here",
275 |     llm=llm,
276 |     use_vision=False
277 | )
278 | ```
279 | 
280 | Required environment variables:
281 | 
282 | ```bash .env
283 | GROK_API_KEY=
284 | ```
285 | 
286 | ## Coming soon
287 | (We are working on it)
288 | - Groq
289 | - Github
290 | - Fine-tuned models
291 | 


--------------------------------------------------------------------------------
/docs/customize/system-prompt.mdx:
--------------------------------------------------------------------------------
 1 | ---
 2 | title: "System Prompt"
 3 | description: "Customize the system prompt to control agent behavior and capabilities"
 4 | icon: "message"
 5 | ---
 6 | 
 7 | ## Overview
 8 | 
 9 | You can customize the system prompt in two ways:
10 | 
11 | 1. Extend the default system prompt with additional instructions
12 | 2. Override the default system prompt entirely
13 | 
14 | <Note>
15 |   Custom system prompts allow you to modify the agent's behavior at a
16 |   fundamental level. Use this feature carefully as it can significantly impact
17 |   the agent's performance and reliability.
18 | </Note>
19 | 
20 | ### Extend System Prompt (recommended)
21 | 
22 | To add additional instructions to the default system prompt:
23 | 
24 | ```python
25 | extend_system_message = """
26 | REMEMBER the most important RULE:
27 | ALWAYS open first a new tab and go first to url wikipedia.com no matter the task!!!
28 | """
29 | ```
30 | 
31 | ### Override System Prompt
32 | 
33 | <Warning>
34 |   Not recommended! If you must override the [default system
35 |   prompt](https://github.com/browser-use/browser-use/blob/main/browser_use/agent/system_prompt.md),
36 |   make sure to test the agent yourself.
37 | </Warning>
38 | 
39 | Anyway, to override the default system prompt:
40 | 
41 | ```python
42 | # Define your complete custom prompt
43 | override_system_message = """
44 | You are an AI agent that helps users with web browsing tasks.
45 | 
46 | [Your complete custom instructions here...]
47 | """
48 | 
49 | # Create agent with custom system prompt
50 | agent = Agent(
51 |     task="Your task here",
52 |     llm=ChatOpenAI(model='gpt-4'),
53 |     override_system_message=override_system_message
54 | )
55 | ```
56 | 
57 | ### Extend Planner System Prompt
58 | 
59 | You can customize the behavior of the planning agent by extending its system prompt:
60 | 
61 | ```python
62 | extend_planner_system_message = """
63 | PRIORITIZE gathering information before taking any action.
64 | Always suggest exploring multiple options before making a decision.
65 | """
66 | 
67 | # Create agent with extended planner system prompt
68 | llm = ChatOpenAI(model='gpt-4o')
69 | planner_llm = ChatOpenAI(model='gpt-4o-mini')
70 | 
71 | agent = Agent(
72 | 	task="Your task here",
73 | 	llm=llm,
74 | 	planner_llm=planner_llm,
75 | 	extend_planner_system_message=extend_planner_system_message
76 | )
77 | ```
78 | 


--------------------------------------------------------------------------------
/docs/development.mdx:
--------------------------------------------------------------------------------
  1 | ---
  2 | title: 'Development'
  3 | description: 'Preview changes locally to update your docs'
  4 | ---
  5 | 
  6 | <Info>
  7 |   **Prerequisite**: Please install Node.js (version 19 or higher) before proceeding.
  8 | </Info>
  9 | 
 10 | Follow these steps to install and run Mintlify on your operating system:
 11 | 
 12 | **Step 1**: Install Mintlify:
 13 | 
 14 | <CodeGroup>
 15 | 
 16 |   ```bash npm
 17 |   npm i -g mintlify
 18 |   ```
 19 | 
 20 | ```bash yarn
 21 | yarn global add mintlify
 22 | ```
 23 | 
 24 | </CodeGroup>
 25 | 
 26 | **Step 2**: Navigate to the docs directory (where the `mint.json` file is located) and execute the following command:
 27 | 
 28 | ```bash
 29 | mintlify dev
 30 | ```
 31 | 
 32 | A local preview of your documentation will be available at `http://localhost:3000`.
 33 | 
 34 | ### Custom Ports
 35 | 
 36 | By default, Mintlify uses port 3000. You can customize the port Mintlify runs on by using the `--port` flag. To run Mintlify on port 3333, for instance, use this command:
 37 | 
 38 | ```bash
 39 | mintlify dev --port 3333
 40 | ```
 41 | 
 42 | If you attempt to run Mintlify on a port that's already in use, it will use the next available port:
 43 | 
 44 | ```md
 45 | Port 3000 is already in use. Trying 3001 instead.
 46 | ```
 47 | 
 48 | ## Mintlify Versions
 49 | 
 50 | Please note that each CLI release is associated with a specific version of Mintlify. If your local website doesn't align with the production version, please update the CLI:
 51 | 
 52 | <CodeGroup>
 53 | 
 54 | ```bash npm
 55 | npm i -g mintlify@latest
 56 | ```
 57 | 
 58 | ```bash yarn
 59 | yarn global upgrade mintlify
 60 | ```
 61 | 
 62 | </CodeGroup>
 63 | 
 64 | ## Validating Links
 65 | 
 66 | The CLI can assist with validating reference links made in your documentation. To identify any broken links, use the following command:
 67 | 
 68 | ```bash
 69 | mintlify broken-links
 70 | ```
 71 | 
 72 | ## Deployment
 73 | 
 74 | <Tip>
 75 |   Unlimited editors available under the [Pro
 76 |   Plan](https://mintlify.com/pricing) and above.
 77 | </Tip>
 78 | 
 79 | If the deployment is successful, you should see the following:
 80 | 
 81 | <Frame>
 82 |   <img src="/images/checks-passed.png" style={{ borderRadius: '0.5rem' }} />
 83 | </Frame>
 84 | 
 85 | ## Code Formatting
 86 | 
 87 | We suggest using extensions on your IDE to recognize and format MDX. If you're a VSCode user, consider the [MDX VSCode extension](https://marketplace.visualstudio.com/items?itemName=unifiedjs.vscode-mdx) for syntax highlighting, and [Prettier](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode) for code formatting.
 88 | 
 89 | ## Troubleshooting
 90 | 
 91 | <AccordionGroup>
 92 |   <Accordion title='Error: Could not load the "sharp" module using the darwin-arm64 runtime'>
 93 | 
 94 |     This may be due to an outdated version of node. Try the following:
 95 |     1. Remove the currently-installed version of mintlify: `npm remove -g mintlify`
 96 |     2. Upgrade to Node v19 or higher.
 97 |     3. Reinstall mintlify: `npm install -g mintlify`
 98 |   </Accordion>
 99 | 
100 |   <Accordion title="Issue: Encountering an unknown error">
101 | 
102 |     Solution: Go to the root of your device and delete the \~/.mintlify folder. Afterwards, run `mintlify dev` again.
103 |   </Accordion>
104 | </AccordionGroup>
105 | 
106 | Curious about what changed in the CLI version? [Check out the CLI changelog.](https://www.npmjs.com/package/mintlify?activeTab=versions)
107 | 
108 | # Development Workflow
109 | 
110 | ## Branches
111 | - **`stable`**: Mirrors the latest stable release. This branch is updated only when a new stable release is published (every few weeks).
112 | - **`main`**: The primary development branch. This branch is updated frequently (every hour or more).
113 | 
114 | ## Tags
115 | - **`x.x.x`**: Stable release tags. These are created for stable releases and updated every few weeks.
116 | - **`x.x.xrcXX`**: Pre-release tags. These are created for unstable pre-releases and updated every Friday at 5 PM UTC.
117 | 
118 | ## Workflow Summary
119 | 1. **Push to `main`**:
120 |    - Runs pre-commit hooks to fix formatting.
121 |    - Executes tests to ensure code quality.
122 | 
123 | 2. **Release a new version**:
124 |    - If the tag is a pre-release (`x.x.xrcXX`), the package is pushed to PyPI as a pre-release.
125 |    - If the tag is a stable release (`x.x.x`), the package is pushed to PyPI as a stable release, and the `stable` branch is updated to match the release.
126 | 
127 | 3. **Scheduled Pre-Releases**:
128 |    - Every Friday at 5 PM UTC, a new pre-release tag (`x.x.xrcXX`) is created from the `main` branch and pushed to the repository.
129 | 


--------------------------------------------------------------------------------
/docs/development/contribution-guide.mdx:
--------------------------------------------------------------------------------
 1 | ---
 2 | title: "Contribution Guide"
 3 | description: "Learn how to contribute to Browser Use"
 4 | icon: "github"
 5 | ---
 6 | 
 7 | 
 8 | - check out our most active issues or ask in [Discord](https://discord.gg/zXJJHtJf3k) for ideas of what to work on
 9 | - get inspiration / share what you build in the [`#showcase-your-work`](https://discord.com/channels/1303749220842340412/1305549200678850642) channel and on [`awesome-browser-use-prompts`](https://github.com/browser-use/awesome-prompts)!
10 | - no typo/style-only nit PRs, you can submit nit fixes but only if part of larger bugfix or new feature PRs
11 | - include a demo screenshot/gif, tests, and ideally an example script demonstrating any changes in your PR
12 | - bump your issues/PRs with comments periodically if you want them to be merged faster
13 | 


--------------------------------------------------------------------------------
/docs/development/evaluations.mdx:
--------------------------------------------------------------------------------
 1 | ---
 2 | title: "Evaluations"
 3 | description: "Test the Browser Use agent on standardized benchmarks"
 4 | icon: "chart-bar"
 5 | ---
 6 | 
 7 | ## Prerequisites
 8 | 
 9 | Browser Use uses proprietary/private test sets that must never be committed to Github and must be fetched through a authorized api request.
10 | Accessing these test sets requires an approved Browser Use account.
11 | There are currently no publicly available test sets, but some may be released in the future.
12 | 
13 | ## Get an Api Access Key
14 | 
15 | First, navigate to https://browser-use.tools and log in with an authorized browser use account.
16 | 
17 | Then, click the "Account" button at the top right of the page, and click the "Cycle New Key" button on that page.
18 | 
19 | Copy the resulting url and secret key into your `.env` file. It should look like this:
20 | 
21 | ```bash .env
22 | EVALUATION_TOOL_URL= ...
23 | EVALUATION_TOOL_SECRET_KEY= ...
24 | ```
25 | 
26 | ## Running Evaluations
27 | 
28 | First, ensure your file `eval/service.py` is up to date.
29 | 
30 | Then run the file:
31 | 
32 | ```bash
33 | python eval/service.py
34 | ```
35 | 
36 | ## Configuring Evaluations
37 | 
38 | You can modify the evaluation by providing flags to the evaluation script. For instance:
39 | 
40 | ```bash
41 | python eval/service.py --parallel_runs 5 --parallel_evaluations 5 --max-steps 25 --start 0 --end 100 --model gpt-4o
42 | ```
43 | 
44 | The evaluations webpage has a convenient GUI for generating these commands. To use it, navigate to https://browser-use.tools/dashboard.
45 | 
46 | Then click the button "New Eval Run" on the left panel. This will open a interface with selectors, inputs, sliders, and switches.
47 | 
48 | Input your desired configuration into the interface and copy the resulting python command at the bottom. Then run this command as before.
49 | 


--------------------------------------------------------------------------------
/docs/development/local-setup.mdx:
--------------------------------------------------------------------------------
 1 | ---
 2 | title: "Local Setup"
 3 | description: "Set up Browser Use development environment locally"
 4 | icon: "laptop-code"
 5 | ---
 6 | 
 7 | ## Prerequisites
 8 | 
 9 | Browser Use requires Python 3.11 or higher. We recommend using [uv](https://docs.astral.sh/uv/) for Python environment management.
10 | 
11 | ## Clone the Repository
12 | 
13 | First, clone the Browser Use repository:
14 | 
15 | ```bash
16 | git clone https://github.com/browser-use/browser-use
17 | cd browser-use
18 | ```
19 | 
20 | ## Environment Setup
21 | 
22 | 1. Create and activate a virtual environment:
23 | 
24 | ```bash
25 | uv venv --python 3.11
26 | source .venv/bin/activate
27 | ```
28 | 
29 | 2. Install dependencies:
30 | 
31 | ```bash
32 | # Install the package in editable mode with all development dependencies
33 | uv sync
34 | ```
35 | 
36 | ## Configuration
37 | 
38 | Set up your environment variables:
39 | 
40 | ```bash
41 | # Copy the example environment file
42 | cp .env.example .env
43 | ```
44 | 
45 | Or manually create a `.env` file with the API key for the models you want to use set:
46 | 
47 | ```bash .env
48 | OPENAI_API_KEY=...
49 | ANTHROPIC_API_KEY=
50 | AZURE_ENDPOINT=
51 | AZURE_OPENAI_API_KEY=
52 | GEMINI_API_KEY=
53 | DEEPSEEK_API_KEY=
54 | GROK_API_KEY=
55 | NOVITA_API_KEY=
56 | ```
57 | 
58 | <Note>
59 |   You can use any LLM model supported by LangChain. See 
60 |   [LangChain Models](/customize/supported-models) for available options and their specific
61 |   API key requirements.
62 | </Note>
63 | 
64 | ## Development
65 | 
66 | After setup, you can:
67 | 
68 | - Try demos in the example library with `uv run examples/simple.py`
69 | - Run the linter/formatter with `uv run ruff format examples/some/file.py`
70 | - Run tests with `uv run pytest`
71 | - Build the package with `uv build`
72 | 
73 | ## Getting Help
74 | 
75 | If you run into any issues:
76 | 
77 | 1. Check our [GitHub Issues](https://github.com/browser-use/browser-use/issues)
78 | 2. Join our [Discord community](https://link.browser-use.com/discord) for support
79 | 
80 | <Note>
81 |   We welcome contributions! See our [Contribution Guide](/development/contribution-guide) for guidelines on how to help improve
82 |   Browser Use.
83 | </Note>
84 | 


--------------------------------------------------------------------------------
/docs/development/n8n-integration.mdx:
--------------------------------------------------------------------------------
  1 | ---
  2 | title: 'n8n Integration'
  3 | description: 'Learn how to integrate Browser Use with n8n workflows'
  4 | ---
  5 | 
  6 | # Browser Use n8n Integration
  7 | 
  8 | Browser Use can be integrated with [n8n](https://n8n.io), a workflow automation platform, using our community node. This integration allows you to trigger browser automation tasks directly from your n8n workflows.
  9 | 
 10 | ## Installing the n8n Community Node
 11 | 
 12 | There are several ways to install the Browser Use community node in n8n:
 13 | 
 14 | ### Using n8n Desktop or Cloud
 15 | 
 16 | 1. Navigate to **Settings > Community Nodes**
 17 | 2. Click on **Install**
 18 | 3. Enter `n8n-nodes-browser-use` in the **Name** field
 19 | 4. Click **Install**
 20 | 
 21 | ### Using a Self-hosted n8n Instance
 22 | 
 23 | Run the following command in your n8n installation directory:
 24 | 
 25 | ```bash
 26 | npm install n8n-nodes-browser-use
 27 | ```
 28 | 
 29 | ### For Development
 30 | 
 31 | If you want to develop with the n8n node:
 32 | 
 33 | 1. Clone the repository:
 34 |    ```bash
 35 |    git clone https://github.com/draphonix/n8n-nodes-browser-use.git
 36 |    ```
 37 | 2. Install dependencies:
 38 |    ```bash
 39 |    cd n8n-nodes-browser-use
 40 |    npm install
 41 |    ```
 42 | 3. Build the code:
 43 |    ```bash
 44 |    npm run build
 45 |    ```
 46 | 4. Link to your n8n installation:
 47 |    ```bash
 48 |    npm link
 49 |    ```
 50 | 5. In your n8n installation directory:
 51 |    ```bash
 52 |    npm link n8n-nodes-browser-use
 53 |    ```
 54 | 
 55 | ## Setting Up Browser Use Cloud API Credentials
 56 | 
 57 | To use the Browser Use node in n8n, you need to configure API credentials:
 58 | 
 59 | 1. Sign up for an account at [Browser Use Cloud](https://cloud.browser-use.com)
 60 | 2. Navigate to the Settings or API section
 61 | 3. Generate or copy your API key
 62 | 4. In n8n, create a new credential:
 63 |    - Go to **Credentials** tab
 64 |    - Click **Create New**
 65 |    - Select **Browser Use Cloud API**
 66 |    - Enter your API key
 67 |    - Save the credential
 68 | 
 69 | ## Using the Browser Use Node
 70 | 
 71 | Once installed, you can add the Browser Use node to your workflows:
 72 | 
 73 | 1. In your workflow editor, search for "Browser Use" in the nodes panel
 74 | 2. Add the node to your workflow
 75 | 3. Set-up the credentials
 76 | 4. Choose your saved credentials
 77 | 5. Select an operation:
 78 |    - **Run Task**: Execute a browser automation task with natural language instructions
 79 |    - **Get Task**: Retrieve task details
 80 |    - **Get Task Status**: Check task execution status
 81 |    - **Pause/Resume/Stop Task**: Control running tasks
 82 |    - **Get Task Media**: Retrieve screenshots, videos, or PDFs
 83 |    - **List Tasks**: Get a list of tasks
 84 | 
 85 | ### Example: Running a Browser Task
 86 | 
 87 | Here's a simple example of how to use the Browser Use node to run a browser task:
 88 | 
 89 | 1. Add the Browser Use node to your workflow
 90 | 2. Select the "Run Task" operation
 91 | 3. In the "Instructions" field, enter a natural language description of what you want the browser to do, for example:
 92 |    ```
 93 |    Go to example.com, take a screenshot of the homepage, and extract all the main heading texts
 94 |    ```
 95 | 4. Optionally enable "Save Browser Data" to preserve cookies and session information
 96 | 5. Connect the node to subsequent nodes to process the results
 97 | 
 98 | ## Workflow Examples
 99 | 
100 | The Browser Use n8n node enables various automation scenarios:
101 | 
102 | - **Web Scraping**: Extract data from websites on a schedule
103 | - **Form Filling**: Automate data entry across web applications
104 | - **Monitoring**: Check website status and capture visual evidence
105 | - **Report Generation**: Generate PDFs or screenshots of web dashboards
106 | - **Multi-step Processes**: Chain browser tasks together using session persistence
107 | 
108 | ## Troubleshooting
109 | 
110 | If you encounter issues with the Browser Use node:
111 | 
112 | - Verify your API key is valid and has sufficient credits
113 | - Check that your instructions are clear and specific
114 | - For complex tasks, consider breaking them into multiple steps
115 | - Refer to the [Browser Use documentation](https://docs.browser-use.com) for instruction best practices
116 | 
117 | ## Resources
118 | 
119 | - [n8n Community Nodes Documentation](https://docs.n8n.io/integrations/community-nodes/)
120 | - [Browser Use Documentation](https://docs.browser-use.com)
121 | - [Browser Use Cloud](https://cloud.browser-use.com)
122 | - [n8n-nodes-browser-use GitHub Repository](https://github.com/draphonix/n8n-nodes-browser-use) 
123 | 


--------------------------------------------------------------------------------
/docs/development/observability.mdx:
--------------------------------------------------------------------------------
 1 | ---
 2 | title: "Observability"
 3 | description: "Trace Browser Use's agent execution steps and browser sessions"
 4 | icon: "eye"
 5 | ---
 6 | 
 7 | ## Overview
 8 | 
 9 | Browser Use has a native integration with [Laminar](https://lmnr.ai) - open-source platform for tracing, evals and labeling of AI agents.
10 | Read more about Laminar in the [Laminar docs](https://docs.lmnr.ai).
11 | 
12 | <Note>
13 |   Laminar excels at tracing browser agents by providing unified visibility into both browser session recordings and agent execution steps.
14 | </Note>
15 | 
16 | ## Setup
17 | 
18 | To setup Laminar, you need to install the `lmnr` package and set the `LMNR_PROJECT_API_KEY` environment variable.
19 | 
20 | To get your project API key, you can either:
21 | - Register on [Laminar Cloud](https://lmnr.ai) and get the key from your project settings
22 | - Or spin up a local Laminar instance and get the key from the settings page
23 | 
24 | ```bash
25 | pip install 'lmnr[all]'
26 | export LMNR_PROJECT_API_KEY=<your-project-api-key>
27 | ```
28 | 
29 | ## Usage
30 | 
31 | Then, you simply initialize the Laminar at the top of your project and both Browser Use and session recordings will be automatically traced.
32 | 
33 | ```python {5-8}
34 | from langchain_openai import ChatOpenAI
35 | from browser_use import Agent
36 | import asyncio
37 | 
38 | from lmnr import Laminar
39 | # this line auto-instruments Browser Use and any browser you use (local or remote)
40 | Laminar.initialize(project_api_key="...") # you can also pass project api key here
41 | 
42 | async def main():
43 |     agent = Agent(
44 |         task="open google, search Laminar AI",
45 |         llm=ChatOpenAI(model="gpt-4o-mini"),
46 |     )
47 |     result = await agent.run()
48 |     print(result)
49 | 
50 | asyncio.run(main())
51 | ```
52 | 
53 | ## Viewing Traces
54 | 
55 | You can view traces in the Laminar UI by going to the traces tab in your project.
56 | When you select a trace, you can see both the browser session recording and the agent execution steps.
57 | 
58 | Timeline of the browser session is synced with the agent execution steps, timeline highlights indicate the agent's current step synced with the browser session.
59 | In the trace view, you can also see the agent's current step, the tool it's using, and the tool's input and output. Tools are highlighted in the timeline with a yellow color.
60 | 
61 | <img className="block" src="/images/laminar.png" alt="Laminar" />
62 | 
63 | 
64 | ## Laminar
65 | 
66 | To learn more about tracing and evaluating your browser agents, check out the [Laminar docs](https://docs.lmnr.ai).
67 | 


--------------------------------------------------------------------------------
/docs/development/roadmap.mdx:
--------------------------------------------------------------------------------
1 | ---
2 | title: "Roadmap"
3 | description: "Future plans and upcoming features for Browser Use"
4 | icon: "road"
5 | ---
6 | 
7 | Big things coming soon!
8 | 


--------------------------------------------------------------------------------
/docs/development/telemetry.mdx:
--------------------------------------------------------------------------------
 1 | ---
 2 | title: "Telemetry"
 3 | description: "Understanding Browser Use's telemetry and privacy settings"
 4 | icon: "chart-mixed"
 5 | ---
 6 | 
 7 | ## Overview
 8 | 
 9 | Browser Use collects anonymous usage data to help us understand how the library is being used and to improve the user experience. It also helps us fix bugs faster and prioritize feature development.
10 | 
11 | ## Data Collection
12 | 
13 | We use [PostHog](https://posthog.com) for telemetry collection. The data is completely anonymized and contains no personally identifiable information.
14 | 
15 | <Note>
16 |   We never collect personal information, credentials, or specific content from
17 |   your browser automation tasks.
18 | </Note>
19 | 
20 | ## Opting Out
21 | 
22 | You can disable telemetry by setting an environment variable:
23 | 
24 | ```bash .env
25 | ANONYMIZED_TELEMETRY=false
26 | ```
27 | 
28 | Or in your Python code:
29 | 
30 | ```python
31 | import os
32 | os.environ["ANONYMIZED_TELEMETRY"] = "false"
33 | ```
34 | 
35 | <Note>
36 |   Even when enabled, telemetry has zero impact on the library's performance or
37 |   functionality. Code is available in [Telemetry
38 |   Service](https://github.com/browser-use/browser-use/tree/main/browser_use/telemetry).
39 | </Note>
40 | 


--------------------------------------------------------------------------------
/docs/favicon.svg:
--------------------------------------------------------------------------------
 1 | <svg width="100" height="100" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
 2 | <g clip-path="url(#clip0_7_13)">
 3 | <path d="M97.8916 39.0448C82.6177 33.1997 95.2199 10.8169 74.212 11.3849C48.5413 12.0793 8.31528 52.4518 12.4236 78.6851C14.4652 91.6755 24.6096 86.2218 29.3732 88.1154C32.5364 89.3652 36.2792 95.0083 40.3245 95.9047C22.4293 106.193 -0.556809 96.397 0.0102912 74.3423C0.829435 41.86 47.7474 -5.25386 81.1937 0.477571C99.8702 3.68414 102.189 23.5422 97.8916 39.0448Z" fill="white"/>
 4 | <path d="M24.8115 57.7541L39.6068 71.7166C49.0332 80.1875 74.061 94.9706 85.403 84.9469C98.774 73.1306 70.495 32.3162 57.4769 25.802L68.9069 20.6639C86.7138 33.6796 113.783 75.9836 91.7294 94.4025C77.5014 106.282 54.5655 96.2204 41.0811 87.3707C30.8103 80.6294 15.9647 70.9591 24.8115 57.7415V57.7541Z" fill="white"/>
 5 | <path d="M40.3373 4.75723C35.5485 4.88347 31.8055 11.1199 28.2895 12.2182C25.1642 13.1903 20.8414 10.5266 16.1408 14.0487C11.0495 17.8613 12.7891 36.0655 3.02233 40.5976C-2.98893 22.9362 0.75354 1.8789 22.4672 0.0736228C24.1433 -0.0652445 42.7822 1.17195 40.3373 4.74463V4.75723Z" fill="white"/>
 6 | <path d="M76.1025 57.754C84.1175 71.0348 69.5871 86.2092 57.489 74.1025L76.1025 57.754Z" fill="white"/>
 7 | </g>
 8 | <defs>
 9 | <clipPath id="clip0_7_13">
10 | <rect width="100" height="100" fill="white"/>
11 | </clipPath>
12 | </defs>
13 | </svg>
14 | 


--------------------------------------------------------------------------------
/docs/images/browser-use.png:
--------------------------------------------------------------------------------
https://raw.githubusercontent.com/browser-use/browser-use/main/docs/images/browser-use.png


--------------------------------------------------------------------------------
/docs/images/checks-passed.png:
--------------------------------------------------------------------------------
https://raw.githubusercontent.com/browser-use/browser-use/main/docs/images/checks-passed.png


--------------------------------------------------------------------------------
/docs/images/laminar.png:
--------------------------------------------------------------------------------
https://raw.githubusercontent.com/browser-use/browser-use/main/docs/images/laminar.png


--------------------------------------------------------------------------------
/docs/introduction.mdx:
--------------------------------------------------------------------------------
  1 | ---
  2 | title: "Introduction"
  3 | description: "Welcome to Browser Use - We enable AI to control your browser"
  4 | icon: "book-open"
  5 | ---
  6 | 
  7 | <img className="block" src="/images/browser-use.png" alt="Browser Use" />
  8 | 
  9 | ## Overview
 10 | 
 11 | Browser Use is the easiest way to connect your AI agents with the browser. It makes websites accessible for AI agents by providing a powerful, yet simple interface for browser automation.
 12 | 
 13 | <Note>
 14 |   If you have used Browser Use for your project, feel free to show it off in our
 15 |   [Discord community](https://link.browser-use.com/discord)!
 16 | </Note>
 17 | 
 18 | ## Getting Started
 19 | 
 20 | <CardGroup cols={2}>
 21 |   <Card title="Quick Start" icon="rocket" href="/quickstart">
 22 |     Get up and running with Browser Use in minutes
 23 |   </Card>
 24 |   <Card
 25 |     title="Supported Models"
 26 |     icon="robot"
 27 |     href="/customize/supported-models"
 28 |   >
 29 |     Configure different LLMs for your agents
 30 |   </Card>
 31 |   <Card title="Agent Settings" icon="gear" href="/customize/agent-settings">
 32 |     Learn how to configure and customize your agents
 33 |   </Card>
 34 |   <Card title="Custom Functions" icon="code" href="/customize/custom-functions">
 35 |     Extend functionality with custom actions
 36 |   </Card>
 37 | </CardGroup>
 38 | 
 39 | ## Fancy Demos
 40 | 
 41 | ### Writing in Google Docs
 42 | 
 43 | Task: Write a letter in Google Docs to my Papa, thanking him for everything, and save the document as a PDF.
 44 | 
 45 | <Frame>
 46 |   <img src="https://github.com/user-attachments/assets/242ade3e-15bc-41c2-988f-cbc5415a66aa" />
 47 | </Frame>
 48 | 
 49 | ### Job Applications
 50 | 
 51 | Task: Read my CV & find ML jobs, save them to a file, and then start applying for them in new tabs.
 52 | 
 53 | <Frame>
 54 |   <video
 55 |     controls
 56 |     src="https://github.com/user-attachments/assets/171fb4d6-0355-46f2-863e-edb04a828d04"
 57 |   />
 58 | </Frame>
 59 | 
 60 | ### Flight Search
 61 | 
 62 | Task: Find flights on kayak.com from Zurich to Beijing.
 63 | 
 64 | <Frame>
 65 |   <img src="https://github.com/user-attachments/assets/ea605d4a-90e6-481e-a569-f0e0db7e6390" />
 66 | </Frame>
 67 | 
 68 | ### Data Collection
 69 | 
 70 | Task: Look up models with a license of cc-by-sa-4.0 and sort by most likes on Hugging Face, save top 5 to file.
 71 | 
 72 | <Frame>
 73 |   <video
 74 |     controls
 75 |     src="https://github.com/user-attachments/assets/de73ee39-432c-4b97-b4e8-939fd7f323b3"
 76 |   />
 77 | </Frame>
 78 | 
 79 | ## Community & Support
 80 | 
 81 | <CardGroup cols={2}>
 82 |   <Card
 83 |     title="Join Discord"
 84 |     icon="discord"
 85 |     href="https://link.browser-use.com/discord"
 86 |   >
 87 |     Join our community for support and showcases
 88 |   </Card>
 89 |   <Card
 90 |     title="GitHub"
 91 |     icon="github"
 92 |     href="https://github.com/browser-use/browser-use"
 93 |   >
 94 |     Star us on GitHub and contribute to development
 95 |   </Card>
 96 | </CardGroup>
 97 | 
 98 | <Note>
 99 |   Browser Use is MIT licensed and actively maintained. We welcome contributions
100 |   and feedback from the community!
101 | </Note>
102 | 


--------------------------------------------------------------------------------
/docs/logo/dark.svg:
--------------------------------------------------------------------------------
1 | <svg width="1867" height="292" viewBox="0 0 1867 292" fill="none" xmlns="http://www.w3.org/2000/svg">
2 | <path d="M266.265 106.202C224.72 90.3033 258.998 29.4218 201.857 30.9671C132.032 32.8557 22.6176 142.669 33.7922 214.023C39.3453 249.357 66.9381 234.523 79.8952 239.674C88.499 243.073 98.6794 258.423 109.683 260.861C61.0078 288.846 -1.51452 262.2 0.0279922 202.211C2.25607 113.859 129.873 -14.2905 220.847 1.29899C271.647 10.0209 277.954 64.0347 266.265 106.202Z" fill="white"/>
3 | <path d="M67.4872 157.091L107.73 195.069C133.37 218.11 201.446 258.32 232.296 231.056C268.665 198.915 191.746 87.9001 156.337 70.1817L187.427 56.2061C235.862 91.6086 309.49 206.676 249.504 256.775C210.804 289.087 148.418 261.72 111.741 237.649C83.8041 219.312 43.4241 193.009 67.4872 157.057V157.091Z" fill="white"/>
4 | <path d="M109.717 12.9395C96.6917 13.2829 86.511 30.246 76.9474 33.2334C68.4465 35.8774 56.6886 28.6321 43.9029 38.2125C30.0546 48.5826 34.7861 98.0981 8.22063 110.426C-8.12999 62.3865 2.04951 5.11049 61.1106 0.200137C65.6695 -0.177582 116.367 3.1876 109.717 12.9053V12.9395Z" fill="white"/>
5 | <path d="M206.999 157.091C228.8 193.214 189.277 234.489 156.37 201.559L206.999 157.091Z" fill="white"/>
6 | <path d="M504.359 178.759C504.359 195.08 498.53 206.701 486.872 213.621C475.289 220.54 460.397 224 442.195 224H393.795V67.9692H439.374C456.523 67.9692 470.513 71.053 481.344 77.2205C492.174 83.388 497.59 93.5419 497.59 107.682C497.59 116.708 494.882 124.079 489.467 129.795C484.051 135.511 477.169 139.385 468.821 141.415C478.899 142.995 487.323 146.718 494.092 152.585C500.937 158.451 504.359 167.176 504.359 178.759ZM466.338 110.39C466.338 103.47 464.157 98.4308 459.795 95.2718C455.508 92.1128 449.002 90.5333 440.277 90.5333H424.708V131.713H441.631C450.13 131.713 456.373 130.021 460.359 126.636C464.345 123.251 466.338 117.836 466.338 110.39ZM472.318 177.969C472.318 169.019 469.836 162.701 464.872 159.015C459.908 155.33 452.913 153.487 443.887 153.487H424.708V200.872H442.533C451.409 200.872 458.591 199.255 464.082 196.021C469.573 192.711 472.318 186.694 472.318 177.969ZM619.064 101.251C622.675 101.251 625.946 101.552 628.88 102.154C631.888 102.68 634.859 103.47 637.793 104.523L632.49 151.118H612.634V127.764C605.037 128.366 598.381 131.788 592.664 138.031C587.023 144.274 582.548 152.735 579.239 163.415V203.354H603.044V224H532.644V203.354H549.454V125.056H532.644V104.523H572.131L577.659 131.938C582.097 121.634 587.625 113.962 594.244 108.923C600.938 103.809 609.211 101.251 619.064 101.251ZM716.508 101.138C728.242 101.138 738.283 103.733 746.631 108.923C754.98 114.038 761.298 121.333 765.585 130.81C769.948 140.212 772.129 151.268 772.129 163.979C772.129 176.916 769.948 188.161 765.585 197.713C761.223 207.19 754.83 214.523 746.406 219.713C738.057 224.827 728.054 227.385 716.395 227.385C704.662 227.385 694.621 224.865 686.272 219.826C677.924 214.786 671.568 207.528 667.206 198.051C662.843 188.574 660.662 177.292 660.662 164.205C660.662 151.72 662.843 140.738 667.206 131.262C671.643 121.709 678.036 114.301 686.385 109.036C694.809 103.771 704.85 101.138 716.508 101.138ZM716.508 123.59C708.084 123.59 701.842 126.899 697.78 133.518C693.719 140.062 691.688 150.291 691.688 164.205C691.688 178.27 693.719 188.574 697.78 195.118C701.842 201.662 708.047 204.933 716.395 204.933C724.744 204.933 730.949 201.662 735.011 195.118C739.072 188.499 741.103 178.12 741.103 163.979C741.103 150.215 739.072 140.062 735.011 133.518C730.949 126.899 724.782 123.59 716.508 123.59ZM917.521 104.523L899.244 224H864.27L852.198 141.077L839.337 224H805.039L785.973 104.523H813.952L824.332 205.497L839.111 119.641H866.526L880.065 205.497L890.67 104.523H917.521ZM983.037 205.385C990.182 205.385 995.823 204.181 999.96 201.774C1004.17 199.292 1006.28 195.832 1006.28 191.395C1006.28 188.311 1005.56 185.791 1004.13 183.836C1002.71 181.88 999.96 180.038 995.899 178.308C991.912 176.503 985.858 174.509 977.734 172.328C969.461 170.222 962.541 167.74 956.975 164.882C951.41 161.949 947.085 158.188 944.001 153.6C940.917 148.937 939.375 143.221 939.375 136.451C939.375 129.532 941.331 123.402 945.242 118.062C949.228 112.721 954.945 108.585 962.391 105.651C969.912 102.643 978.787 101.138 989.017 101.138C1007.22 101.138 1022.75 105.802 1035.61 115.128L1023.43 133.292C1012.52 126.373 1001.28 122.913 989.693 122.913C976.305 122.913 969.611 126.749 969.611 134.421C969.611 137.053 970.401 139.234 971.981 140.964C973.635 142.694 976.456 144.349 980.442 145.928C984.504 147.508 990.709 149.463 999.058 151.795C1007.63 154.202 1014.63 156.834 1020.04 159.692C1025.53 162.55 1029.78 166.349 1032.79 171.087C1035.87 175.826 1037.42 181.88 1037.42 189.251C1037.42 197.525 1034.93 204.557 1029.97 210.349C1025.08 216.065 1018.54 220.352 1010.34 223.21C1002.14 225.993 993.078 227.385 983.15 227.385C972.319 227.385 962.654 225.843 954.155 222.759C945.656 219.675 938.322 215.426 932.155 210.01L947.611 192.636C952.5 196.547 957.953 199.668 963.97 202C969.987 204.256 976.343 205.385 983.037 205.385ZM1098.31 173.344C1099.13 184.099 1102.29 192.072 1107.78 197.262C1113.35 202.451 1120.46 205.046 1129.11 205.046C1134.6 205.046 1139.86 204.181 1144.9 202.451C1149.94 200.721 1155.02 198.164 1160.13 194.779L1172.54 211.815C1166.75 216.704 1159.98 220.54 1152.23 223.323C1144.49 226.031 1136.14 227.385 1127.19 227.385C1114.48 227.385 1103.65 224.752 1094.7 219.487C1085.82 214.222 1079.09 206.851 1074.5 197.374C1069.99 187.897 1067.73 176.916 1067.73 164.431C1067.73 152.472 1069.95 141.716 1074.39 132.164C1078.9 122.537 1085.37 114.978 1093.79 109.487C1102.29 103.921 1112.3 101.138 1123.8 101.138C1134.63 101.138 1144.07 103.545 1152.12 108.359C1160.17 113.173 1166.37 120.13 1170.74 129.231C1175.1 138.256 1177.28 149.012 1177.28 161.497C1177.28 165.785 1177.09 169.733 1176.72 173.344H1098.31ZM1123.92 122.123C1116.47 122.123 1110.45 124.793 1105.87 130.133C1101.35 135.398 1098.72 143.446 1097.97 154.277H1148.29C1148.14 143.973 1145.99 136.038 1141.86 130.472C1137.79 124.906 1131.81 122.123 1123.92 122.123ZM1295.82 101.251C1299.43 101.251 1302.7 101.552 1305.64 102.154C1308.65 102.68 1311.62 103.47 1314.55 104.523L1309.25 151.118H1289.39V127.764C1281.79 128.366 1275.14 131.788 1269.42 138.031C1263.78 144.274 1259.31 152.735 1256 163.415V203.354H1279.8V224H1209.4V203.354H1226.21V125.056H1209.4V104.523H1248.89L1254.42 131.938C1258.85 121.634 1264.38 113.962 1271 108.923C1277.7 103.809 1285.97 101.251 1295.82 101.251ZM1584.35 172.328C1584.35 183.084 1582.17 192.636 1577.81 200.985C1573.52 209.258 1567.16 215.726 1558.74 220.39C1550.32 225.053 1540.2 227.385 1528.39 227.385C1516.43 227.385 1506.28 225.091 1497.93 220.503C1489.58 215.915 1483.26 209.484 1478.98 201.21C1474.76 192.937 1472.66 183.309 1472.66 172.328V67.9692H1503.57V163.641C1503.57 172.817 1504.36 180.301 1505.94 186.092C1507.52 191.884 1510.12 196.246 1513.73 199.179C1517.34 202.113 1522.22 203.579 1528.39 203.579C1534.56 203.579 1539.45 202.113 1543.06 199.179C1546.74 196.246 1549.38 191.884 1550.96 186.092C1552.54 180.301 1553.33 172.817 1553.33 163.641V67.9692H1584.35V172.328ZM1659.79 205.385C1666.94 205.385 1672.58 204.181 1676.72 201.774C1680.93 199.292 1683.04 195.832 1683.04 191.395C1683.04 188.311 1682.32 185.791 1680.89 183.836C1679.46 181.88 1676.72 180.038 1672.66 178.308C1668.67 176.503 1662.62 174.509 1654.49 172.328C1646.22 170.222 1639.3 167.74 1633.73 164.882C1628.17 161.949 1623.84 158.188 1620.76 153.6C1617.68 148.937 1616.13 143.221 1616.13 136.451C1616.13 129.532 1618.09 123.402 1622 118.062C1625.99 112.721 1631.7 108.585 1639.15 105.651C1646.67 102.643 1655.55 101.138 1665.77 101.138C1683.98 101.138 1699.51 105.802 1712.37 115.128L1700.18 133.292C1689.28 126.373 1678.03 122.913 1666.45 122.913C1653.06 122.913 1646.37 126.749 1646.37 134.421C1646.37 137.053 1647.16 139.234 1648.74 140.964C1650.39 142.694 1653.21 144.349 1657.2 145.928C1661.26 147.508 1667.47 149.463 1675.82 151.795C1684.39 154.202 1691.38 156.834 1696.8 159.692C1702.29 162.55 1706.54 166.349 1709.55 171.087C1712.63 175.826 1714.17 181.88 1714.17 189.251C1714.17 197.525 1711.69 204.557 1706.73 210.349C1701.84 216.065 1695.3 220.352 1687.1 223.21C1678.9 225.993 1669.84 227.385 1659.91 227.385C1649.08 227.385 1639.41 225.843 1630.91 222.759C1622.41 219.675 1615.08 215.426 1608.91 210.01L1624.37 192.636C1629.26 196.547 1634.71 199.668 1640.73 202C1646.75 204.256 1653.1 205.385 1659.79 205.385ZM1775.06 173.344C1775.89 184.099 1779.05 192.072 1784.54 197.262C1790.11 202.451 1797.21 205.046 1805.86 205.046C1811.35 205.046 1816.62 204.181 1821.66 202.451C1826.7 200.721 1831.78 198.164 1836.89 194.779L1849.3 211.815C1843.51 216.704 1836.74 220.54 1828.99 223.323C1821.25 226.031 1812.9 227.385 1803.95 227.385C1791.24 227.385 1780.4 224.752 1771.45 219.487C1762.58 214.222 1755.85 206.851 1751.26 197.374C1746.75 187.897 1744.49 176.916 1744.49 164.431C1744.49 152.472 1746.71 141.716 1751.15 132.164C1755.66 122.537 1762.13 114.978 1770.55 109.487C1779.05 103.921 1789.05 101.138 1800.56 101.138C1811.39 101.138 1820.83 103.545 1828.88 108.359C1836.93 113.173 1843.13 120.13 1847.5 129.231C1851.86 138.256 1854.04 149.012 1854.04 161.497C1854.04 165.785 1853.85 169.733 1853.47 173.344H1775.06ZM1800.67 122.123C1793.23 122.123 1787.21 124.793 1782.62 130.133C1778.11 135.398 1775.48 143.446 1774.73 154.277H1825.04C1824.89 143.973 1822.75 136.038 1818.61 130.472C1814.55 124.906 1808.57 122.123 1800.67 122.123Z" fill="white"/>
7 | </svg>
8 | 


--------------------------------------------------------------------------------
/docs/logo/light.svg:
--------------------------------------------------------------------------------
1 | <svg width="1867" height="292" viewBox="0 0 1867 292" fill="none" xmlns="http://www.w3.org/2000/svg">
2 | <path d="M266.265 106.202C224.72 90.3033 258.998 29.4218 201.857 30.9671C132.032 32.8557 22.6176 142.669 33.7922 214.023C39.3453 249.357 66.9381 234.523 79.8952 239.674C88.499 243.073 98.6794 258.423 109.683 260.861C61.0078 288.846 -1.51452 262.2 0.0279922 202.211C2.25607 113.859 129.873 -14.2905 220.847 1.29899C271.647 10.0209 277.954 64.0347 266.265 106.202Z" fill="black"/>
3 | <path d="M67.4872 157.091L107.73 195.069C133.37 218.11 201.446 258.32 232.296 231.056C268.665 198.915 191.746 87.9001 156.337 70.1817L187.427 56.2061C235.862 91.6086 309.49 206.676 249.504 256.775C210.804 289.087 148.418 261.72 111.741 237.649C83.8041 219.312 43.4241 193.009 67.4872 157.057V157.091Z" fill="black"/>
4 | <path d="M109.717 12.9395C96.6917 13.2829 86.511 30.246 76.9474 33.2334C68.4465 35.8774 56.6886 28.6321 43.9029 38.2125C30.0546 48.5826 34.7861 98.0981 8.22063 110.426C-8.12999 62.3865 2.04951 5.11049 61.1106 0.200137C65.6695 -0.177582 116.367 3.1876 109.717 12.9053V12.9395Z" fill="black"/>
5 | <path d="M206.999 157.091C228.8 193.214 189.277 234.489 156.37 201.559L206.999 157.091Z" fill="black"/>
6 | <path d="M504.359 178.759C504.359 195.08 498.53 206.701 486.872 213.621C475.289 220.54 460.397 224 442.195 224H393.795V67.9692H439.374C456.523 67.9692 470.513 71.053 481.344 77.2205C492.174 83.388 497.59 93.5419 497.59 107.682C497.59 116.708 494.882 124.079 489.467 129.795C484.051 135.511 477.169 139.385 468.821 141.415C478.899 142.995 487.323 146.718 494.092 152.585C500.937 158.451 504.359 167.176 504.359 178.759ZM466.338 110.39C466.338 103.47 464.157 98.4308 459.795 95.2718C455.508 92.1128 449.002 90.5333 440.277 90.5333H424.708V131.713H441.631C450.13 131.713 456.373 130.021 460.359 126.636C464.345 123.251 466.338 117.836 466.338 110.39ZM472.318 177.969C472.318 169.019 469.836 162.701 464.872 159.015C459.908 155.33 452.913 153.487 443.887 153.487H424.708V200.872H442.533C451.409 200.872 458.591 199.255 464.082 196.021C469.573 192.711 472.318 186.694 472.318 177.969ZM619.064 101.251C622.675 101.251 625.946 101.552 628.88 102.154C631.888 102.68 634.859 103.47 637.793 104.523L632.49 151.118H612.634V127.764C605.037 128.366 598.381 131.788 592.664 138.031C587.023 144.274 582.548 152.735 579.239 163.415V203.354H603.044V224H532.644V203.354H549.454V125.056H532.644V104.523H572.131L577.659 131.938C582.097 121.634 587.625 113.962 594.244 108.923C600.938 103.809 609.211 101.251 619.064 101.251ZM716.508 101.138C728.242 101.138 738.283 103.733 746.631 108.923C754.98 114.038 761.298 121.333 765.585 130.81C769.948 140.212 772.129 151.268 772.129 163.979C772.129 176.916 769.948 188.161 765.585 197.713C761.223 207.19 754.83 214.523 746.406 219.713C738.057 224.827 728.054 227.385 716.395 227.385C704.662 227.385 694.621 224.865 686.272 219.826C677.924 214.786 671.568 207.528 667.206 198.051C662.843 188.574 660.662 177.292 660.662 164.205C660.662 151.72 662.843 140.738 667.206 131.262C671.643 121.709 678.036 114.301 686.385 109.036C694.809 103.771 704.85 101.138 716.508 101.138ZM716.508 123.59C708.084 123.59 701.842 126.899 697.78 133.518C693.719 140.062 691.688 150.291 691.688 164.205C691.688 178.27 693.719 188.574 697.78 195.118C701.842 201.662 708.047 204.933 716.395 204.933C724.744 204.933 730.949 201.662 735.011 195.118C739.072 188.499 741.103 178.12 741.103 163.979C741.103 150.215 739.072 140.062 735.011 133.518C730.949 126.899 724.782 123.59 716.508 123.59ZM917.521 104.523L899.244 224H864.27L852.198 141.077L839.337 224H805.039L785.973 104.523H813.952L824.332 205.497L839.111 119.641H866.526L880.065 205.497L890.67 104.523H917.521ZM983.037 205.385C990.182 205.385 995.823 204.181 999.96 201.774C1004.17 199.292 1006.28 195.832 1006.28 191.395C1006.28 188.311 1005.56 185.791 1004.13 183.836C1002.71 181.88 999.96 180.038 995.899 178.308C991.912 176.503 985.858 174.509 977.734 172.328C969.461 170.222 962.541 167.74 956.975 164.882C951.41 161.949 947.085 158.188 944.001 153.6C940.917 148.937 939.375 143.221 939.375 136.451C939.375 129.532 941.331 123.402 945.242 118.062C949.228 112.721 954.945 108.585 962.391 105.651C969.912 102.643 978.787 101.138 989.017 101.138C1007.22 101.138 1022.75 105.802 1035.61 115.128L1023.43 133.292C1012.52 126.373 1001.28 122.913 989.693 122.913C976.305 122.913 969.611 126.749 969.611 134.421C969.611 137.053 970.401 139.234 971.981 140.964C973.635 142.694 976.456 144.349 980.442 145.928C984.504 147.508 990.709 149.463 999.058 151.795C1007.63 154.202 1014.63 156.834 1020.04 159.692C1025.53 162.55 1029.78 166.349 1032.79 171.087C1035.87 175.826 1037.42 181.88 1037.42 189.251C1037.42 197.525 1034.93 204.557 1029.97 210.349C1025.08 216.065 1018.54 220.352 1010.34 223.21C1002.14 225.993 993.078 227.385 983.15 227.385C972.319 227.385 962.654 225.843 954.155 222.759C945.656 219.675 938.322 215.426 932.155 210.01L947.611 192.636C952.5 196.547 957.953 199.668 963.97 202C969.987 204.256 976.343 205.385 983.037 205.385ZM1098.31 173.344C1099.13 184.099 1102.29 192.072 1107.78 197.262C1113.35 202.451 1120.46 205.046 1129.11 205.046C1134.6 205.046 1139.86 204.181 1144.9 202.451C1149.94 200.721 1155.02 198.164 1160.13 194.779L1172.54 211.815C1166.75 216.704 1159.98 220.54 1152.23 223.323C1144.49 226.031 1136.14 227.385 1127.19 227.385C1114.48 227.385 1103.65 224.752 1094.7 219.487C1085.82 214.222 1079.09 206.851 1074.5 197.374C1069.99 187.897 1067.73 176.916 1067.73 164.431C1067.73 152.472 1069.95 141.716 1074.39 132.164C1078.9 122.537 1085.37 114.978 1093.79 109.487C1102.29 103.921 1112.3 101.138 1123.8 101.138C1134.63 101.138 1144.07 103.545 1152.12 108.359C1160.17 113.173 1166.37 120.13 1170.74 129.231C1175.1 138.256 1177.28 149.012 1177.28 161.497C1177.28 165.785 1177.09 169.733 1176.72 173.344H1098.31ZM1123.92 122.123C1116.47 122.123 1110.45 124.793 1105.87 130.133C1101.35 135.398 1098.72 143.446 1097.97 154.277H1148.29C1148.14 143.973 1145.99 136.038 1141.86 130.472C1137.79 124.906 1131.81 122.123 1123.92 122.123ZM1295.82 101.251C1299.43 101.251 1302.7 101.552 1305.64 102.154C1308.65 102.68 1311.62 103.47 1314.55 104.523L1309.25 151.118H1289.39V127.764C1281.79 128.366 1275.14 131.788 1269.42 138.031C1263.78 144.274 1259.31 152.735 1256 163.415V203.354H1279.8V224H1209.4V203.354H1226.21V125.056H1209.4V104.523H1248.89L1254.42 131.938C1258.85 121.634 1264.38 113.962 1271 108.923C1277.7 103.809 1285.97 101.251 1295.82 101.251ZM1584.35 172.328C1584.35 183.084 1582.17 192.636 1577.81 200.985C1573.52 209.258 1567.16 215.726 1558.74 220.39C1550.32 225.053 1540.2 227.385 1528.39 227.385C1516.43 227.385 1506.28 225.091 1497.93 220.503C1489.58 215.915 1483.26 209.484 1478.98 201.21C1474.76 192.937 1472.66 183.309 1472.66 172.328V67.9692H1503.57V163.641C1503.57 172.817 1504.36 180.301 1505.94 186.092C1507.52 191.884 1510.12 196.246 1513.73 199.179C1517.34 202.113 1522.22 203.579 1528.39 203.579C1534.56 203.579 1539.45 202.113 1543.06 199.179C1546.74 196.246 1549.38 191.884 1550.96 186.092C1552.54 180.301 1553.33 172.817 1553.33 163.641V67.9692H1584.35V172.328ZM1659.79 205.385C1666.94 205.385 1672.58 204.181 1676.72 201.774C1680.93 199.292 1683.04 195.832 1683.04 191.395C1683.04 188.311 1682.32 185.791 1680.89 183.836C1679.46 181.88 1676.72 180.038 1672.66 178.308C1668.67 176.503 1662.62 174.509 1654.49 172.328C1646.22 170.222 1639.3 167.74 1633.73 164.882C1628.17 161.949 1623.84 158.188 1620.76 153.6C1617.68 148.937 1616.13 143.221 1616.13 136.451C1616.13 129.532 1618.09 123.402 1622 118.062C1625.99 112.721 1631.7 108.585 1639.15 105.651C1646.67 102.643 1655.55 101.138 1665.77 101.138C1683.98 101.138 1699.51 105.802 1712.37 115.128L1700.18 133.292C1689.28 126.373 1678.03 122.913 1666.45 122.913C1653.06 122.913 1646.37 126.749 1646.37 134.421C1646.37 137.053 1647.16 139.234 1648.74 140.964C1650.39 142.694 1653.21 144.349 1657.2 145.928C1661.26 147.508 1667.47 149.463 1675.82 151.795C1684.39 154.202 1691.38 156.834 1696.8 159.692C1702.29 162.55 1706.54 166.349 1709.55 171.087C1712.63 175.826 1714.17 181.88 1714.17 189.251C1714.17 197.525 1711.69 204.557 1706.73 210.349C1701.84 216.065 1695.3 220.352 1687.1 223.21C1678.9 225.993 1669.84 227.385 1659.91 227.385C1649.08 227.385 1639.41 225.843 1630.91 222.759C1622.41 219.675 1615.08 215.426 1608.91 210.01L1624.37 192.636C1629.26 196.547 1634.71 199.668 1640.73 202C1646.75 204.256 1653.1 205.385 1659.79 205.385ZM1775.06 173.344C1775.89 184.099 1779.05 192.072 1784.54 197.262C1790.11 202.451 1797.21 205.046 1805.86 205.046C1811.35 205.046 1816.62 204.181 1821.66 202.451C1826.7 200.721 1831.78 198.164 1836.89 194.779L1849.3 211.815C1843.51 216.704 1836.74 220.54 1828.99 223.323C1821.25 226.031 1812.9 227.385 1803.95 227.385C1791.24 227.385 1780.4 224.752 1771.45 219.487C1762.58 214.222 1755.85 206.851 1751.26 197.374C1746.75 187.897 1744.49 176.916 1744.49 164.431C1744.49 152.472 1746.71 141.716 1751.15 132.164C1755.66 122.537 1762.13 114.978 1770.55 109.487C1779.05 103.921 1789.05 101.138 1800.56 101.138C1811.39 101.138 1820.83 103.545 1828.88 108.359C1836.93 113.173 1843.13 120.13 1847.5 129.231C1851.86 138.256 1854.04 149.012 1854.04 161.497C1854.04 165.785 1853.85 169.733 1853.47 173.344H1775.06ZM1800.67 122.123C1793.23 122.123 1787.21 124.793 1782.62 130.133C1778.11 135.398 1775.48 143.446 1774.73 154.277H1825.04C1824.89 143.973 1822.75 136.038 1818.61 130.472C1814.55 124.906 1808.57 122.123 1800.67 122.123Z" fill="black"/>
7 | </svg>
8 | 


--------------------------------------------------------------------------------
/docs/mint.json:
--------------------------------------------------------------------------------
 1 | {
 2 |   "$schema": "https://mintlify.com/schema.json",
 3 |   "name": "Browser Use",
 4 |   "logo": {
 5 |     "dark": "/logo/dark.svg",
 6 |     "light": "/logo/light.svg",
 7 |     "href": "https://browser-use.com"
 8 |   },
 9 |   "favicon": "/favicon.svg",
10 |   "colors": {
11 |     "primary": "#F97316",
12 |     "light": "#FFF7ED",
13 |     "dark": "#C2410C",
14 |     "anchors": {
15 |       "from": "#F97316",
16 |       "to": "#FB923C"
17 |     },
18 |     "background": {
19 |       "dark": "#0D0A09"
20 |     }
21 |   },
22 |   "feedback": {
23 |     "thumbsRating": true,
24 |     "raiseIssue": true,
25 |     "suggestEdit": true
26 |   },
27 |   "topbarLinks": [
28 |     {
29 |       "name": "Github",
30 |       "url": "https://github.com/browser-use/browser-use"
31 |     },
32 |     {
33 |       "name": "Twitter",
34 |       "url": "https://x.com/gregpr07"
35 |     }
36 |   ],
37 |   "topbarCtaButton": {
38 |     "name": "Join Discord",
39 |     "url": "https://link.browser-use.com/discord"
40 |   },
41 |   "tabs": [
42 |     {
43 |       "name": "Cloud API",
44 |       "url": "cloud",
45 |       "openapi": "https://api.browser-use.com/openapi.json"
46 |     }
47 |   ],
48 |   "navigation": [
49 |     {
50 |       "group": "Get Started",
51 |       "pages": ["introduction", "quickstart"]
52 |     },
53 |     {
54 |       "group": "Customize",
55 |       "pages": [
56 |         "customize/supported-models",
57 |         "customize/agent-settings",
58 |         "customize/browser-settings",
59 |         "customize/real-browser",
60 |         "customize/output-format",
61 |         "customize/system-prompt",
62 |         "customize/sensitive-data",
63 |         "customize/custom-functions",
64 |         "customize/hooks"
65 |       ]
66 |     },
67 |     {
68 |       "group": "Development",
69 |       "pages": [
70 |         "development/contribution-guide",
71 |         "development/local-setup",
72 |         "development/telemetry",
73 |         "development/observability",
74 |         "development/evaluations",
75 |         "development/roadmap"
76 |       ]
77 |     },
78 |     {
79 |       "group": "Cloud API",
80 |       "pages": ["cloud/quickstart", "cloud/implementation"]
81 |     }
82 |   ],
83 |   "footerSocials": {
84 |     "x": "https://x.com/gregpr07",
85 |     "github": "https://github.com/browser-use/browser-use",
86 |     "linkedin": "https://linkedin.com/company/browser-use"
87 |   }
88 | }
89 | 


--------------------------------------------------------------------------------
/docs/quickstart.mdx:
--------------------------------------------------------------------------------
 1 | ---
 2 | title: "Quickstart"
 3 | description: "Start using Browser Use with this quickstart guide"
 4 | icon: "rocket"
 5 | ---
 6 | 
 7 | {/* You can install Browser Use from PyPI or clone it from Github. */}
 8 | 
 9 | ## Prepare the environment
10 | 
11 | Browser Use requires Python 3.11 or higher.
12 | 
13 | First, we recommend using [uv](https://docs.astral.sh/uv/) to setup the Python environment.
14 | 
15 | ```bash
16 | uv venv --python 3.11
17 | ```
18 | 
19 | and activate it with:
20 | 
21 | ```bash
22 | # For Mac/Linux:
23 | source .venv/bin/activate
24 | 
25 | # For Windows:
26 | .venv\Scripts\activate
27 | ```
28 | 
29 | Install the dependencies:
30 | 
31 | ```bash
32 | uv pip install browser-use
33 | ```
34 | 
35 | Then install patchright:
36 | 
37 | ```bash
38 | uv run patchright install
39 | ```
40 | 
41 | ## Create an agent
42 | 
43 | Then you can use the agent as follows:
44 | 
45 | ```python agent.py
46 | from langchain_openai import ChatOpenAI
47 | from browser_use import Agent
48 | from dotenv import load_dotenv
49 | load_dotenv()
50 | 
51 | import asyncio
52 | 
53 | llm = ChatOpenAI(model="gpt-4o")
54 | 
55 | async def main():
56 |     agent = Agent(
57 |         task="Compare the price of gpt-4o and DeepSeek-V3",
58 |         llm=llm,
59 |     )
60 |     result = await agent.run()
61 |     print(result)
62 | 
63 | asyncio.run(main())
64 | ```
65 | 
66 | ## Set up your LLM API keys
67 | 
68 | `ChatOpenAI` and other Langchain chat models require API keys. You should store these in your `.env` file. For example, for OpenAI and Anthropic, you can set the API keys in your `.env` file, such as:
69 | 
70 | 
71 | ```bash .env
72 | OPENAI_API_KEY=
73 | ANTHROPIC_API_KEY=
74 | ```
75 | 
76 | For other LLM models you can refer to the [Langchain documentation](https://python.langchain.com/docs/integrations/chat/) to find how to set them up with their specific API keys.
77 | 


--------------------------------------------------------------------------------