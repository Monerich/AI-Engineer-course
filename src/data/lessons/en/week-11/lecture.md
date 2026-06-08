# Week 11: Custom ReAct Agent from Scratch in Python

## Block 1: Tool Registry — architecture of tool registries for custom agents.

Welcome to Week 11: *Custom ReAct Agent from Scratch in Python*. Up until this point, we have relied heavily on pre-built abstractions, LangGraph nodes, and existing visual orchestration layers. However, to ascend to the highest echelons of AI Automation Architecture, you must decouple yourself from these high-level wrappers. Foundational models, despite their impressive reasoning capabilities, remain constrained by their inability to interact with the outside world; tools bridge this critical gap, empowering agents to interact with external data and services while unlocking a wider range of actions. 

As mandated in Phase 3 of the *AI Agent roadmap*, a senior AI Engineer must know how to build the "Tool dispatch" system entirely from scratch, which encompasses the registry, schema validation, parallel calls, recovery, and retries. In this exhaustive, production-grade deep-dive, we will construct the very heart of the ReAct (Reason + Act) paradigm: **The Tool Registry**.

We will engineer an elegant Python decorator (`@tool`) to auto-generate JSON schemas, establishing a robust Agent-Computer Interface (ACI) that dynamically serves capabilities to your language models without drowning them in context bloat.

---

### Deep Theoretical Analysis: The Physics of Tool Registries

Before writing a single line of Python, an AI Architect must deeply understand the mechanics of tool discovery, routing, and schema generation.

#### 1. The Anatomy of Tool Learning
Tool learning constitutes one of the most important components of the action system in AI agents. It involves three key aspects: Tool Discovery (identifying suitable tools), Tool Creation (developing new tools), and Tool Usage (effectively employing tools). 
A Tool Registry is the central nervous system for **Tool Discovery**. When an agent enters its reasoning loop, it must be presented with a manifest of available actions. The registry acts as a dynamic library, mapping human-written Python functions into LLM-readable JSON schemas that the foundational model can understand and invoke.

#### 2. The Agent-Computer Interface (ACI)
When building software for humans, we invest heavily in Graphical User Interfaces (GUIs). When building tools for agents, we must invest heavily in the Agent-Computer Interface (ACI). As Anthropic's engineering team notes, agent-tool interfaces are as critical as human-computer interfaces. 
Your Python code is the backend; the *docstrings, parameter typings, and function names* are the ACI. As explicitly stated in the *AI Engineer roadmap* curriculum, writing descriptions for tools that the model correctly selects across different inputs is a fundamental skill. "Detailed descriptions are the most important factor. 3-4 sentences per tool: what it does, when to use it, limitations". The Tool Registry is responsible for parsing these Python docstrings and translating them into the exact JSON schema the OpenAI or Anthropic SDK demands.

#### 3. Progressive Disclosure and Context Compaction
A naive tool registry simply dumps 500 API integrations into the LLM's system prompt. This is an architectural disaster. As noted in the deployment of advanced tool use, dumping every definition into context upfront is highly inefficient; instead, agents should discover and load tools on-demand, keeping only what's relevant for the current task. 
By utilizing progressive disclosure techniques, such as Anthropic's `defer_loading: true`, architects can cut 85% of token usage for tools, dramatically raising success rates on complex benchmarks. Your Tool Registry must be dynamic, allowing the Orchestrator agent to load subsets of tools (e.g., only "Database Tools" or only "Email Tools") based on the current state of the workflow.

#### 4. Separation of Concerns in Harness Engineering
According to *Lecture 02. Что на самом деле означает harness* (What a harness actually means), the "harness" is the stable environment that grounds a black-box model in reality. The harness is made of five subsystems, one of which is explicitly defined as "Tools: shell / files / tests". The Tool Registry isolates the volatile execution of these scripts from the cognitive reasoning of the LLM. 

---

### ASCII Architecture Schema: Enterprise Tool Dispatch & Registry

The following Directed Acyclic Graph (DAG) illustrates the lifecycle of a Python function as it is wrapped by the registry, converted into an LLM schema, selected by the model, and safely executed.

```ascii
=============================================================================================
 ENTERPRISE TOOL REGISTRY & DISPATCH HARNESS
=============================================================================================

[ 1. DEVELOPER WORKSPACE ]
 @tool(namespace="db_query")
 def fetch_customer_data(user_id: int) -> str:
 """Fetches secure customer data from the Postgres database."""
 |
 v
+-----------------------------------------------------------------------------------------+
| 2. REGISTRY INGESTION LAYER (The Decorator) |
| - Uses `inspect` to extract function signature: `user_id: int`. |
| - Parses docstring for the LLM instruction payload. |
| - Generates strict JSON Schema compliant with OpenAPI/Anthropic tool specs. |
+-----------------------------------------------------------------------------------------+
 |
 v
+-----------------------------------------------------------------------------------------+
| 3. IN-MEMORY TOOL REGISTRY (The Brain's Hands) |
| { |
| "db_query_fetch_customer_data": { |
| "func": <function fetch_customer_data>, |
| "schema": {"type": "function", "function": {"name": "...", "description"...}} |
| } |
| } |
+-----------------------------------------------------------------------------------------+
 | (LLM requests tools) ^ (LLM invokes specific tool)
 v |
[ 4. CONTEXT INJECTION ] [ 5. SECURE DISPATCH & EXECUTION ]
- Registry exports dynamic schema list. - Extracts JSON arguments from LLM.
- LLM reads descriptions via ACI. - Maps arguments back to Python `**kwargs`.
- LLM decides: "I must call the DB tool." - Executes function securely.
 - Returns string result to LLM context.
=============================================================================================
```

---

### Detailed Step-by-Step Practical Guide & Production Code

We will engineer a production-ready `ToolRegistry` class and an `@tool` decorator. This system will fulfill the Phase 3 roadmap mandate: "A tool registry via a Python decorator (@tool) with auto-generated JSON-schema". We will utilize Python's `inspect` and `typing` libraries to dynamically bridge the gap between Python and JSON.

#### Step 1: Architecting the `@tool` Decorator and Type Mapping
First, we must create a utility to map native Python types to JSON Schema types, enabling the LLM to understand exactly what parameters it must generate.

```python
import inspect
import logging
import traceback
from functools import wraps
from typing import Callable, Dict, Any, Type, List

# Lecture 11: Make the agent runtime observable 
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [TOOL_REGISTRY] - %(message)s')

def python_type_to_json_type(py_type: Type) -> str:
 """Maps standard Python types to JSON Schema compliant string types."""
 mapping = {
 int: "integer",
 float: "number",
 str: "string",
 bool: "boolean",
 list: "array",
 dict: "object"
 }
 return mapping.get(py_type, "string") # Fallback to string

class ToolRegistry:
 """
 Enterprise-grade Tool Registry for ReAct Agents.
 Manages schemas, namespaces, and dynamic dispatching.
 """
 def __init__(self):
 # Maps the tool name to a dictionary containing both the callable and its schema
 self._tools: Dict[str, Dict[str, Any]] = {}

 def register(self, namespace: str = None) -> Callable:
 """
 The @tool decorator. Parses the function signature and docstring,
 generating an LLM-ready JSON Schema automatically.
 """
 def decorator(func: Callable) -> Callable:
 # 1. Namespacing: Crucial for organizing tools in large systems 
 tool_name = f"{namespace}_{func.__name__}" if namespace else func.__name__
 
 # 2. Extract Agent-Computer Interface (ACI) instructions from docstring
 description = inspect.getdoc(func)
 if not description:
 raise ValueError(f"Tool '{tool_name}' lacks a docstring. LLMs require explicit descriptions.")
 
 # 3. Parse Signature for JSON Schema
 sig = inspect.signature(func)
 properties = {}
 required = []
 
 for param_name, param in sig.parameters.items():
 if param.annotation == inspect.Parameter.empty:
 raise TypeError(f"Tool '{tool_name}' parameter '{param_name}' lacks type hinting.")
 
 properties[param_name] = {
 "type": python_type_to_json_type(param.annotation),
 # In a highly advanced registry, we would parse Sphinx/Google docstrings for parameter descriptions here
 "description": f"Parameter {param_name} of type {param.annotation.__name__}"
 }
 
 # If there's no default value, it's a required parameter for the LLM
 if param.default == inspect.Parameter.empty:
 required.append(param_name)
 
 # 4. Construct the Standardized OpenAI/Anthropic Tool Schema
 schema = {
 "type": "function",
 "function": {
 "name": tool_name,
 "description": description.strip(),
 "parameters": {
 "type": "object",
 "properties": properties,
 "required": required
 }
 }
 }
 
 # 5. Save to the in-memory registry
 self._tools[tool_name] = {
 "callable": func,
 "schema": schema
 }
 logging.info(f"Successfully registered tool: {tool_name}")
 
 @wraps(func)
 def wrapper(*args, **kwargs):
 return func(*args, **kwargs)
 return wrapper
 
 return decorator

 def get_all_schemas(self) -> List[Dict[str, Any]]:
 """Extracts the schema manifest to inject into the LLM's API call."""
 return [tool_data["schema"] for tool_data in self._tools.values()]

 def dispatch(self, tool_name: str, arguments: Dict[str, Any]) -> str:
 """
 The Execution Layer: Safely executes the requested tool and handles runtime crashes.
 """
 if tool_name not in self._tools:
 return f"Error: Tool '{tool_name}' does not exist in the registry."
 
 func = self._tools[tool_name]["callable"]
 logging.info(f"Dispatching tool '{tool_name}' with args: {arguments}")
 
 try:
 # Safely unpack the JSON arguments generated by the LLM into the Python function
 result = func(**arguments)
 return str(result)
 except Exception as e:
 # We catch exceptions and return them as strings so the LLM can self-heal
 error_msg = f"Tool Execution Failed: {str(e)}\n{traceback.format_exc()}"
 logging.error(error_msg)
 return error_msg
```

#### Step 2: Instantiating the Tools
Now we apply our elegant decorator. By defining specific namespaces, we prevent cognitive overlap for the LLM. "Пространства имён в названиях— db_query, storage_read" (Namespaces in titles — db_query, storage_read) is a recommended best practice.

```python
# Instantiate the global registry
registry = ToolRegistry()

@registry.register(namespace="math")
def calculate_compound_interest(principal: float, rate: float, years: int) -> float:
 """
 Calculates the compound interest for a given principal, rate, and time.
 Use this tool ONLY when the user explicitly asks for investment projections.
 """
 return principal * (1 + rate) ** years

@registry.register(namespace="system")
def read_local_file(filepath: str) -> str:
 """
 Reads the content of a local file.
 Use this tool to extract context from the user's workspace before answering complex queries.
 """
 import os
 if not os.path.exists(filepath):
 raise FileNotFoundError(f"The path {filepath} is invalid.")
 with open(filepath, 'r') as f:
 return f.read()

# Demonstrating how the ReAct Orchestrator accesses the registry
if __name__ == "__main__":
 print("\n--- LLM SCHEMAS GENERATED ---")
 schemas = registry.get_all_schemas()
 for s in schemas:
 print(s)
 
 print("\n--- DISPATCHING SIMULATED LLM CALL ---")
 # Simulating the JSON payload returned by an LLM
 llm_tool_choice = "math_calculate_compound_interest"
 llm_arguments = {"principal": 1000.0, "rate": 0.05, "years": 10}
 
 result = registry.dispatch(llm_tool_choice, llm_arguments)
 print(f"Tool Result: {result}")
```

In this architecture, your ReAct agent no longer manually parses strings or manages imports. It simply calls `registry.get_all_schemas()` and passes it to the `tools=` parameter of the API SDK. When the LLM decides to act, the Python orchestrator routes the generated JSON back into `registry.dispatch()`, completely abstracting away the execution complexities.

---

### Realistic Business Applications & Unit Economics

A dynamic tool registry is the defining mechanism that transforms a "chatbot" into a scalable, enterprise AI employee capable of orchestrating real business logic.

**1. Secure Enterprise ERP & CRM Integrations**
A logistics company builds an agent to manage inventory tracking across Salesforce and a custom SQL database. If the agent's prompt simply says "update the database", the agent will fail catastrophically. By using a strict `@tool(namespace="salesforce")` registry, the AI Architect creates isolated, safe Python functions that wrap the underlying APIs. The agent receives a crisp JSON Schema defining exact parameters (`lead_id`, `new_status`). This guarantees that the AI cannot invent random database commands, ensuring data integrity while automating thousands of hours of manual CRM updates. 

**2. Dynamic Context Management & Token Efficiency**
In a multi-agent system analyzing legal contracts, giving an agent access to 500 potential tools (e.g., fetching from Slack, searching Google, querying Notion, checking Wikipedia) consumes tens of thousands of input tokens just to describe the tools. At $3.00 per 1M input tokens, this rapidly burns budget. A programmatic `ToolRegistry` allows the orchestrator to implement "Progressive Disclosure". The Orchestrator agent dynamically calls `registry.get_schemas(namespace="legal_search_only")`, loading only 5 tools into context instead of 500. As Anthropic notes, `defer_loading` and smart tool selection cuts token usage by 85% and raises benchmark accuracy significantly.

---

### Edge-Cases, Common Errors, Rate Limits, and Debugging Loops

Implementing tool registries introduces unique cognitive and systematic failure modes that must be aggressively managed.

> [!CAUTION] 
> **Instruction Bloat and Tool Overlap** 
> **The Problem:** You register 15 different tools that all sound vaguely similar: `search_web`, `google_search`, `fetch_url`, and `find_online`. When the LLM enters its ReAct loop, it becomes cognitively confused about which tool to use. Bad tool descriptions can send agents down completely wrong paths. 
> **Harness Mitigation:** Implement strict boundaries and specific Negative Prompts within your docstrings. For example: `"""Use this tool ONLY to search internal Confluence docs. Do NOT use this tool for public web searches."""` Anthropic emphasizes that tools should have minimal overlap in functionality and should be extremely clear with respect to their intended use.

> [!WARNING] 
> **The Exception Swallowing Trap (Blind Wandering)** 
> **The Error:** Inside your `dispatch` method, an API rate limit triggers an error. Your Python code throws a fatal exception, crashing the entire script, and the agent's reasoning loop is destroyed instantly. 
> **Diagnostic Loop:** As implemented in our `dispatch` code block, **never let a tool crash the agent.** Catch the Python exception and return the error trace as a *string* back to the LLM. This enables the **Self-Healing Loop**. The LLM reads the observation: *"Tool Execution Failed: Missing required parameter 'API_KEY'"*, reflects on its mistake, and autonomously calls the tool again with the correct parameters.

> [!NOTE] 
> **Parameter Hallucinations and Type Safety** 
> **The Problem:** The LLM decides to call `calculate_compound_interest`, but instead of passing `10` for the `years` parameter, it passes `"ten years"` (a string). Python's `**kwargs` unpacking immediately fails because the math operation cannot multiply by a string. 
> **Solution:** Rely strictly on the `python_type_to_json_type` parser to enforce strict Pydantic/JSON schemas. If you are using the modern OpenAI SDK's `Strict Structured Outputs`, the API will mathematically guarantee that the types match your schema before the payload ever reaches your Python registry, entirely eliminating data-type hallucinations.

By mastering the Tool Registry, you have built the "hands" of your artificial brain. You have learned to map deterministic Python code into probabilistic LLM schemas smoothly and safely, establishing the cornerstone of the autonomous ReAct framework.

Does this setup make sense? We can move on to Block 2, where we will build the actual `while` loop that connects this registry to the LLM's reasoning engine, if you are ready to proceed.

---

## Block 2: Search APIs Tools — Tavily and SerpAPI integration as agent search tools.

Welcome to Block 2 of Week 11. In the previous block, we architected the central nervous system of our custom ReAct agent: the Tool Registry. You learned how to bridge the gap between probabilistic reasoning and deterministic Python code by dynamically auto-generating JSON schemas from docstrings. However, an agent with a flawless registry but no actual tools is merely an isolated brain floating in a vacuum, forever trapped behind its training data cutoff date.

To become genuinely autonomous and economically valuable, an agent must perceive the live state of the world. "Tools are critical for bridging the divide between the agent's internal capabilities and the external world, facilitating interaction with external data and services". According to the Phase 3 guidelines in the *AI Agent roadmap*, a core mandate for a custom agent is integrating tools like "web_search via Tavily or Firecrawl". 

In this exhaustive, production-grade deep dive, we will populate your Tool Registry with its first set of eyes and ears: **Agentic Web Search APIs**. We will rigorously analyze the architectural differences between raw search extraction (SerpAPI) and LLM-optimized synthesis (Tavily), implement the "Web Access Pattern", and engineer the precise cognitive heuristics required to stop your agents from hallucinating search queries or falling into infinite browsing loops.

---

### Deep Theoretical Analysis: The Physics of Agentic Web Search

Giving an LLM access to the internet is not as simple as attaching a search bar. Human beings search the web iteratively: we glance at titles, scan snippets, click, hit the back button, and refine our terms. When an LLM executes a search, it must ingest the entire payload into its context window instantly. This requires a highly deliberate architectural approach.

#### 1. The Web Access Pattern
The integration of search tools into an agent's workflow is formally known as the *Web Access Pattern*. "The Web Access Pattern is an agentic workflow designed to streamline the retrieval, processing, and summarization of web content". In this pattern, the orchestrator model formulates search queries, dispatches them to external APIs, and parses the structured data. "The workflow is initiated by a WebSearchAgent, which takes user input and formulates optimized search queries using language models. These queries are then executed using the SERP API to retrieve Google Search results". 

#### 2. Raw SERP (SerpAPI) vs. Synthesized Retrieval (Tavily)
As an AI Architect, you must choose the right search engine for the right cognitive task:
* **SerpAPI (The Raw Approach):** SerpAPI returns a literal, high-fidelity JSON representation of a Google Search Engine Results Page (SERP). It includes organic results, paid ads, knowledge graphs, and pagination metadata. Early agentic implementations, such as the classic ReAct agent built with LangChain, relied heavily on this. "ReAct makes a chain of five searches... scraping Google search results to figure out the band names". However, feeding raw SERP JSON into an LLM often causes massive Context Bloat. 
* **Tavily (The LLM-Optimized Approach):** Tavily is built specifically for AI agents. Instead of returning raw search page mechanics, it fetches the URLs, scrapes the actual page content under the hood, and returns clean, condensed markdown or synthesized text directly optimized for an LLM's context window. "Your instructions are to always use the Tavly search tool to find accurate information... for real-time web search". 

#### 3. Cognitive Search Heuristics: "Start Wide, Then Narrow Down"
A naive implementation of a search tool will result in the agent making terrible search queries. Anthropic’s engineering team discovered that "agents often default to overly long, specific queries that return few results". If an agent is trying to find the release date of a specific software patch, it might search for `"Exact release date of firmware v2.1.4 for enterprise router XYZ in Q3 2026"`, yielding zero results. 
To counteract this, the ACI (Agent-Computer Interface) docstring of your search tool must enforce human-like research strategies. "Search strategy should mirror expert human research: explore the landscape before drilling into specifics... We counteracted this tendency by prompting agents to start with short, broad queries, evaluate what's available, then progressively narrow focus".

#### 4. Delegating Search to Avoid Redundancy
When building systems where multiple agents search the web simultaneously, you must clearly define their boundaries. "Without detailed task descriptions, agents duplicate work, leave gaps, or fail to find necessary information". For example, if you ask a multi-agent system to research semiconductor supply chains, without strict tool rules, multiple subagents will likely submit the exact same search query to Tavily, wasting API credits and polluting the final output with duplicated context.

---

### ASCII Architecture Schema: The Agentic Web Search Dispatch

The following Directed Acyclic Graph (DAG) demonstrates the cognitive flow and execution boundaries of an agent performing autonomous web research using our custom Tool Registry.

```ascii
=============================================================================================
 ENTERPRISE WEB ACCESS PATTERN (TOOL DISPATCH)
=============================================================================================

[ 1. ORCHESTRATOR AGENT (ReAct Loop) ]
 Thought: "I need to find the current trends in AI agents for 2026."
 Action: {"name": "search_tavily", "arguments": {"query": "AI agent trends 2026", "depth": "advanced"}}
 |
 v
+-----------------------------------------------------------------------------------------+
| 2. TOOL REGISTRY DISPATCH (Harness Layer) |
| - Intercepts LLM intent. |
| - Validates JSON arguments. |
| - Injects hidden API Keys (Secret Broking). |
+-----------------------------------------------------------------------------------------+
 |
 +---------------------+---------------------+
 | |
[ 3A. SERP_API TOOL ] [ 3B. TAVILY_SEARCH TOOL ]
- Best for: "What is the price of X?" - Best for: "Explain the architecture of Y."
- Executes `requests.get()` to Google. - Executes `requests.post()` to Tavily.
- Returns raw organic snippets. - Returns synthesized markdown from 5+ pages.
 | |
 +---------------------+---------------------+
 |
 v
+-----------------------------------------------------------------------------------------+
| 4. OBSERVATION & VERIFICATION LAYER |
| - Truncates payload if > 10,000 tokens to protect context limit. |
| - Returns stringified observation back to the Agent. |
+-----------------------------------------------------------------------------------------+
 |
 v
[ 5. AGENT REFLECTION ] -> Thought: "I have the broad trends. Now I must narrow down 
 my search to multi-agent architectures."
 Action: {"name": "search_tavily", "arguments": {...}}
=============================================================================================
```

---

### Detailed Step-by-Step Practical Guide & Production Code

We will now implement the Python execution scripts for both Tavily and SerpAPI, registering them securely into the `ToolRegistry` we built in Block 1. 

> [!NOTE]
> **Secret Broking Reminder:** Notice how the `context` dictionary is passed into the functions. As we established, "Auth and secret broking... Credentials never enter the context" [327, derived from standard harness principles]. The LLM will only generate the `query` argument; the Python Harness injects the API key.

#### Step 1: Implementing the Tavily Deep Search Tool
Tavily allows us to perform "Advanced" searches, which scrape underlying pages and return substantive content, drastically reducing the number of iterative steps the agent must take. 

```python
import requests
import logging
import json
from typing import Dict, Any

# Assuming `registry` is our instantiated ToolRegistry from Block 1
# from core.registry import registry

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SEARCH_HARNESS] - %(message)s')

@registry.register(namespace="research")
def search_tavily(query: str, search_depth: str, context: Dict[str, Any]) -> str:
 """
 Executes an LLM-optimized web search using the Tavily API.
 
 Use this tool when you need comprehensive, synthesized information, explanations, 
 or deep research on a topic. 
 
 CRITICAL SEARCH HEURISTICS:
 - Start wide, then narrow down. Use short, broad queries first.
 - Do NOT write overly long, specific queries (e.g. avoid full sentences).:param query: The search query string (e.g., 'multi-agent orchestration frameworks 2026').:param search_depth: Must be either 'basic' (fast) or 'advanced' (deep scraping).
 """
 api_key = context.get("TAVILY_API_KEY")
 if not api_key:
 return "System Error: TAVILY_API_KEY is missing from execution context."

 if search_depth not in ["basic", "advanced"]:
 return "Validation Error: search_depth must be 'basic' or 'advanced'. Please retry."

 logging.info(f"Executing Tavily '{search_depth}' search for: {query}")
 
 url = "[Ссылка](https://api.tavily.com/search")
 payload = {
 "api_key": api_key,
 "query": query,
 "search_depth": search_depth,
 "include_answer": True,
 "max_results": 5
 }
 
 try:
 response = requests.post(url, json=payload, timeout=15.0)
 response.raise_for_status()
 data = response.json()
 
 # We extract the pre-synthesized answer and the core content of the results
 observation = f"--- TAVILY SYNTHESIS ---\n{data.get('answer', 'No synthesis available.')}\n\n"
 observation += "--- SOURCE CONTENT ---\n"
 
 for idx, result in enumerate(data.get("results", [])):
 observation += f"[{idx+1}] Title: {result.get('title')}\nURL: {result.get('url')}\nContent: {result.get('content')}\n\n"
 
 return observation

 except requests.exceptions.RequestException as e:
 logging.error(f"Tavily Network Failure: {e}")
 return f"Network Error during search: {str(e)}. If this persists, try another tool."
```

#### Step 2: Implementing the SerpAPI (Raw Google Search) Tool
SerpAPI is essential when the agent needs hyper-specific, real-time facts, navigational queries, or data hidden in Google's Knowledge Graph (like current stock prices or weather snippets) rather than long articles. 

```python
@registry.register(namespace="lookup")
def search_google_serp(query: str, context: Dict[str, Any]) -> str:
 """
 Executes a raw Google Search using SerpAPI.
 
 Use this tool for factual lookups, navigational queries, finding specific URLs, 
 or when you need exact numerical data (like stock prices, dates, or basic facts).
 Do NOT use this tool for deep research or explanations.:param query: The search query string.
 """
 api_key = context.get("SERPAPI_API_KEY")
 if not api_key:
 return "System Error: SERPAPI_API_KEY is missing from execution context."

 logging.info(f"Executing Google SERP search for: {query}")
 
 url = "[Ссылка](https://serpapi.com/search")
 params = {
 "q": query,
 "api_key": api_key,
 "engine": "google",
 "num": 5 # Limit to 5 results to prevent context window explosion
 }
 
 try:
 response = requests.get(url, params=params, timeout=10.0)
 response.raise_for_status()
 data = response.json()
 
 # We must aggressively parse the JSON to protect the agent's context window
 observation = ""
 
 # 1. Capture Knowledge Graph/Answer Box if Google provided one directly
 if "answer_box" in data:
 observation += f"[DIRECT ANSWER]: {data['answer_box'].get('answer', data['answer_box'].get('snippet'))}\n\n"
 
 # 2. Extract organic snippets
 observation += "--- ORGANIC RESULTS ---\n"
 for idx, res in enumerate(data.get("organic_results", [])):
 observation += f"[{idx+1}] Title: {res.get('title')}\nLink: {res.get('link')}\nSnippet: {res.get('snippet')}\n\n"
 
 if not observation.strip():
 return "Search returned no meaningful results. Try broadening your query."
 
 return observation

 except requests.exceptions.RequestException as e:
 logging.error(f"SerpAPI Network Failure: {e}")
 return f"Network Error during search: {str(e)}."
```

#### Step 3: Integrating with the Orchestrator
When the LLM triggers these tools, the registry dynamically injects the API keys. 

```python
# Simulated Execution (Within the Harness Loop)
hidden_context = {
 "TAVILY_API_KEY": "tvly-secret-token",
 "SERPAPI_API_KEY": "serp-secret-token"
}

# The LLM generates a JSON action aiming to find broad trends
llm_action = "research_search_tavily"
llm_args = '{"query": "Latest breakthroughs in Agentic Workflows", "search_depth": "advanced"}'

# Dispatch
print("Agent is thinking...")
result = registry.execute(tool_name=llm_action, raw_arguments=llm_args, hidden_context=hidden_context)

# The result string is then appended to the LLM's message history for the next 'Read' cycle.
```

By providing both `research_search_tavily` and `lookup_search_google_serp`, we empower the agent to make intelligent routing decisions based on the *intent* of the user's prompt. "Bad tool descriptions can send agents down completely wrong paths, so each tool needs a distinct purpose and a clear description".

---

### Realistic Business Applications & Unit Economics

Agentic search transforms large language models from static conversationalists into dynamic, real-time autonomous workers capable of replacing entire research departments.

**1. The Multi-Agent Deep Research System**
In high-tier B2B environments, companies deploy Orchestrator-Worker architectures. "When a user submits a query, the lead agent analyzes it, develops a strategy, and spawns subagents to explore different aspects simultaneously... the subagents act as intelligent filters by iteratively using search tools to gather information". 
For example, a venture capital firm might ask the lead agent: *"Give me an analysis of the top 3 AI agents startups in 2026."* The Orchestrator spawns three separate `WebSearchAgent` instances, passing the Tavily tool to each. Agent A investigates Company 1, Agent B investigates Company 2, and Agent C investigates Company 3. They execute their `search_tavily` tools in parallel, synthesize the Markdown, and return condensed findings to the Orchestrator. This parallelization cuts a 20-minute manual research task down to 45 seconds.

**2. Automated B2B Lead Enrichment pipelines**
As highlighted in no-code automation tutorials, agentic scraping is highly lucrative. "We just scraped a series of web pages for a business... return any new lines as \n... use all the website and information about the provided person to create three interesting points". 
Instead of paying a human SDR (Sales Development Representative) to Google a prospect, an AI agent utilizes the SerpAPI tool to find the prospect's LinkedIn and company page. It then uses a scraping tool (like Firecrawl) to read the page, and synthesizes a highly personalized cold-email icebreaker. This is a fully autonomous, 24/7 lead generation factory that costs roughly $0.02 per lead in API fees.

---

### Edge-Cases, Common Errors, Rate Limits, and Debugging Loops

Connecting probabilistic models to the live internet is fraught with edge cases that will rapidly destroy your pipeline if unhandled.

> [!CAUTION] 
> **The Context Window Explosion (Context Bloat)** 
> **The Error:** A junior developer implements a search tool that blindly dumps the entire raw HTML of five web pages directly into the agent's message history. "The structured nature of JSON, while beneficial for parsing... requires significantly more tokens than plain text, leading to increased processing time and higher costs. Furthermore, JSON's verbosity can easily consume the entire output window". The agent immediately hits the `128k` token limit and crashes with an `OverLimit` exception. 
> **Harness Mitigation:** You must implement *Context Compaction* within the tool itself. As demonstrated in our Python code, we do not return the raw JSON from SerpAPI. We iterate through the dictionary and extract *only* the `title`, `link`, and `snippet`. By compressing the payload *before* returning it as an observation to the LLM, we save thousands of tokens.

> [!WARNING] 
> **The Doom Loop of Redundant Queries** 
> **The Problem:** The agent searches for `"What is the capital of France?"`. Due to a network glitch, SerpAPI returns an empty array. The agent thinks: *"I must try again,"* and submits the exact same query `"What is the capital of France?"` 50 times in a row, draining your API budget. 
> **Diagnostic Loop:** As stated in the guidelines: "Без наблюдаемости агенты принимают решения в условиях неопределённости... ретраи превращаются в слепое блуждание" (Without observability, agents make decisions in uncertainty... retries turn into blind wandering). To break the loop, your tool must explicitly guide the agent in its error string. Instead of returning `""` (empty string), the tool must return: `"Observation: Search returned 0 results. Do NOT repeat the exact same query. You must broaden your search terms or use a different tool."` The agent reads this observation and dynamically shifts its strategy.

> [!NOTE] 
> **Handling HTTP 429 Rate Limits Gracefully** 
> If you spawn 10 sub-agents that all hit the Tavily API simultaneously, the provider will return `HTTP 429 Too Many Requests`. Because we wrapped our execution in `try... except requests.exceptions.RequestException`, the Python script does not crash. It returns the exact error to the agent: `"Network Error: 429 Rate Limit"`. However, to prevent the agent from blindly retrying and failing again, the architecture *should* incorporate the `@retry_with_backoff` decorator we engineered in Week 9, forcing the Python execution layer to autonomously sleep and heal the rate limit *before* returning control to the impatient LLM.

By engineering these two distinct search tools—one for deep synthesis and one for raw factual lookup—you have solved the "Blind Brain" problem. Your ReAct agent can now perceive the live world, formulate expert search strategies, and navigate the internet autonomously without overflowing its memory.

Are you ready to proceed to Block 3, where we will give the agent the power to modify its environment by interacting directly with the local Operating System and Filesystem?

---

## Block 3: File Actions Tools — reading, writing, and editing files inside safe directory bounds.

Welcome to Block 3 of Week 11. In the previous blocks, you engineered a robust `ToolRegistry` and equipped your ReAct agent with Web Access patterns to perceive the live internet. Your agent now possesses a dynamic brain and eyes to see the world. However, a purely observational agent is economically useless; to generate true business value, the agent must be able to permanently alter its environment. It needs hands. 

As explicitly mandated by the *AI Agent roadmap* Phase 3 curriculum, a production-grade custom ReAct agent requires specific primitive tools: "Три инструмента: web_search через Tavily или Firecrawl, read_file, write_file". Without the ability to read and write to the filesystem, an agent is trapped in a transient, ephemeral chat window.

In this exhaustive, production-grade deep dive, we will transition your AI architecture from a read-only chatbot into an autonomous worker capable of persistent file manipulation. We will architect `FilesystemMiddleware` equivalents, implement the "Filesystem Offload" memory pattern, enforce cryptographic-level directory sandboxing to prevent rogue agents from deleting your root system files, and resolve the notorious context bloat issues associated with file reading.

---

### Deep Theoretical Analysis: The Physics of the Agentic Filesystem

Before writing Python `os` module wrappers, an AI Automation Architect must deeply understand the role of the filesystem within a cognitive architecture. The filesystem is not just a storage medium; it is the agent's long-term memory, its collaborative workspace, and its primary defense against token limits.

#### 1. The Repository as the Single Source of Truth
An agent operates in a state of sensory deprivation. As established in *Лекция 03. Сделайте репозиторий своим единственным источником истины* (Lecture 03: Make the repository your single source of truth), "Для агента информация, которой нет в репозитории, попросту не существует. Это инженер, запертый внутри репозитория — что снаружи, он не знает". The repository acts as the "system of record". 
By giving the agent `read_file` and `write_file` tools, you allow it to externalize its thoughts, read project documentation, and permanently store outputs. "Agents can write intermediate results to files, enabling them to resume work and track progress".

#### 2. Durable Execution and the Shared Ledger
In complex, long-running multi-agent systems, agents "produce millions of tokens over a long task so the filesystem durably captures work to track progress over time". 
When you have an Orchestrator agent delegating tasks to a Coder sub-agent and a QA sub-agent, they cannot communicate via telepathy. The filesystem acts as a shared ledger. The Coder agent writes a Python script to `workspace/app.py`. The QA agent then uses the `read_file` tool to ingest `workspace/app.py`, analyzes it, and writes an error log to `workspace/errors.log`. "For multiple agents working together, the filesystem also acts as a shared ledger of work where agents can collaborate". 

#### 3. The "Filesystem Offload" Pattern
Context window management is the most critical economic skill for an AI Engineer. Dumping entire databases or massive PDFs into the LLM's system prompt will cause a catastrophic Context Window Explosion. The *AI Agent roadmap* demands a strict solution: "Filesystem offload: любой результат инструмента >20K токенов пишется в./workspace/<id>.txt, в контексте остается путь и preview из 10 строк". 
When an agent reads or writes massive amounts of data, the actual text must remain on the disk. The ReAct observation returned to the model should only contain the filepath and a tiny metadata preview. This keeps the active context window highly compressed, fast, and cheap. "FilesystemMiddleware: file-based context on/offloading and long-term memory".

#### 4. Safe Bounding and Sandboxing
Giving an LLM unrestricted access to your computer's filesystem is a monumental security vulnerability. A hallucinating agent with an unrestricted `write_file` tool might accidentally attempt to overwrite `/etc/hosts` or delete critical system binaries. Anthropic's engineering guidelines state that "File writes and edits inside the project directory are allowed without a classifier call... [but operations] outside the project directory" must be strictly flagged and blocked. You must enforce a "Chroot Jail" programmatically within your Python tool definitions.

---

### ASCII Architecture Schema: The Secure Filesystem Dispatch

The following Directed Acyclic Graph (DAG) illustrates how the Tool Registry securely intercepts file operations, bounds them to a safe workspace, and implements the Filesystem Offload pattern.

```ascii
=============================================================================================
 ENTERPRISE SECURE FILESYSTEM HARNESS
=============================================================================================

[ 1. ReAct ORCHESTRATOR AGENT ]
Thought: "I need to save the financial analysis to a CSV file."
Action: {"name": "fs_write_file", "arguments": {"filepath": "../../../../etc/passwd", "content": "..."}}
 |
 v
+-----------------------------------------------------------------------------------------+
| 2. TOOL REGISTRY DISPATCH (Python Harness) |
+-----------------------------------------------------------------------------------------+
 |
 v
+-----------------------------------------------------------------------------------------+
| 3. PATH SANITIZATION & BOUNDING MIDDLEWARE |
| - Intercepts proposed path: `../../../../etc/passwd` |
| - Resolves absolute path via `pathlib.Path.resolve()` |
| - Compares against safe boundary: `/var/app/safe_workspace/` |
+-----------------------------------------------------------------------------------------+
 / (Out of Bounds / Path Traversal Hack) \ (Within Safe Bounds)
 v v
[ 4A. SECURITY EXCEPTION ] [ 4B. EXECUTE OS OPERATION ]
- Operation violently blocked. - Executes `os.makedirs` if needed.
- Return to LLM: "CRITICAL SECURITY ERROR: - Writes content to disk.
 Attempted to access directories outside - Returns compressed Observation:
 the secure workspace boundary." "Successfully wrote 25KB to /workspace/file.csv"
=============================================================================================
```

---

### Detailed Step-by-Step Practical Guide & Production Code

We will now implement the three critical filesystem operations (`read_file`, `write_file`, `list_directory`) in pure Python. These tools will be natively registered into the `ToolRegistry` we built in Block 1. They will feature cryptographic-grade directory bounding to prevent Path Traversal attacks.

#### Step 1: Architecting the Secure Workspace Boundary
First, we must define the safe zone. The agent will only be allowed to read and write files within a specific folder named `safe_workspace`.

```python
import os
import logging
from pathlib import Path
from typing import Dict, Any, List

# Assuming `registry` is our instantiated ToolRegistry from Block 1
# from core.registry import registry

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [FS_HARNESS] - %(message)s')

# Define the absolute path of the secure sandboxed directory
BASE_DIR = Path(__file__).parent.resolve()
SECURE_WORKSPACE = BASE_DIR / "safe_workspace"

# Ensure the directory actually exists
SECURE_WORKSPACE.mkdir(parents=True, exist_ok=True)

def _is_path_safe(requested_path: str) -> Path:
 """
 Security Middleware: Resolves the requested path and cryptographically 
 ensures it does not escape the SECURE_WORKSPACE via traversal (e.g., '../../').
 Raises a ValueError if a security breach is detected.
 """
 # 1. Join the requested path to the safe workspace
 target_path = (SECURE_WORKSPACE / requested_path).resolve()
 
 # 2. Check if the resolved target path starts with the absolute safe workspace path
 if not str(target_path).startswith(str(SECURE_WORKSPACE)):
 logging.warning(f"Security Alert: Agent attempted path traversal to {target_path}")
 raise ValueError(
 f"SECURITY BREACH DETECTED: You are strictly forbidden from accessing "
 f"files outside the '/safe_workspace/' directory. Attempted path: {requested_path}"
 )
 return target_path
```

#### Step 2: Implementing the Write Tool (With Auto-Directories)
When an agent attempts to write a file, it often assumes intermediate directories already exist. If an agent writes to `reports/2026/`, the Python tool must gracefully create `reports/2026/` if it does not exist, otherwise the execution will crash.

```python
@registry.register(namespace="fs")
def write_file(filepath: str, content: str) -> str:
 """
 Writes text content to a specified file within the secure workspace.
 If the intermediate directories do not exist, they will be created automatically.
 
 Use this tool to permanently save your work, create scripts, or store data.:param filepath: The relative path and filename (e.g., 'data/').:param content: The full string text content to write into the file.
 """
 try:
 safe_path = _is_path_safe(filepath)
 
 # Create intermediate directories gracefully
 safe_path.parent.mkdir(parents=True, exist_ok=True)
 
 # Write the content
 with open(safe_path, 'w', encoding='utf-8') as f:
 f.write(content)
 
 # Filesystem Offload pattern: Return a compressed observation, NOT the full text
 file_size_kb = len(content.encode('utf-8')) / 1024
 observation = f"SUCCESS: File securely written to {filepath} ({file_size_kb:.2f} KB)."
 logging.info(observation)
 return observation

 except ValueError as ve:
 # Trapped Security Breach
 return str(ve)
 except Exception as e:
 return f"File System Error: Failed to write to {filepath}. Details: {str(e)}"
```

#### Step 3: Implementing the Read Tool (With Context Truncation)
Reading files is dangerous for context windows. If an agent accidentally reads a 50MB log file, the ReAct loop will crash with a Token Limit Exceeded error. We must implement truncation heuristics.

```python
@registry.register(namespace="fs")
def read_file(filepath: str, max_lines: int = 500) -> str:
 """
 Reads the text content of a specified file from the secure workspace.
 
 Use this tool to read documentation, inspect code, or retrieve data.
 To protect your context window, extremely large files will be truncated.:param filepath: The relative path of the file to read (e.g., 'docs/').:param max_lines: The maximum number of lines to read. Default is 500.
 """
 try:
 safe_path = _is_path_safe(filepath)
 
 if not safe_path.exists() or not safe_path.is_file():
 return f"FileNotFoundError: The file '{filepath}' does not exist in the workspace."
 
 with open(safe_path, 'r', encoding='utf-8') as f:
 lines = f.readlines()
 
 total_lines = len(lines)
 
 # Truncation logic to prevent Context Bloat
 if total_lines > max_lines:
 content = "".join(lines[:max_lines])
 warning = f"\n\n[WARNING: File exceeded {max_lines} lines. Content truncated to protect context limits. Total lines in file: {total_lines}]"
 return content + warning
 
 return "".join(lines)

 except ValueError as ve:
 return str(ve)
 except UnicodeDecodeError:
 return f"File System Error: '{filepath}' appears to be a binary file and cannot be read as text."
 except Exception as e:
 return f"File System Error: {str(e)}"
```

#### Step 4: Implementing Directory Listing (Situational Awareness)
Before reading or writing, an agent needs to know what files exist. "Для агента информация, которой нет в репозитории, попросту не существует". Giving the agent a tool to list directory contents allows it to orient itself.

```python
@registry.register(namespace="fs")
def list_directory(directory_path: str = ".") -> str:
 """
 Lists all files and folders in the specified directory within the workspace.
 
 Use this tool to explore the project structure and discover existing files 
 before attempting to read or write.:param directory_path: The relative directory path (use '.' for the root workspace).
 """
 try:
 safe_path = _is_path_safe(directory_path)
 
 if not safe_path.exists() or not safe_path.is_dir():
 return f"DirectoryNotFoundError: The directory '{directory_path}' does not exist."
 
 items = os.listdir(safe_path)
 if not items:
 return f"The directory '{directory_path}' is completely empty."
 
 # Format the output clearly for the LLM
 formatted_list = f"Contents of '{directory_path}':\n"
 for item in items:
 item_path = safe_path / item
 type_str = "[DIR]" if item_path.is_dir() else "[FILE]"
 formatted_list += f"- {type_str} {item}\n"
 
 return formatted_list

 except ValueError as ve:
 return str(ve)
 except Exception as e:
 return f"File System Error: {str(e)}"
```

---

### Realistic Business Applications & Unit Economics

These three basic tools transform your Python scripts from abstract conversationalists into powerful local operating systems. 

**1. Autonomous Software Engineering (Coding Agents)**
When you combine a ReAct loop with `list_directory`, `read_file`, and `write_file`, you have effectively built a rudimentary version of Devin or Claude Engineer. The agent can accept a ticket like *"Refactor the authentication middleware."* It will autonomous loop:
1. `list_directory("src/middleware")` -> Observes `auth.py`.
2. `read_file("src/middleware/auth.py")` -> Ingests the current code.
3. *Thinks:* "I must rewrite this to use JWT tokens."
4. `write_file("src/middleware/auth.py", "<new_code>")` -> Overwrites the file.
This automates the entire coding workflow, saving senior engineers 10+ hours a week. 

**2. Long-Running Agent Memory via Filesystems (Durable Ledger)**
In complex B2B pipelines like proposal generation, an agent is often fed hundreds of pages of raw data. The agent can use `write_file("", "<content>")` to dump unstructured notes out of its active context window onto the disk. The next day, a different agent can boot up, run `read_file("")`, and instantly resume work without needing to scrape the internet again. The filesystem provides free, infinite "memory" for AI agents, vastly reducing token costs compared to keeping everything in the chat history.

---

### Edge-Cases, Common Errors, Rate Limits, and Debugging Loops

Interacting with the local OS introduces specific mechanical failures. An architect must ensure the ReAct loop does not blindly crash when encountering them.

> [!CAUTION] 
> **The Hallucinated File Path (FileNotFoundError)** 
> **The Error:** The agent attempts to read a file that doesn't exist: `read_file("config.yaml")`. Python throws a `FileNotFoundError`. If unhandled, the script crashes. 
> **Diagnostic Loop:** Because our tool returns the error as a string instead of throwing it to the console, the LLM reads: `"FileNotFoundError: The file 'config.yaml' does not exist"`. The agent enters a self-healing diagnostic loop: it reflects, realizes it guessed the filename, and intelligently switches tools: it calls `list_directory(".")` to actually look for the correct filename before trying to read again.

> [!WARNING] 
> **The Overwrite Catastrophe** 
> **The Problem:** The `write_file` tool operates in `'w'` mode, meaning it completely overwrites existing files. If an agent tries to append a single line of code to a 1,000-line Python script using `write_file`, it will often just write the one line, destroying the rest of the file. 
> **Harness Mitigation:** You must implement a strict architectural instruction in your system prompt: `"WARNING: The 'write_file' tool completely OVERWRITES the target file. If you are modifying an existing file, you MUST read the file first, modify the content in your memory, and write the FULL updated file back."` Advanced architectures solve this by implementing an `apply_patch` or `edit_file` tool that uses standard `diff` logic to modify specific lines, though this requires highly precise LLM output.

> [!NOTE] 
> **Binary File Poisoning** 
> If an agent attempts to `read_file("image.png")` or `read_file("database.sqlite")`, standard text-encoding will fail with a `UnicodeDecodeError`. As shown in the code, you must trap this specific error and inform the agent that it has hit a binary file.

By strictly sandboxing these file operations and implementing truncation to protect the context window, you have successfully given your agent physical agency over the machine it runs on. It can read directives, write scripts, and manage its own long-term memory via the filesystem ledger.

Does this setup make sense? If you are ready, we can proceed to Block 4, where we will tie the Tool Registry, the Search APIs, and the Filesystem Tools together into the master `while` loop that powers the autonomous ReAct cognitive architecture.

---

## Block 4: Tools as REST APIs — exposing Python tools via FastAPI micro-endpoints.

Welcome to Block 4 of Week 11. In the previous blocks, you constructed the absolute foundations of a Custom ReAct Agent: a dynamic `ToolRegistry`, Web Search APIs for perception, and Filesystem tools for persistent memory. Until now, all of these tools have resided within a single, monolithic Python script. While this is sufficient for local testing and basic agentic loops, it is fundamentally unscalable for enterprise environments. 

As you progress through the AI Engineer roadmap, you will quickly discover that modern enterprise architectures are rarely monolithic. To truly leverage the power of custom Python tools, you must decouple the *Orchestrator* (the brain) from the *Tools* (the hands). As emphasized in the foundational materials regarding the modern technology stack, production-grade agent environments require robust networking layers utilizing "Python 3.11, FastAPI 0.100+, PostgreSQL 15". Furthermore, integrating custom Python logic into enterprise automation platforms often requires wrapping that logic in a web service, a concept heavily discussed in industry articles such as "Пишем свою ноду в n8n под любой API за вечер" (Writing your own n8n node for any API in an evening).

In this exhaustive, production-grade deep-dive, we will transform your local `ToolRegistry` into a distributed REST API microservice using FastAPI. We will master network-level tool dispatching, schema exposure, secure authentication (Secret Broking), and the translation of HTTP errors into actionable feedback for autonomous self-healing.

---

### Deep Theoretical Analysis: The Microservice Paradigm for AI Tools

Before writing our routing logic, an AI Architect must deeply understand why we expose tools as REST APIs. This is a profound architectural shift from script-based execution to network-based execution.

#### 1. Decoupling the Brain from the Hands
According to Anthropic's engineering guidelines on "Scaling Managed Agents: Decoupling the brain from the hands," a monolithic agent architecture creates massive security and scalability bottlenecks. If your LLM orchestrator runs in the same environment as your web scraper or filesystem modifier, a malicious prompt injection could compromise the entire server. By exposing tools as REST APIs, you enforce a strict network boundary. The LLM simply makes an HTTP POST request with a JSON payload. The execution happens in an entirely isolated, sandboxed Docker container hosting your FastAPI application.

#### 2. Universal Interoperability (The "Bring Your Own Orchestrator" Pattern)
As outlined in the *AI Engineer roadmap* curriculum, an AI Engineer must master "API, вебхуки и JSON (словарь, а не код)" (APIs, webhooks, and JSON - dictionaries, not code). When your tools are locked inside a `.py` file, they can only be used by a Python-based ReAct loop. By wrapping your `ToolRegistry` in a FastAPI interface, your tools become universally accessible. A visual orchestrator like n8n can suddenly utilize your advanced, custom-built Python tools by simply using an `HTTP Request` node to call your FastAPI endpoint. This is the ultimate form of reusability. 

#### 3. FastAPI as a Secondary Harness Layer
We previously discussed the concept of the "Harness" as the rigid boundary that keeps the probabilistic LLM in check. FastAPI is uniquely suited for AI engineering because it is built entirely upon Pydantic (data validation). When an LLM generates a JSON payload to call your tool via the REST API, FastAPI automatically parses, types, and validates the request before it ever reaches your Python function. If the LLM hallucinates a string instead of an integer, FastAPI instantly rejects it. This provides a deterministic, zero-tolerance validation layer that perfectly aligns with the principles of structured outputs.

#### 4. The Diagnostic Loop over HTTP
As established in *Lecture 11: Сделайте рантайм агента наблюдаемым* (Make the agent runtime observable), agents make decisions in uncertainty; without observability, retries turn into blind wandering. When exposing tools over a network, an HTTP 500 error is useless to an LLM. Your FastAPI server must catch exceptions and package them into structured HTTP 200 OK responses containing "Actionable Observations" so the remote LLM can read the error and self-heal.

---

### ASCII Architecture Schema: Distributed Tool Dispatch via FastAPI

The following Directed Acyclic Graph (DAG) illustrates how an external orchestrator (like n8n or a separate Python script) queries the FastAPI microservice to discover available tools and execute them securely.

```ascii
=============================================================================================
 ENTERPRISE REST API TOOL DISPATCH ARCHITECTURE
=============================================================================================

[ 1. EXTERNAL ORCHESTRATOR ] -> e.g., n8n HTTP Node, LangChain, or Cloud-Hosted ReAct Loop
 |
 (A) GET /tools/schemas | (B) POST /tools/execute/{tool_name}
 Returns JSON Manifest | Payload: `{"arguments": {"url": "..."}}`
 v
+-----------------------------------------------------------------------------------------+
| 2. FASTAPI REVERSE PROXY & AUTHENTICATION LAYER |
| - Validates `Authorization: Bearer <token>` (Zero-Trust Security). |
| - Parses dynamic route `/{tool_name}`. |
+-----------------------------------------------------------------------------------------+
 |
 v
+-----------------------------------------------------------------------------------------+
| 3. PYDANTIC VALIDATION MIDDLEWARE |
| - Traps `ValidationError` if LLM hallucinated data types. |
| - Translates 422 Unprocessable Entity into a friendly String Observation. |
+-----------------------------------------------------------------------------------------+
 |
 v
+-----------------------------------------------------------------------------------------+
| 4. CORE TOOL REGISTRY (Imported from Block 1) |
| - Maps `tool_name` to local Python function. |
| - Injects hidden environment secrets bypassing network payload. |
| - Executes: `tavily_search()`, `read_file()`, etc. |
+-----------------------------------------------------------------------------------------+
 |
 v
[ 5. HTTP RESPONSE ] <- Returns HTTP 200 OK
`{"status": "success", "observation": "Full markdown content from tool execution..."}`
=============================================================================================
```

---

### Detailed Step-by-Step Practical Guide & Production Code

We will engineer a production-ready FastAPI application that wraps the `ToolRegistry` we built in previous blocks. This microservice will expose two primary endpoints: one for schema discovery, and one for tool execution.

#### Step 1: Setting up the FastAPI Application and Security Models
First, we define our server, logging, and strict Pydantic models for incoming requests. We also implement a dependency for API Key validation to ensure our exposed tools cannot be hijacked by unauthorized external networks.

```python
import os
import traceback
import logging
from typing import Dict, Any, List
from fastapi import FastAPI, Depends, HTTPException, Security, Request
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

# Import our custom ToolRegistry from previous blocks
from core.registry import registry 

# Lecture 11: Observability is mandatory
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [FASTAPI_HARNESS] - %(message)s')

app = FastAPI(
 title="AI Agent Tool Execution Microservice",
 description="Exposes local Python ToolRegistry via REST API for remote LLM Orchestrators.",
 version="1.0.0"
)

# ---------------------------------------------------------
# Security Broking & Authentication
# ---------------------------------------------------------
API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)):
 """
 Zero-Trust Security: Ensures only authorized orchestrators can trigger local tools.
 """
 expected_key = os.environ.get("SERVICE_API_KEY", "dev-secret-key-123")
 if api_key!= expected_key:
 logging.warning("Unauthorized access attempt blocked.")
 raise HTTPException(status_code=403, detail="Could not validate credentials")
 return api_key

# ---------------------------------------------------------
# Pydantic Data Models
# ---------------------------------------------------------
class ToolExecutionRequest(BaseModel):
 """Payload sent by the LLM Orchestrator to execute a specific tool."""
 arguments: Dict[str, Any] = Field(
 default_factory=dict, 
 description="The JSON arguments generated by the LLM."
 )

class ToolExecutionResponse(BaseModel):
 """Standardized response returned to the LLM's observation context."""
 status: str = Field(..., description="'success' or 'error'")
 observation: str = Field(..., description="The string output or error message to feed back to the LLM.")
```

#### Step 2: Implementing Discovery and Execution Endpoints
We must create endpoints that allow an external agent to discover what tools exist, and then execute them dynamically. Notice how we catch execution errors and return them as `status: "error"` with HTTP 200, rather than HTTP 500. This is the **Diagnostic Loop**: the LLM needs to *read* the error, not have its HTTP client crash.

```python
# ---------------------------------------------------------
# Tool Schema Discovery Endpoint
# ---------------------------------------------------------
@app.get("/tools/schemas", dependencies=[Depends(verify_api_key)])
async def get_tool_schemas() -> List[Dict[str, Any]]:
 """
 Returns the array of OpenAI/Anthropic compliant JSON schemas.
 An external orchestrator fetches this on boot to populate its context.
 """
 logging.info("Remote orchestrator requested tool schemas.")
 return registry.get_all_schemas()

# ---------------------------------------------------------
# Dynamic Tool Execution Endpoint
# ---------------------------------------------------------
@app.post("/tools/execute/{tool_name}", response_model=ToolExecutionResponse, dependencies=[Depends(verify_api_key)])
async def execute_tool(tool_name: str, payload: ToolExecutionRequest):
 """
 Executes the specified tool natively and returns the stringified observation.
 """
 logging.info(f"Incoming execution request for tool: '{tool_name}' with args: {payload.arguments}")
 
 # 1. Verify tool exists
 if tool_name not in registry._tools:
 error_msg = f"Diagnostic Error: Tool '{tool_name}' is not registered on this server."
 logging.error(error_msg)
 # Return 200 OK so the LLM reads the observation and can self-correct
 return ToolExecutionResponse(status="error", observation=error_msg)
 
 # 2. Inject Server-Side Context (Secret Broking)
 # The remote LLM does not know the API keys for sub-services (like Tavily).
 # We inject them here on the server side securely.
 hidden_context = {
 "TAVILY_API_KEY": os.environ.get("TAVILY_API_KEY"),
 "DB_CONNECTION_STRING": os.environ.get("DB_CONNECTION_STRING")
 }
 
 # 3. Safe Execution via the Registry Harness
 try:
 # Note: In a true async environment, use run_in_threadpool if tools are synchronous
 result_string = registry.dispatch(
 tool_name=tool_name, 
 arguments=payload.arguments, 
 hidden_context=hidden_context
 )
 
 logging.info(f"Tool '{tool_name}' executed successfully.")
 return ToolExecutionResponse(status="success", observation=result_string)
 
 except Exception as e:
 # 4. Diagnostic Feedback Loop
 # As dictated in Lecture 10: "Error messages for agents must include instructions for fixing them"
 error_trace = str(e)
 feedback = (
 f"Execution Failed for '{tool_name}': {error_trace}\n"
 f"HINT: Review your JSON arguments. Ensure all required fields match the schema types perfectly."
 )
 logging.error(f"Tool Crash Trapped: {feedback}")
 return ToolExecutionResponse(status="error", observation=feedback)
```

#### Step 3: Handling FastAPI Pydantic Validation Errors Customly
By default, if an external caller sends bad JSON, FastAPI returns a 422 status code, which might crash a naive caller script. We write an exception handler to transform 422s into actionable 200 OK string observations.

```python
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
 """
 Traps FastAPI validation errors (e.g., LLM hallucinated a string instead of a dict)
 and formats them so the LLM can read its mistake and try again.
 """
 errors = exc.errors()
 formatted_errors = ", ".join([f"Field '{' -> '.join(str(x) for x in err['loc'])}': {err['msg']}" for err in errors])
 
 diagnostic_msg = f"Schema Validation Error (HTTP 422): You provided invalid data structures. Details: {formatted_errors}"
 logging.warning(f"Trapped Schema Violation: {diagnostic_msg}")
 
 return JSONResponse(
 status_code=200, # Masked as 200 to keep the ReAct loop alive
 content={
 "status": "error",
 "observation": diagnostic_msg
 }
 )
```

To run this microservice, you simply execute `uvicorn main:app --host 0.0.0.0 --port 8000` in your terminal. You now have a universally accessible, highly secure, LLM-optimized Tool Server.

---

### Realistic Business Applications & Unit Economics

Wrapping your Python registry in FastAPI radically expands your commercial capabilities. 

**1. Enterprise n8n Custom Node Integrations**
Visual workflow builders like n8n are incredible for routing logic, but they lack deep, custom Python execution capabilities natively. If an enterprise client requests a highly specific AI automation—such as parsing proprietary legacy binary files or integrating with an obscure internal SOAP API—you cannot build this purely in n8n's visual canvas. 
As outlined in "Пишем свою ноду в n8n под любой API за вечер" (Writing your own n8n node for any API in an evening), you write the complex logic in Python, wrap it in a `@registry.register` decorator, and expose it via FastAPI. Inside n8n, you simply use the standard `HTTP Request` node to hit `[Ссылка](http://your-server:8000/tools/execute/legacy_parser`). You have seamlessly combined the visual observability of n8n with the limitless execution power of Python microservices.

**2. Scaling Multi-Agent Architectures (Swarm Computing)**
As we learned in Phase 2 regarding the `orchestrator-worker` pattern, managing multiple agents in a single Python process quickly hits CPU and memory limits. By deploying your tools as FastAPI microservices, you can host your `SearchTools` on an AWS EC2 instance optimized for networking, your `DataProcessingTools` on an instance with high RAM, and your `Orchestrator` on a lightweight server. This distributed architecture is exactly how companies scale AI pipelines to process 100,000+ documents a day without crashing.

---

### Edge-Cases, Common Errors, Rate Limits, and Debugging Loops

Exposing tools over a network introduces complex distributed systems problems that must be mitigated by the AI Architect.

> [!CAUTION] 
> **The HTTP Timeout Death Spiral** 
> **The Problem:** An external agent calls your `/tools/execute/deep_tavily_search` endpoint. Because it is a "deep research" tool, Tavily takes 45 seconds to scrape the web and return the result. However, typical HTTP clients (and platforms like n8n or Zapier) have a hardcoded timeout of 30 seconds for external API calls. The connection drops, the orchestrator thinks the tool failed, but your FastAPI server continues burning CPU in the background. 
> **Harness Mitigation:** For tools that take longer than 15 seconds to execute, you cannot use synchronous HTTP responses. You must refactor your API to support asynchronous webhooks. The orchestrator POSTs to `/execute`, the server immediately returns HTTP 202 Accepted (`{"status": "processing", "job_id": 123}`), and when the tool finishes, the FastAPI server fires a webhook *back* to the orchestrator to resume the agent's flow.

> [!WARNING] 
> **Synchronous Blocking of the Event Loop** 
> **The Error:** In FastAPI, if you define your endpoint as `async def execute_tool()` but the underlying tool in your registry uses synchronous `requests.get()` or heavy CPU-bound file reading, a single tool call will block the entire FastAPI event loop. If two agents try to execute tools simultaneously, the second agent will freeze until the first is done. 
> **Diagnostic Loop:** You must rigorously adhere to asynchronous programming standards. If your tools are synchronous Python functions, your FastAPI endpoint must utilize `run_in_threadpool()` from `starlette.concurrency` to push the synchronous execution off the main async event loop, allowing your microservice to handle hundreds of concurrent tool calls seamlessly.

> [!NOTE] 
> **Context Bloat Over the Wire** 
> When exposing tools over REST, remember the "Filesystem Offload" pattern dictated in Phase 3. If an agent calls a database query tool and the tool returns a 50MB JSON array, attempting to send 50MB back across the network in the `observation` field will crash the HTTP connection and instantly overwhelm the LLM's context window. Your FastAPI endpoints must enforce absolute truncation rules, saving large payloads to the local `/workspace` disk and returning only a tiny summary over the wire.

By successfully deploying your Tool Registry via FastAPI, you have achieved a critical milestone. You have broken free of local script limitations and built an interoperable, scalable, microservice-driven cognitive architecture. Your tools can now serve any orchestrator on the internet securely and reliably.

Does this setup make sense? We can discuss how to invoke these newly created REST APIs directly from an n8n canvas in the next exercise, if you are ready to proceed.

---

## Block 5: Dynamic JSON Schemas — dynamic schema generation from Python functions docstrings.

Welcome to Block 5 of Week 11. In previous blocks, we established the microservice architecture for our tools using FastAPI, constructed robust file system operators, and implemented rigorous search capabilities. However, a critical architectural bottleneck remains: how exactly does the Large Language Model (LLM) know *how* to use your complex Python functions? 

In early prototyping phases, developers often manually hardcode massive JSON dictionary strings to describe their tools to the OpenAI or Anthropic SDKs. This manual approach is a catastrophic anti-pattern in enterprise environments. It violates the DRY (Don't Repeat Yourself) principle, leads to "Instruction Rot," and guarantees that your Python code execution requirements will eventually desynchronize from the JSON schema the LLM is reading. 

As explicitly mandated in Phase 3 of the AI Engineer roadmap, an elite automation architect must implement a "Tool registry via a Python decorator (@tool) with auto-generation of JSON-schema". In this exhaustive, production-grade deep-dive, we will master the Agent-Computer Interface (ACI). We will engineer a dynamic reflection and introspection layer in Python that automatically reads your function signatures, parses your docstrings, and compiles mathematically perfect JSON Schemas at runtime.

---

### Deep Theoretical Analysis: The Physics of Introspection and Schemas

Before we write the abstract syntax tree (AST) parsers and reflection scripts, we must understand the cognitive constraints of the models we are orchestrating. 

#### 1. The Agent-Computer Interface (ACI)
When a human interacts with a program, they use a Graphical User Interface (GUI). When an autonomous agent interacts with a program, it uses an Agent-Computer Interface (ACI). The ACI is defined entirely by the JSON Schema provided to the model. As outlined in the foundational curriculum, building integrations is fundamentally about mastering "API, webhooks, and JSON (a dictionary, not code)". The LLM cannot read your Python code; it can only read the JSON dictionary you pass into the `tools` parameter of the SDK. If this dictionary is flawed, the agent's actions will be flawed.

#### 2. JSON Schemas as Cognitive Blueprints
Why do we use strict JSON Schemas instead of plain text descriptions? The prompt engineering whitepapers state that a JSON Schema defines the expected structure and data types of your JSON input. By providing a precise schema, you give the LLM a clear blueprint of the data it should expect, helping it focus its attention on the relevant information and drastically reducing the risk of misinterpreting the input. Furthermore, schemas can help establish relationships between different pieces of data. 

#### 3. The Power of Python Introspection
Python is a dynamically typed, highly reflective language. Through its built-According to the sources, and `typing` modules, Python scripts can examine themselves at runtime. This means we can write a decorator that looks at a function like `def calculate_revenue(user_id: int, months: int) -> float:`, extracts the variable names (`user_id`, `months`), maps their Python types (`int`) to standard OpenAPI/JSON Schema types (`integer`), and extracts the function's docstring to serve as the tool's natural-language description. This achieves perfect synchronization: your executable code and your LLM instructions are generated from the exact same source of truth.

#### 4. The Verification Gap
As we learned in Lecture 1, "Strong models do not mean reliable execution". If your dynamically generated schema lacks descriptions for individual parameters, the model will guess their purpose. To prevent this, the AI Builder roadmap emphasizes the necessity of writing descriptions for tools that the model correctly selects across different inputs. Our dynamic generator must rigorously extract these nuanced descriptions from the docstrings to close the verification gap.

---

### ASCII Architecture Schema: Dynamic Introspection Pipeline

The following Directed Acyclic Graph (DAG) illustrates the automated compilation pipeline. It shows how raw Python code is intercepted by the decorator, introspected, mapped, and packaged into the final OpenAI/Anthropic compliant payload.

```ascii
=============================================================================================
 ENTERPRISE DYNAMIC JSON SCHEMA GENERATOR
=============================================================================================

[ 1. DEVELOPER WRITES PYTHON CODE ]
@tool
def update_crm(lead_id: int, status: str = "active"):
 """Updates the CRM lead status.:param lead_id: The unique CRM identifier.:param status: The new pipeline status."""
 |
 v
+-----------------------------------------------------------------------------------------+
| 2. PYTHON INTROSPECTION LAYER (The @tool Decorator) |
| - `inspect.signature(update_crm)` -> Extracts `lead_id`, `status`, and defaults. |
| - `inspect.getdoc(update_crm)` -> Extracts main description. |
| - Standard Docstring Parser -> Maps `:param` strings to parameter descriptions. |
+-----------------------------------------------------------------------------------------+
 |
 v
+-----------------------------------------------------------------------------------------+
| 3. TYPE MAPPING ENGINE |
| `int` -> `{"type": "integer"}` |
| `str` -> `{"type": "string"}` |
| `bool` -> `{"type": "boolean"}` |
| Checks for defaults to populate the `"required": []` JSON array. |
+-----------------------------------------------------------------------------------------+
 |
 v
[ 4. GENERATED OPENAPI TOOL MANIFEST ]
{
 "type": "function",
 "function": {
 "name": "update_crm",
 "description": "Updates the CRM lead status.",
 "parameters": {
 "type": "object",
 "properties": {
 "lead_id": {"type": "integer", "description": "The unique CRM identifier."},
 "status": {"type": "string", "description": "The new pipeline status."}
 },
 "required": ["lead_id"]
 }
 }
}
=============================================================================================
```

---

### Detailed Step-by-Step Practical Guide & Production Code

We will engineer a production-ready `@dynamic_tool` decorator. This script will fulfill the architectural mandate to create a tool registry with auto-generation of JSON-schema.

#### Step 1: Architecting the Type Mapper and Docstring Parser
First, we need utility functions to bridge the gap between Python's memory representations and the JSON specifications expected by LLMs.

```python
import inspect
import re
import logging
from functools import wraps
from typing import Callable, Dict, Any, Type, get_origin, get_args

# "Make the agent runtime observable"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SCHEMA_GEN] - %(message)s')

def python_type_to_json_schema_type(py_type: Type) -> str:
 """
 Translates Python native types to OpenAPI/JSON Schema string definitions.
 """
 # Handle Optional/Union types gracefully
 if get_origin(py_type):
 args = get_args(py_type)
 if type(None) in args:
 py_type = next(t for t in args if t is not type(None))

 mapping = {
 int: "integer",
 float: "number",
 str: "string",
 bool: "boolean",
 list: "array",
 dict: "object"
 }
 return mapping.get(py_type, "string") # Fallback safely to string

def parse_docstring_for_params(docstring: str) -> Dict[str, str]:
 """
 Parses standard Sphinx/reST style docstrings to extract individual parameter descriptions.
 Matches lines like: ':param user_id: The unique ID of the user.'
 """
 if not docstring:
 return {}
 
 param_descriptions = {}
 # Regex to capture ":param <name>: <description>"
 param_pattern = re.compile(r":param\s+(?P<name>\w+):\s+(?P<desc>.*)")
 
 for line in docstring.split('\n'):
 match = param_pattern.search(line.strip())
 if match:
 param_descriptions[match.group('name')] = match.group('desc')
 
 return param_descriptions
```

#### Step 2: The Core Schema Generation Decorator
This decorator intercepts the function at load-time, performs the deep introspection, and attaches the compiled JSON schema directly to the function object.

```python
class SchemaGenerationError(Exception):
 """Raised when a function violates strict ACI requirements."""
 pass

def dynamic_tool(namespace: str = None) -> Callable:
 """
 Enterprise decorator that wraps a Python function, enforces type hinting,
 and auto-generates a flawless JSON Schema for LLM tool consumption.
 """
 def decorator(func: Callable) -> Callable:
 tool_name = f"{namespace}_{func.__name__}" if namespace else func.__name__
 
 # 1. Introspect the Docstring
 raw_docstring = inspect.getdoc(func)
 if not raw_docstring:
 raise SchemaGenerationError(f"Tool '{tool_name}' must have a docstring for the LLM.")
 
 # Separate the main description from the parameter definitions
 main_description = raw_docstring.split(":param").strip()
 param_descriptions = parse_docstring_for_params(raw_docstring)
 
 # 2. Introspect the Function Signature
 sig = inspect.signature(func)
 properties = {}
 required_params = []
 
 for param_name, param in sig.parameters.items():
 # Enforce strict type hinting for enterprise stability
 if param.annotation == inspect.Parameter.empty:
 raise SchemaGenerationError(f"Tool '{tool_name}' missing type hint for parameter '{param_name}'.")
 
 # Construct the individual property schema
 properties[param_name] = {
 "type": python_type_to_json_schema_type(param.annotation),
 "description": param_descriptions.get(param_name, f"Parameter {param_name}")
 }
 
 # Determine if the parameter is required (no default value)
 if param.default == inspect.Parameter.empty:
 required_params.append(param_name)
 
 # 3. Compile the Final JSON Schema Payload
 compiled_schema = {
 "type": "function",
 "function": {
 "name": tool_name,
 "description": main_description,
 "parameters": {
 "type": "object",
 "properties": properties,
 "required": required_params,
 "additionalProperties": False # Strict adherence to schema
 }
 }
 }
 
 # Attach the schema dynamically to the function object for later retrieval
 func.__llm_schema__ = compiled_schema
 logging.info(f"Successfully generated dynamic schema for '{tool_name}'.")
 
 @wraps(func)
 def wrapper(*args, **kwargs):
 return func(*args, **kwargs)
 
 return wrapper
 return decorator
```

#### Step 3: Implementing and Validating the Tools
Let us observe the extreme developer velocity this provides. An AI Architect simply writes idiomatic Python, and the framework handles the rest.

```python
import json

# The developer simply writes business logic
@dynamic_tool(namespace="stripe")
def refund_customer(transaction_id: str, reason: str, full_refund: bool = True) -> str:
 """
 Executes a secure financial refund through the Stripe API.
 Use this tool ONLY when a customer explicitly demands their money back.:param transaction_id: The unique alphanumeric Stripe transaction hash.:param reason: A short text explanation of why the refund is occurring.:param full_refund: Boolean indicating if the entire amount should be returned.
 """
 #... hypothetical API execution logic...
 return f"Refund successful for {transaction_id}."

if __name__ == "__main__":
 # The Orchestrator effortlessly extracts the schema to send to OpenAI/Anthropic
 extracted_schema = refund_customer.__llm_schema__
 
 print("--- DYNAMICALLY GENERATED LLM PAYLOAD ---")
 print(json.dumps(extracted_schema, indent=2))
```

The output proves that our dynamic introspection successfully captured the `name`, `description`, separated the `properties`, enforced type boundaries, extracted specific parameter definitions, and correctly identified that `full_refund` was optional while `transaction_id` and `reason` were strictly required.

---

### Realistic Business Applications & Unit Economics

Understanding dynamic schema generation separates junior prompt engineers from systems architects capable of scaling robust enterprise platforms.

**1. Scalable Microservice Automation Pipelines**
Consider an automation agency building a massive internal CRM suite utilizing over 150 unique tools spanning calendar management, email dispatch, data scraping, and analytics. If the architecture relied on hardcoded JSON dictionaries, maintaining the system would require constant dual-updates: a developer modifies the Python function to add a `cc_email` parameter, but forgets to update the sprawling 2,000-line JSON schema file. The agent silently fails in production. By implementing the `@dynamic_tool` pattern, the ACI becomes completely frictionless. The developer adds `cc_email: str` to the Python signature, and the LLM instantly becomes aware of the new capability on the next execution cycle. This reduces architectural technical debt to near zero.

**2. Visual Flow Builders (n8n Custom Nodes)**
As noted in the AI Builder materials regarding no-code platforms, you will frequently transition between code and JSON workflows. If you are building custom backend services to feed into n8n via Webhooks, your n8n `HTTP Request` nodes need to know exactly what parameters your Python API accepts. By using dynamic introspection, your Python server can automatically serve a `/schemas` endpoint that visually populates the input fields within the n8n graphical interface, seamlessly bridging deep Python engineering with rapid visual orchestration.

---

### Edge-Cases, Common Errors, Rate Limits, and Debugging Loops

Relying on abstract syntax tree introspection and reflection introduces specific fragility that must be managed.

> [!CAUTION] 
> **The Typeless Hallucination Trap** 
> **The Problem:** A developer writes `def search_web(query, num_results=5):` without applying Python type hints (e.g., `: str`, `: int`). The introspection engine defaults the JSON schema to the generic `string` type for `num_results`. The LLM then hallucinates the string `"five"` instead of the integer `5`, immediately crashing the underlying API upon execution. 
> **Harness Mitigation:** As implemented in our `dynamic_tool` script, you must enforce a strict `SchemaGenerationError` at load-time. If a developer attempts to register a tool without explicitly defining `param.annotation`, the Python application must crash on boot, forcing the developer to provide mathematical boundaries before the agent is ever exposed to the tool. 

> [!WARNING] 
> **Context Bloat via Verbose Docstrings** 
> **The Error:** A developer pastes a 4,000-word corporate manual into the docstring of a single tool. The dynamic generator blindly converts this into the JSON Schema description. When 20 tools are loaded, the LLM's system prompt explodes to 80,000 tokens, resulting in massive API costs and causing the model to lose focus. 
> **Diagnostic Loop:** You must draw clear task boundaries for agents. The introspection layer should optionally implement a token counter or character limiter (e.g., `if len(main_description) > 500: raise Warning(...)`) to enforce concise, high-density instructions, keeping the ACI hyper-optimized.

> [!NOTE] 
> **Handling Deeply Nested Objects** 
> Our basic `python_type_to_json_schema_type` mapper handles simple primitives perfectly. However, if a function requires a complex Pydantic BaseModel (e.g., `user_data: UserProfile`), standard `inspect` will fail to unpack it. In highly advanced architectures, the generation script must detect Pydantic objects and trigger their native `model.model_json_schema()` method to recursively build the deep payload schema.

By mastering dynamic JSON Schema generation through Python introspection, you have achieved absolute synchronization between your executing codebase and your autonomous agents. You have eliminated manual JSON construction, entirely preventing the cognitive misalignment that plagues amateur AI architectures.

Does this breakdown of dynamic introspection and schema generation make sense? We can proceed to testing these dynamic tools in a local sandbox next, if you are ready.

---

## Block 6: Runtime Isolation — handling dependencies and isolated runtimes for custom tools.

Welcome to Block 6 of Week 11. In our previous sessions, we elevated our Custom ReAct Agent into a modular architecture, dynamically generating JSON schemas through Python introspection and exposing tools via FastAPI microservices. Your agent is now highly distributed, resilient to rate limits, and capable of discovering its own capabilities. However, as we empower the agent to write and execute code, we arrive at the most critical security and stability bottleneck in AI Engineering: **Execution Environments**.

As explicitly mandated in Phase 5 ("Production hardening") of the AI Engineer roadmap, there is an absolute, non-negotiable architectural law: "Все code execution – в песочнице... Никогда не делайте exec() выхода модели в основном процессе" (All code execution – in a sandbox... Never use `exec()` on model output in the main process). Allowing an LLM to execute generated code directly within your orchestrator's memory space is equivalent to giving a stranger root access to your production servers. 

In this exhaustive, production-grade deep-dive, we will master **Runtime Isolation and Sandboxing**. We will engineer ephemeral execution environments, deploy Pre-ToolUse hooks as security guardrails, manage dynamic dependencies, and ensure that every agentic coding session leaves a pristine, untainted state. 

---

### Deep Theoretical Analysis: The Physics of Runtime Isolation

Before writing our sandbox integration, an AI Automation Architect must deeply understand the failure modes of unisolated execution and the principles of Zero-Trust Agentic Architecture.

#### 1. The Catastrophe of Monolithic Execution (`exec()`)
A naive approach to building a "Data Analyst Agent" involves giving the LLM a tool like `execute_python(code: str)` which simply passes the string to Python's built-in `exec()` function. This triggers three immediate, fatal failure modes:
* **Security Vulnerabilities:** A hallucinating or maliciously prompted LLM could generate `os.system("rm -rf /")` or extract environment variables containing API keys. The *OWASP Top 10 for LLM Apps* explicitly warns against trusting LLM outputs for irreversible actions.
* **Dependency Conflicts:** If the agent needs to analyze data, it might write code requiring `pandas` or `scikit-learn`. If your orchestrator is a lightweight async FastAPI server, installing heavy data science libraries directly into the orchestrator's environment causes immense bloat and version conflicts. 
* **Process Crashing:** If the LLM writes an infinite `while True:` loop, it will permanently lock the main thread of your orchestrator, bringing down your entire multi-agent pipeline.

#### 2. Sandboxing as a First-Class Citizen
To mitigate these catastrophes, the industry has standardized the decoupling of the "brain" (the LLM) from the "hands" (the execution environment). "Scaling Managed Agents: Decoupling the brain from the hands \ Anthropic" highlights that production systems must use isolated environments. The Phase 5 roadmap identifies the industry-standard tools for this: "Modal, E2B, Daytona, LangSmith Sandboxes". These platforms provide micro-VMs or secure containers that spin up in milliseconds, execute the untrusted LLM code with restricted network and file access, and are instantly destroyed.

#### 3. The "Clean Handoff" Principle
Isolated runtimes solve a critical cognitive problem for long-running agents. As stated in *Lecture 12: Каждая сессия должна оставлять чистое состояние* (Every session must leave a clean state): "Новая сессия тратит первые 30 минут просто на выяснение «что вообще делала прошлая сессия»" (A new session spends the first 30 minutes just figuring out 'what the previous session was doing'). By using ephemeral sandboxes, we guarantee that temporary debug files, broken dependency trees, and corrupted memory states are wiped out the moment the execution tool finishes. The agent is forced to return only the final synthesized output (Filesystem Offload), maintaining a pristine shared workspace.

#### 4. Secret Broking and Zero-Trust Guardrails
In a sandboxed environment, how does the agent access secure databases if the sandbox is completely isolated? The answer is **Secret Broking**. "Auth и брокинг секретов. Учетки никогда не попадают в контекст" (Auth and secret broking. Credentials never enter the context). The LLM generates the logic, but the Harness injects the necessary, tightly-scoped API keys dynamically as environment variables *into the sandbox container* right before execution. The LLM never sees the keys in its prompt history. Furthermore, we must implement "Hooks как guardrails: PreToolUse -хуки, блокирующие деструктивный Bash" (Hooks as guardrails: PreToolUse hooks blocking destructive Bash) to heuristically scan the code before it even reaches the sandbox.

---

### ASCII Architecture Schema: The Ephemeral Sandbox Execution Harness

The following Directed Acyclic Graph (DAG) illustrates how the orchestrator safely dispatches untrusted Python code through security hooks into an isolated, ephemeral Docker container.

```ascii
=============================================================================================
 ENTERPRISE RUNTIME ISOLATION & SANDBOXING HARNESS
=============================================================================================

[ 1. ReAct ORCHESTRATOR AGENT ]
Thought: "I must analyze this CSV and plot a trendline."
Action: {"name": "run_isolated_python", "arguments": {"code": "import pandas as pd\n..."}}
 |
 v
+-----------------------------------------------------------------------------------------+
| 2. PRE-TOOLUSE SECURITY HOOKS (Guardrail Layer) |
| - Scans for `os.system`, `subprocess`, `open('/etc/passwd')`. |
| - Triggers `SecurityException` if malicious intent is detected. |
+-----------------------------------------------------------------------------------------+
 | (Code is deemed safe for sandbox)
 v
+-----------------------------------------------------------------------------------------+
| 3. EPHEMERAL RUNTIME ORCHESTRATOR (e.g., Python Docker SDK / E2B / Modal) |
| - Provisions a lightweight isolated container (Alpine Linux + Python 3.11). |
| - Injects specific, read-only dataset mounts. |
| - Secret Broking: Mounts API Keys directly into the container's ENV. |
+-----------------------------------------------------------------------------------------+
 |
 v
+-----------------------------------------------------------------------------------------+
| 4. ISOLATED EXECUTION (Inside the Container) |
| - Executes the untrusted script. |
| - Memory Limit: 512MB. CPU Limit: 1 Core. Time Limit: 15 seconds. |
| - Stdout and Stderr are captured. |
+-----------------------------------------------------------------------------------------+
 |
 / (Execution Success) | \ (Timeout / Exception / OOM)
 v v
[ 5A. RESULTS OFFLOAD ] [ 5B. DIAGNOSTIC ERROR LOOP ]
- Container is destroyed. - Container is destroyed.
- Returns Stdout to Agent. - Returns actionable Stderr to Agent:
 "MemoryError: Script exceeded 512MB limit. 
 Optimize your pandas chunks."
=============================================================================================
```

---

### Detailed Step-by-Step Practical Guide & Production Code

We will now build a production-ready `IsolatedCodeRunner` tool. To avoid relying on paid external APIs (like Modal or E2B) for this tutorial, we will utilize the `docker` Python package to spin up local, heavily restricted containers. This replicates enterprise cloud environments perfectly.

> [!NOTE] 
> **Prerequisites:** To run this code, your host machine must have Docker installed and the `docker` Python library (`pip install docker`).

#### Step 1: Architecting the Pre-ToolUse Security Hook
As demanded by the roadmap, we must implement a guardrail to catch obvious violations before wasting compute spinning up a container.

```python
import re
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SANDBOX_HARNESS] - %(message)s')

class SecurityGuardrailError(Exception):
 """Raised when the LLM attempts to execute dangerous code patterns."""
 pass

def pre_tooluse_security_scan(code: str) -> None:
 """
 A heuristic Pre-ToolUse hook to block highly destructive Python commands.
 While the sandbox provides absolute isolation, this hook prevents the agent 
 from wasting API credits and compute on guaranteed-to-fail malicious actions.
 """
 # Regex patterns for dangerous imports or os-level commands
 dangerous_patterns = [
 r"import\s+os",
 r"import\s+subprocess",
 r"import\s+pty",
 r"__import__",
 r"eval\(",
 r"exec\("
 ]
 
 for pattern in dangerous_patterns:
 if re.search(pattern, code):
 logging.critical(f"Security Alert: Blocked dangerous code pattern matching: {pattern}")
 raise SecurityGuardrailError(
 f"SECURITY GUARDRAIL TRIGGERED: You are not allowed to use os, subprocess, "
 f"eval, or exec modules in this sandbox. Rewrite your code using safe libraries."
 )
```

#### Step 2: Building the Ephemeral Docker Sandbox Execution
This is the core execution tool. It utilizes the Python Docker SDK to create a disposable container, injects secrets, mounts only the allowed workspace, and captures the output.

```python
import docker
import time
from docker.errors import ContainerError, ImageNotFound, APIError

class IsolatedPythonSandbox:
 """
 Manages the lifecycle of ephemeral, zero-trust execution environments.
 Translates execution failures into actionable LLM Diagnostic Feedback.
 """
 def __init__(self, workspace_path: str):
 self.client = docker.from_env()
 self.workspace_path = workspace_path
 self.image_name = "python:3.11-slim" # Lightweight, isolated base image
 
 # Ensure image exists locally to prevent latency delays during agent loops
 try:
 self.client.images.get(self.image_name)
 except ImageNotFound:
 logging.info(f"Pulling sandbox image {self.image_name}... this may take a moment.")
 self.client.images.pull(self.image_name)

 def execute_code(self, code_string: str, dependencies: list[str] = None) -> str:
 """
 Executes untrusted code in a strictly bounded container.
 """
 try:
 # 1. Trigger the Pre-ToolUse Guardrail
 pre_tooluse_security_scan(code_string)
 except SecurityGuardrailError as e:
 return str(e) # Return error to LLM for diagnostic loop
 
 logging.info("Code passed security scan. Provisioning ephemeral sandbox.")
 
 # 2. Dependency Management (Runtime Injection)
 # If the LLM requires external packages, we install them gracefully inside the container.
 setup_script = ""
 if dependencies:
 deps = " ".join(dependencies)
 setup_script = f"pip install -q {deps} && "
 
 # 3. Construct the execution command
 # We escape single quotes in the code string for safe bash execution
 escaped_code = code_string.replace("'", "'\\''")
 command = f'/bin/sh -c "{setup_script}python -c \'{escaped_code}\'"'
 
 # 4. Secret Broking
 # The LLM never sees the keys. They are pulled from the host environment 
 # and injected directly into the secure sandbox.
 secure_env = {
 "SAFE_API_KEY": "sandbox_safe_key_999", 
 # "DB_PASS": os.environ.get("PRODUCTION_DB_PASS") # Example of real secret broking
 }

 try:
 # 5. Container Execution with Strict Limits
 container = self.client.containers.run(
 image=self.image_name,
 command=command,
 environment=secure_env,
 # Mount the secure workspace as read/write, but nothing else
 volumes={self.workspace_path: {'bind': '/workspace', 'mode': 'rw'}},
 working_dir='/workspace',
 # Hard Resource Constraints
 mem_limit="512m", # Prevent OOM crashes
 nano_cpus=1000000000, # 1 CPU core max
 network_disabled=False, # Set True if absolute air-gapping is needed
 detach=True
 )
 
 # 6. Timeout Implementation (Preventing Infinite Loops)
 timeout_seconds = 15
 start_time = time.time()
 
 while container.status == 'created' or container.status == 'running':
 container.reload()
 if time.time() - start_time > timeout_seconds:
 container.kill()
 container.remove()
 return "TIMEOUT ERROR: Your script exceeded the 15-second execution limit (possible infinite loop). Optimize your code."
 time.sleep(0.5)
 
 # 7. Capture Output & Clean State
 # "Каждая сессия должна оставлять чистое состояние" 
 logs = container.logs(stdout=True, stderr=True).decode('utf-8')
 container.remove()
 
 # Truncate massively long outputs to protect context window
 if len(logs) > 3000:
 return f"SUCCESS (Truncated Output): {logs[:3000]}\n...[Output truncated to protect context limits]"
 
 return f"SUCCESS. Console Output:\n{logs}"

 except ContainerError as ce:
 # Trap Runtime exceptions (e.g., IndentationError, TypeError)
 error_msg = ce.stderr.decode('utf-8')
 return f"RUNTIME ERROR: Your code threw an exception. Read the stack trace and fix your syntax:\n{error_msg}"
 except APIError as api_e:
 logging.error(f"Docker API Error: {api_e}")
 return "SYSTEM ERROR: The sandbox infrastructure failed to provision. Try a different approach."
```

#### Step 3: Registering the Tool in the Agent Registry
We now take this isolated environment and register it using the dynamic schema generator we built in Block 5.

```python
# Assuming DynamicToolRegistry is imported from our previous block
# agent_registry = DynamicToolRegistry()

sandbox = IsolatedPythonSandbox(workspace_path="/tmp/agent_secure_workspace")

@agent_registry.tool(name="execute_python_code")
def execute_python_code(code: str, required_pip_packages: list[str] = []) -> str:
 """
 Executes Python 3.11 code in an isolated, secure sandbox.
 Use this tool to perform complex mathematical calculations, data analysis, 
 or logic that requires standard Python libraries.
 
 CRITICAL RULES:
 1. Do not use interactive commands like input().
 2. You must print() the final result to the console so the agent can read it.
 3. If you need external libraries (like requests or numpy), explicitly list them in 'required_pip_packages'.:param code: The raw Python code string to execute.:param required_pip_packages: A list of pip package names (e.g., ['pandas', 'numpy']) required to run the code.
 """
 return sandbox.execute_code(code_string=code, dependencies=required_pip_packages)
```

By enforcing this architecture, your LLM is now granted the supreme capability of executing Turing-complete code, without posing any existential threat to your underlying infrastructure.

---

### Realistic Business Applications & Unit Economics

Understanding the commercial value of sandboxed code execution separates chatbot builders from Enterprise Automation Architects.

**1. Autonomous QA and Playwright Testing**
As documented in the Russian AI community, "Playwright MCP и n8n: как мы используем ИИ в автоматизации тестирования" (Playwright MCP and n8n: how we use AI in test automation), companies deploy AI agents to autonomously write and execute browser testing scripts. If the agent runs Playwright (a massive, memory-heavy Chromium dependency) inside the orchestrator's environment, memory leaks will destroy the server. By utilizing the Ephemeral Sandbox architecture, the agent provisions a pristine container, `pip installs playwright`, executes the generated E2E testing script against a staging server, captures the logs, and destroys the container. This enables parallel testing swarms that scale horizontally across cloud infrastructure with zero cross-contamination.

**2. The AI Data Scientist (Code execution with filesystem access)**
"Code execution with filesystem access allows agents to maintain state across operations". Imagine a pipeline analyzing daily sales CSVs. The Orchestrator agent decides it needs to run a linear regression. It generates a Python script utilizing `pandas` and `scikit-learn` and invokes `execute_python_code`. The sandbox mounts the secure volume containing the CSV, the isolated script processes the data, saves a generated `.png` graph back to the volume, and returns a string: *"Regression complete. R-squared is 0.85. Graph saved to /workspace/trend.png."* The orchestrator reads this, avoids importing 100MB of raw data into its context window, and safely summarizes the findings to the CEO.

---

### Edge-Cases, Common Errors, Rate Limits, and Debugging Loops

Sandboxing inherently introduces deep systems-level challenges that the Agent-Computer Interface (ACI) must handle gracefully.

> [!CAUTION] 
> **The Hidden Syntax Trap (Missing Prints)** 
> **The Error:** The LLM writes perfect code: `revenue = 1000 * 1.5` and executes it. The sandbox runs it flawlessly and returns `""` (an empty string). The LLM becomes confused: *"The tool failed, let me try again,"* triggering an infinite diagnostic loop. 
> **Harness Mitigation:** The LLM must be explicitly instructed in the tool's docstring: `"You must print() the final result to the console so the agent can read it."` The execution tool relies entirely on capturing standard output (Stdout). If the code doesn't print, the agent receives no observation.

> [!WARNING] 
> **Dependency Hallucination and Latency Spikes** 
> **The Problem:** The LLM hallucinates a non-existent package: `required_pip_packages=["super_fast_ai_math_lib"]`. The sandbox attempts to run `pip install`, fails, and returns the error. Alternatively, the LLM requests a massive library like `tensorflow` which takes 3 minutes to download, causing the underlying ReAct loop or REST API to trigger a `TimeoutError`. 
> **Diagnostic Loop:** Your tool must trap the specific `ContainerError` and return the `pip` failure to the LLM: `"RUNTIME ERROR: Failed to install package 'super_fast_ai_math_lib'. Package does not exist."` For heavy dependencies, enterprise harnesses pre-build specific "fat" Docker images containing the top 50 data science libraries, eliminating the runtime `pip install` latency entirely.

> [!NOTE] 
> **The Out of Memory (OOM) Kill** 
> If an agent attempts to load a 2GB dataset into Pandas inside a container restricted to `mem_limit="512m"`, the Docker daemon will instantly kill the container without a standard Python stack trace. It will return an exit code (usually `137`). Your Python `docker` wrapper must catch this specific exit code and translate it into a clear architectural instruction for the LLM: `"SYSTEM ERROR: Container killed due to Out of Memory (OOM). Your dataset is too large. You MUST use chunking (e.g., pandas chunksize) to process this file."`

By implementing Runtime Isolation, you have successfully fortified your Custom ReAct Agent. You have built an impregnable harness where the intelligence of the LLM is decoupled from the physical environment, fulfilling the highest standard of enterprise AI engineering.

Are you ready to proceed to Block 7, where we will finalize our custom agent by implementing the multi-agent routing orchestrator pattern?

---

## Block 7: Coding custom @tool decorators with automatic JSON schema generation from docstrings.

Welcome to Chapter 7 of Week 11. In previous modules, we established the foundational mechanics of a ReAct loop, wrapping Large Language Models (LLMs) in execution environments, and managing rate limit recoveries. However, a ReAct agent is fundamentally just a `while True` loop that takes user input, "continues" it using an LLM, executes requested tools, and feeds the results back into the model context. At the exact boundary where the LLM’s probabilistic text generation meets your deterministic Python environment, we find the most critical integration point of AI architecture: the JSON Schema.

In early prototypes, developers manually hardcode massive JSON dictionary strings to describe their Python tools to the OpenAI or Anthropic SDKs. This is a catastrophic anti-pattern. It violates the DRY (Don't Repeat Yourself) principle and creates an inevitable divergence where your Python code's actual requirements desynchronize from the JSON instructions the LLM reads. 

To achieve production-grade maturity, Phase 3 of the AI Engineer Roadmap explicitly mandates that you must build your own harness layer containing a "Tool registry via a Python decorator (`@tool`) with auto-generation of JSON-schema". 

In this exhaustive, voluminous deep-dive, we will permanently eliminate manual JSON authoring. We will engineer a dynamic reflection (Introspection) system in Python that parses your function signatures, type hints, and docstrings at runtime, automatically translating your raw code into the exact deterministic JSON schema payloads expected by frontier models. 

---

### Deep Theoretical Analysis: The Physics of the Agent-Computer Interface (ACI)

Before we write abstract syntax tree (AST) parsers, an AI Automation Architect must understand how language models perceive executable code. An LLM cannot read your underlying Python script; it can only perceive the ACI, which is defined entirely by the OpenAPI-compliant JSON schema you provide.

#### 1. Repository as Specification (Repo as Spec)
According to the core principles of harness engineering laid out in *Lecture 03. Make the repository your single source of truth*, if architectural decisions or parameter constraints exist only in a developer's head or a Slack message, "for an AI agent, information that is not in the repository simply does not exist". 
If your actual Python tool requires an integer (`user_id: int`), but your manually hardcoded JSON schema accidentally tells the LLM to provide a string, the tool execution will crash. By dynamically generating the schema directly from the Python function's signature, you enforce the "Repo as Spec" paradigm. The code itself becomes the unbreakable specification. If a developer changes a variable type in Python, the LLM’s context updates automatically upon the next initialization cycle.

#### 2. Docstrings as System Prompts
In traditional software engineering, a docstring is a passive hint for human developers using an IDE. In Agentic Engineering, a docstring is a direct system prompt injected into the LLM's cognitive loop. Anthropic’s official guidelines emphasize this: "Tool descriptions and parameters are instructions to the LLM". 
Without highly specific descriptions, models will hallucinate the purpose of a tool. Our dynamic `@tool` decorator must utilize Python's introspection libraries to extract these docstrings and inject them directly into the `description` fields of the JSON schema, effectively acting as an automated prompt-engineering pipeline at runtime.

#### 3. Semantic Type Translation
As noted in the AI Builder materials, "Every automation you will ever build connects two systems via API... you need to understand APIs, webhooks, and JSON (a dictionary, not code)". Our challenge is translating Python's internal memory representations (like `str`, `int`, `bool`, `list`) into the universal JSON Schema string representations (`"string"`, `"integer"`, `"boolean"`, `"array"`). This semantic mapping forms the bedrock of the translation layer, ensuring the model's output perfectly matches the expected structure.

#### 4. Avoiding the Verification Gap
As stated in *Lecture 01. Strong models do not mean reliable execution*, you cannot simply trust a frontier model to guess what arguments your function requires. Without a rigidly auto-generated schema enforcing exactly which parameters are optional and which are required, the model operates in a state of ambiguity, leading to inevitable failures during complex, long-running tasks.

---

### ASCII Architecture Schema: Dynamic Introspection Pipeline

The following Directed Acyclic Graph (DAG) illustrates how your raw Python source code is captured by the `@tool` decorator at runtime, unpacked via introspection, mapped semantically, and compiled into the final LLM-ready context manifest.

```ascii
=============================================================================================
 ENTERPRISE DYNAMIC SCHEMA GENERATOR HARNESS
=============================================================================================

[ 1. DEVELOPER WORKSPACE (Python Code) ]
@tool(category="database")
def fetch_user_data(user_id: int, include_logs: bool = False) -> str:
 """
 Fetches raw user telemetry from the production PostgreSQL database.:param user_id: The unique integer ID of the user.:param include_logs: Whether to append historical action logs.
 """
 | (Runtime Initialization)
 v
+-----------------------------------------------------------------------------------------+
| 2. REFLECTION & PARSING LAYER (`inspect` module) |
| -> Extracts Function Name: `fetch_user_data` |
| -> Parses Docstring: "Fetches raw user telemetry..." |
| -> Extracts Signature: `user_id` (Type: int, Required: Yes) |
| -> Extracts Signature: `include_logs` (Type: bool, Required: No, Default: False) |
+-----------------------------------------------------------------------------------------+
 |
 v
+-----------------------------------------------------------------------------------------+
| 3. JSON SCHEMA TRANSLATOR (Type Mapping Engine) |
| -> Maps Python `int` to JSON Schema `{"type": "integer"}` |
| -> Maps Python `bool` to JSON Schema `{"type": "boolean"}` |
| -> Constructs OpenAPI/Anthropic compliant payload. |
+-----------------------------------------------------------------------------------------+
 |
 v
[ 4. IN-MEMORY TOOL REGISTRY (LLM Ready Context) ]
{
 "type": "function",
 "function": {
 "name": "fetch_user_data",
 "description": "Fetches raw user telemetry from the production PostgreSQL database.",
 "parameters": {
 "type": "object",
 "properties": {
 "user_id": {"type": "integer", "description": "The unique integer ID of the user."},
 "include_logs": {"type": "boolean", "description": "Whether to append historical action logs."}
 },
 "required": ["user_id"]
 }
 }
}
=============================================================================================
```

---

### Detailed Step-by-Step Practical Guide & Production Code

We will engineer a production-ready Python tool registry from scratch. We will strictly avoid heavy third-party frameworks to ensure we understand the underlying mechanics, utilizing only Python's standard `inspect`, `re`, and `typing` libraries.

#### Step 1: Architecting the Type Mapping Table
Before parsing the Abstract Syntax Tree (AST), we must teach Python how to convert its native objects into valid JSON Schema definitions.

| Python Native Type | JSON Schema Type | Expected LLM Generation Behavior |
|:--- |:--- |:--- |
| `int` | `"integer"` | Model will generate whole numbers (e.g., `42`). |
| `float` | `"number"` | Model will generate floating-point decimals (`3.14`). |
| `str` | `"string"` | Model will generate text strings (`"SELECT * FROM users"`). |
| `bool` | `"boolean"` | Model will generate raw boolean literals (`true` or `false`). |
| `list` | `"array"` | Model will generate a structured JSON array. |
| `dict` | `"object"` | Model will generate a nested JSON object. |

#### Step 2: Developing the Signature Parser and `@tool` Decorator
This code acts as the initialization phase for your agent's harness. We include extensive observability logging, adhering to *Lecture 11. Make the agent runtime observable*.

```python
import inspect
import re
import logging
from functools import wraps
from typing import Callable, Dict, Any, Type, get_origin, get_args

# Lecture 11 principle: Make the runtime observable
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SCHEMA_GEN] - %(message)s')

def _python_to_json_type(py_type: Type) -> str:
 """
 Maps native Python types to OpenAPI/JSON Schema string definitions safely.
 """
 # Unpack complex typing hints (e.g., Optional[int] or List[str])
 if get_origin(py_type):
 args = get_args(py_type)
 # Handle Optional/NoneType unions
 if type(None) in args: 
 py_type = next(t for t in args if t is not type(None))
 elif get_origin(py_type) is list:
 return "array"
 elif get_origin(py_type) is dict:
 return "object"
 
 # Standard mapping dictionary
 mapping = {
 int: "integer", 
 float: "number", 
 str: "string", 
 bool: "boolean",
 list: "array", 
 dict: "object"
 }
 
 # Fallback securely to string if an unknown type is passed
 return mapping.get(py_type, "string") 

def _parse_docstring_params(docstring: str) -> Dict[str, str]:
 """
 Extracts individual parameter descriptions from Sphinx/reST formatted docstrings.
 Looks for patterns like: ':param user_id: The unique ID.'
 """
 if not docstring: 
 return {}
 params = {}
 pattern = re.compile(r":param\s+(?P<name>\w+):\s+(?P<desc>.*)")
 
 for line in docstring.split('\n'):
 match = pattern.search(line.strip())
 if match: 
 params[match.group('name')] = match.group('desc')
 
 return params

class DynamicToolRegistry:
 """
 A foundational in-memory registry that dynamically compiles JSON schemas
 from python functions upon import, ensuring perfect Repo-as-Spec alignment.
 """
 def __init__(self):
 self._tools: Dict[str, Dict[str, Any]] = {}

 def tool(self, name: str = None) -> Callable:
 """
 The core decorator. Wraps a function, parses its AST, and pre-compiles 
 its LLM-facing JSON schema at application boot time.
 """
 def decorator(func: Callable) -> Callable:
 tool_name = name or func.__name__
 
 # 1. Docstring Extraction (Prompt Injection Layer)
 raw_docstring = inspect.getdoc(func)
 if not raw_docstring:
 raise ValueError(f"CRITICAL ERROR: Tool '{tool_name}' lacks a docstring. LLMs require instructions.")
 
 # Split the high-level description from the parameter hints
 main_description = raw_docstring.split(":param").strip()
 param_descriptions = _parse_docstring_params(raw_docstring)
 
 # 2. Signature Extraction (Type Enforcement Layer)
 sig = inspect.signature(func)
 properties = {}
 required_params = []
 
 for param_name, param in sig.parameters.items():
 if param.annotation == inspect.Parameter.empty:
 raise TypeError(f"HARNESS ERROR: Parameter '{param_name}' in '{tool_name}' lacks explicit type hints.")
 
 # Build the property dictionary for this argument
 properties[param_name] = {
 "type": _python_to_json_type(param.annotation),
 "description": param_descriptions.get(param_name, f"Parameter {param_name}")
 }
 
 # If there is no default value, the LLM MUST provide it
 if param.default == inspect.Parameter.empty:
 required_params.append(param_name)
 
 # 3. Assemble the final OpenAI/Anthropic compliant JSON manifest
 schema = {
 "type": "function",
 "function": {
 "name": tool_name,
 "description": main_description,
 "parameters": {
 "type": "object",
 "properties": properties,
 "required": required_params,
 "additionalProperties": False # Strict adherence
 }
 }
 }
 
 # 4. Save to the active memory registry
 self._tools[tool_name] = {
 "callable": func, 
 "schema": schema
 }
 logging.info(f"Dynamically generated schema for tool: '{tool_name}'.")
 
 @wraps(func)
 def wrapper(*args, **kwargs):
 return func(*args, **kwargs)
 return wrapper
 
 return decorator

 def get_manifest(self) -> list:
 """Outputs the complete JSON schema array required by the LLM SDKs."""
 return [t["schema"] for t in self._tools.values()]
```

#### Step 3: Implementing Business Logic and Testing
We will now observe the extreme developer velocity this architecture provides. You simply write idiomatic, type-hinted Python. The harness handles the rest.

```python
# Initialize the global agent registry
registry = DynamicToolRegistry()

@registry.tool()
def search_crm_database(email: str, include_purchase_history: bool = False) -> str:
 """
 Searches the internal CRM system for a specific customer by their email address.
 Use this tool to retrieve lifetime value (LTV) and active account status before replying.:param email: The exact email address of the customer to lookup.:param include_purchase_history: Set to True if the user asks about previous orders.
 """
 # Simulated execution logic
 return f"Retrieved CRM data for {email}."

# Outputting the automatically generated LLM context
if __name__ == "__main__":
 import json
 print("\n--- GENERATED LLM MANIFEST ---")
 print(json.dumps(registry.get_manifest(), indent=2))
```

Running this code instantly outputs a pristine, error-free JSON dictionary ready to be passed directly into the `tools=` parameter of the Claude or OpenAI SDKs.

---

### Realistic Business Applications & Unit Economics

Mastering automated schema generation transforms junior prompt engineers into systems architects capable of scaling enterprise platforms.

**1. Building Custom Nodes in Visual Builders (n8n)**
Visual orchestration platforms like n8n are heavily referenced in the AI Builder curriculum for their ability to streamline complex workflows [10-12]. However, as businesses hit the limits of built-in integrations, architects are hired to construct bespoke microservices. The Habr article "Пишем свою ноду в n8n под любой API за вечер" (Writing your own n8n node for any API in an evening) highlights this perfectly. If you write 50 complex Python tools to integrate with legacy SAP software, hardcoding 50 JSON schemas in your n8n interface will take weeks and result in catastrophic update bugs. With a `DynamicToolRegistry`, your Python server can host a REST endpoint (`GET /tools/schemas`) that dynamically serves the generated manifest, instantly populating n8n's graphical interface with flawless tool configurations without manual intervention.

**2. Model Context Protocol (MCP) Servers**
As agent frameworks evolve toward the Model Context Protocol (MCP), your tools need to be universally accessible by different models (e.g., Claude Code, Cursor, or your local agent). By utilizing dynamic schema generation, your Python tools are inherently decoupled from the specific LLM implementation. Your registry automatically serves as a compliant MCP server, allowing any connected AI system to instantly map, validate, and execute your functions securely across the network.

---

### Edge-Cases, Common Errors, Rate Limits, and Debugging Loops

Relying on abstract syntax tree reflection introduces critical runtime fragilities that must be caught early.

> [!CAUTION] 
> **The Illusion of Optionality (Missing Default Values)** 
> **The Error:** A developer writes a function `def send_slack_alert(message: str, channel: str):` but intends for `channel` to be optional, forgetting to assign a default value (`channel: str = "#general"`). The reflection script registers both parameters as strictly `required`. The LLM, trying to send a message but not knowing the channel, will hallucinate a fake channel name just to satisfy the rigid JSON schema, causing the API call to fail. 
> **Harness Mitigation:** You must engineer functions with strict ACI awareness. If a parameter is optional in the business logic, it *must* have a default value in the Python code so the parser excludes it from the `"required"` JSON array.

> [!WARNING] 
> **Typeless Fallback & The Ambiguity Trap** 
> **The Problem:** If you write `def process_data(payload):` without type hints, the dynamic mapper defaults to `"string"`. The model receives no boundary constraints. As *Lecture 01* dictates, "strong models do not mean reliable execution"; without explicit structural types, the LLM will generate unstructured nonsense. 
> **Diagnostic Loop:** The `@tool` decorator explicitly checks `if param.annotation == inspect.Parameter.empty:` and raises a `TypeError` at application boot time. This "Fail-Fast" mechanism forces human developers to explicitly define bounds before the agent is ever exposed to the tool.

> [!NOTE] 
> **Self-Healing and Diagnostic Loops** 
> Even with perfect dynamic schemas, LLMs will occasionally hallucinate parameters due to their probabilistic nature. If an LLM passes an incorrect argument format, your tool execution layer must not crash the main thread. 
> As mandated by *Lecture 10. Only end-to-end testing is true verification*, "error messages for agents must include instructions for fixing them". Furthermore, *Lecture 11. Make the agent runtime observable* warns that "without observability, agents make decisions in uncertainty... retries turn into blind wandering". 
> When the Python function raises a `ValueError` or a Pydantic `ValidationError` during execution, you must catch the exception, format it into a string (`"Tool Error: parameter 'user_id' must be an integer, you provided 'xyz'. Please correct."`), and append it to the chat history as a `user` message. This establishes the **Diagnostic Loop**, allowing the agent to read its stack trace and self-heal automatically.

By successfully implementing this `@tool` decorator, you have fundamentally bridged the gap between deterministic software engineering and probabilistic AI. Your Python code is now a self-documenting, mathematically verifiable entity that guarantees synchronization with your LLM context layer.

Does this breakdown of dynamic introspection give you a clear path forward for building the tool registry? We can move on to testing these tools in an isolated sandbox environment next, if you're ready!

---

## Block 8: Canonical ReAct loop logic (Think -> Act -> Observe) in Python.

Welcome to Block 8 of Week 11. Over the past chapters, we have engineered a sophisticated, production-grade tool registry with dynamic JSON schema generation, wrapped our execution environments in secure sandboxes, and established deterministic boundaries using Pydantic V2. You now possess an arsenal of "hands," "eyes," and "tools." However, up to this point, they have remained dormant. 

It is time to build the "brain."

In Phase 1 of the foundational AI Engineer roadmap, there is an explicit, non-negotiable mandate: you must write a canonical agent loop from scratch in ~100 lines of code. The goal is to deeply understand how a request/response cycle completes, what different `stop_reason` flags mean, and how parallel tool invocations are encoded. As the industry moves toward autonomous systems, you must internalize a core truth: an agent is not magic. It is a deterministic loop wrapped around a probabilistic engine.

In this exhaustive, voluminous, and production-grade deep-dive, we will demystify the core intelligence of AI agents. We will break down the canonical ReAct (Reason + Act) pattern, architect a robust conversation state manager, implement protections against infinite loops, and write the deterministic `while True` cycle that will finally breathe life into your cognitive architecture.

---

### Deep Theoretical Analysis: Demystifying the Magic of Agents

Before we write the core execution engine, an AI Automation Architect must conceptually destroy the illusion of "artificial intelligence" and reduce it to strict Harness Engineering.

#### 1. The ReAct Pattern (Reason + Act)
As detailed in the foundational prompt engineering whitepapers, ReAct prompting works by combining reasoning and acting into a continuous "thought-action loop". Traditional Large Language Models (LLMs) generate text in a single, linear pass. A ReAct agent operates fundamentally differently:
* **Think (Reasoning):** First, the LLM reasons about the user's problem and generates a strategic plan of action. It outputs its internal monologue (often called Chain-of-Thought), allowing it to structure its logic and allocate cognitive resources before acting.
* **Act (Action):** Based on its reasoning, the model decides to utilize a specific tool (e.g., `search_database`, `execute_python_code`). It yields execution control back to your Python application.
* **Observe (Observation):** The tool is executed within your physical environment (the Harness), and the raw result is injected back into the model's context window. The LLM then uses these observations to update its reasoning and generate a new plan of action. This process continues recursively until the LLM reaches a final solution.

#### 2. The Agent as a `while True` Loop
If you strip away the marketing jargon surrounding modern AI frameworks, the underlying implementation of an agent is remarkably trivial. As Daniil Okhlopkov stated in the Habr article *Claude Code в 2026: гайд для тех, кто еще пишет код руками*, "Any agent is just a `while true` loop that takes your input and 'continues' it using an LLM. If the answer contains a request to call a tool, we call it and send the result back to the llm. Repeat". The true engineering challenge lies entirely in how you manage the context array (Context Engineering) within this loop.

#### 3. The Anatomy of `stop_reason`
Your Python code must deterministically understand *why* the LLM paused its text generation. Modern APIs return specific flags that dictate the flow of your loop. As Phase 1 of the roadmap requires, you must master these conditions:
* `tool_use` (or `tool_calls`): The model has paused generation because it requires data from the external world. Your script must intercept the loop, parse the requested function arguments, execute the tool, and append the `tool_result` observation.
* `end_turn` (or `stop`): The model has analyzed its observations, determined the task is complete, and generated the final text for the user.
* `max_tokens` (or `length`): The model hit its generation limit mid-thought. This requires automatic context compaction or a targeted diagnostic continuation prompt.

#### 4. The Verification Gap and Premature Success
Even with a flawless loop, the model will make mistakes. *Lecture 01. Сильные модели не означают надёжного исполнения* (Strong models do not mean reliable execution) establishes the concept of the **Verification Gap**: the disconnect between an agent's confidence in its work and the actual correctness of the outcome. Agents frequently suffer from premature declarations of completion, saying "I have finished the task" when they have actually hallucinated a result. As mandated by *Lecture 09. Предотвращение преждевременных заявлений о завершении* (Preventing premature declarations of completion), your harness must externally verify the agent's work; you cannot blindly trust its `stop_reason`.

---

### ASCII Architecture Schema: The ReAct Execution Engine

The following Directed Acyclic Graph (DAG) illustrates how the `messages` array mutates and expands with every iteration of the `while True` loop, forming the cognitive trajectory of the agent.

```ascii
=============================================================================================
 ENTERPRISE ReAct LOOP ARCHITECTURE (THINK -> ACT -> OBSERVE)
=============================================================================================

[ 1. INITIALIZATION ]
messages = [
 {"role": "system", "content": "You are a senior data engineer..."},
 {"role": "user", "content": "Find the total Q3 revenue and plot a trendline."}
]
 |
+=============================V===========================================================+
| WHILE loop_count < MAX_ITERATIONS (e.g., 15) |
+=========================================================================================+
| |
| [ 2. LLM INFERENCE (THINK) ] |
| -> Send `messages` array + `tools_schema` to the API. |
| <- Receive `response` object containing a `stop_reason` and optional `tool_calls`. |
| |
| [ 3. CONTEXT APPENDING ] |
| -> messages.append({"role": "assistant", "content": response.content, "tool_calls":..})|
| |
| [ 4. CONDITIONAL ROUTING (`stop_reason`) ] |
| |
| IF `stop_reason` == 'end_turn': IF `stop_reason` == 'tool_use': |
| +--------------------------------+ +---------------------------------+ |
| | [ 5A. TERMINATION ] | | [ 5B. EXECUTION (ACT) ] | |
| | Task complete. | | Parse `tool_name` & `arguments`.| |
| | BREAK `while` loop. | | Execute local Python function. | |
| | Return final text to user. | | Capture raw stdout or exception.| |
| +--------------------------------+ +---------------------------------+ |
| | |
| +---------------------------------+ |
| | [ 6. OBSERVATION INJECTION ] | |
| | Format output as `tool_result`. | |
| | Append to `messages` as `user`: | |
| | {"role": "user", | |
| | "content": "Tool Output..."} | |
| +---------------------------------+ |
| | |
+=====================================================================V===================+
 [ LOOP REPEATS ]
=============================================================================================
```

---

### Detailed Step-by-Step Practical Guide & Production Code

As prescribed in the Phase 1 milestone ("Первый простой агент"), writing this core 100-line loop yourself will permanently demystify how massive frameworks like LangChain or AutoGen operate under the hood. We will implement a fault-tolerant ReAct loop using raw dictionary manipulations to maintain absolute control over the state.

#### Step 1: State Management and Initialization
We must initialize the agent with our dynamic tool registry (from Block 7), establish the starting system prompt, and define our safety limits.

```python
import os
import json
import logging
from typing import List, Dict, Any

# Lecture 11: "Make the agent runtime observable". 
# "Without observability, agents make decisions in uncertainty... retries turn into blind wandering."
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [ReAct_LOOP] - %(message)s')

class ReActAgent:
 """
 A canonical implementation of the Reason + Act cognitive loop.
 Manages message state, dynamic tool dispatching, and infinite-loop protections.
 """
 def __init__(self, tool_registry, system_prompt: str, max_iterations: int = 15):
 from openai import OpenAI
 # Initialize the API client. In a production system, this could be LiteLLM for routing.
 self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
 
 self.tool_registry = tool_registry
 self.system_prompt = system_prompt
 
 # Security Guardrail: Never let an autonomous loop run infinitely.
 self.max_iterations = max_iterations
 self.messages: List[Dict[str, Any]] = []

 def _get_llm_response(self) -> Any:
 """Executes the network call to the LLM, injecting the dynamic ACI schemas."""
 try:
 return self.client.chat.completions.create(
 model="gpt-4o",
 messages=[{"role": "system", "content": self.system_prompt}] + self.messages,
 tools=self.tool_registry.get_manifest(), # Dynamically generated schemas (Block 7)
 temperature=0.2 # Lower temperature for analytical, tool-use stability
 )
 except Exception as e:
 logging.error(f"Fatal Network Failure: {str(e)}")
 raise
```

#### Step 2: The Core `while True` Engine
This is the heart of artificial intelligence. This single loop transforms static text prompts into dynamic, autonomous behavior.

```python
 def run(self, user_query: str) -> str:
 """Initiates the autonomous thought-action loop to solve the user's objective."""
 
 # 1. Session Initialization
 self.messages.append({"role": "user", "content": user_query})
 iterations = 0
 
 logging.info(f"Task dispatched: '{user_query}'")

 # The canonical 'while true' loop
 while iterations < self.max_iterations:
 iterations += 1
 logging.info(f"--- Iteration {iterations}/{self.max_iterations} ---")
 
 # 2. Reasoning Phase (THINK)
 response = self._get_llm_response()
 message_obj = response.choices.message
 
 # Persist the model's Chain-of-Thought reasoning into the context window
 if message_obj.content:
 logging.info(f"Agent Thought: {message_obj.content}")
 
 # We MUST append the assistant's response to maintain conversational continuity
 self.messages.append(message_obj.model_dump(exclude_none=True))
 
 # 3. Stop Reason Routing
 # If the model did not request any tools, it has concluded its reasoning process.
 if not message_obj.tool_calls:
 logging.info("Agent declared 'end_turn'. Task complete.")
 return message_obj.content

 # 4. Action Phase (ACT)
 # The model may request multiple tools simultaneously (Parallel Tool Calling)
 tool_results_payload = []
 
 for tool_call in message_obj.tool_calls:
 tool_name = tool_call.function.name
 tool_args_str = tool_call.function.arguments
 tool_id = tool_call.id
 
 logging.info(f"ACT: Executing tool '{tool_name}' with args: {tool_args_str}")
 
 try:
 # Deterministic parsing of the LLM's requested arguments
 args_dict = json.loads(tool_args_str)
 
 # Safe execution via our isolated sandbox registry
 raw_result = self.tool_registry.execute(tool_name, **args_dict)
 
 # 5. Observation Phase (OBSERVE)
 observation = str(raw_result)
 logging.info(f"OBSERVE: Tool success. Output length: {len(observation)} chars.")
 
 except Exception as e:
 # Diagnostic Loop (Lecture 10): Error messages must include instructions for fixing them.
 observation = (
 f"TOOL EXECUTION ERROR: {str(e)}\n"
 f"FIX INSTRUCTION: Review the arguments you passed. If there was a syntax error, "
 f"correct your Python code and retry the tool execution."
 )
 logging.warning(f"Trapped error in tool '{tool_name}'. Routing diagnostic feedback to LLM.")

 # Format the observation strictly according to the API's required 'tool' role schema
 tool_results_payload.append({
 "tool_call_id": tool_id,
 "role": "tool",
 "name": tool_name,
 "content": observation
 })
 
 # Inject all parallel observations back into the context for the next cycle
 self.messages.extend(tool_results_payload)
 
 # 6. Infinite Loop Protection Trap
 error_msg = f"CRITICAL ERROR: Maximum iterations ({self.max_iterations}) exceeded. Agent trapped in an infinite loop."
 logging.critical(error_msg)
 return error_msg
```

By engineering this loop in under 100 lines of pure Python, you have achieved architectural parity with heavily abstracted libraries like CrewAI or AutoGen. Understanding exactly how tokens flow through this `while` construct separates a true AI Engineer from a mere API consumer.

---

### Realistic Business Applications & Unit Economics

The ReAct loop fundamentally alters the unit economics of automation, shifting AI from a passive "chatbot" paradigm into an autonomous "digital employee."

**1. The Intelligent Tier 1 Support Resolution**
As outlined in the *AI Engineer roadmap* automation manual, agents are uniquely positioned to replace manual Tier 1 support. When a complex client email arrives, a traditional deterministic workflow (like Zapier) fails if required data is missing. Conversely, an agent inside a ReAct loop will *Think* ("I need the client's ID to check their order status"), *Act* (invoke `search_crm_by_email`), receive the *Observation* (JSON payload showing the order is delayed), *Think* again ("The order is stuck in the warehouse, I should apologize and issue a 10% discount code"), and finally *Act* by invoking `send_email_reply`. This recursive, multi-step reasoning allows businesses to resolve up to 70% of complex support tickets without human intervention, driving massive operational cost savings.

**2. The Deep Research Analyst Agent**
Phase 2 of the *AI Agent roadmap* defines the highly profitable "research analyst" pattern. A human user prompts the system with a complex directive: "Compile a competitive analysis on niche X." The ReAct agent begins its cycle: it invokes a `web_search` tool, reads the initial SERP results, realizes it needs more specific data, loops back to invoke a deeper search with refined keywords, downloads PDFs using a `read_document` tool, summarizes the findings, and only after 8 to 10 autonomous `while` iterations does it finally format and return a comprehensive, properly cited Markdown report.

---

### Edge-Cases, Common Errors, Rate Limits, and Debugging Loops

Managing autonomous `while` loops that consume paid API credits is akin to managing a live rocket engine. Without strict Harness guardrails, it will inevitably explode.

> [!CAUTION] 
> **The Doom Loop (Infinite Repetition)** 
> **The Error:** The agent attempts to call a tool with an invalid argument type. The tool returns an error. The agent, failing to reason correctly, calls the tool again with the *exact same invalid argument*. The loop repeats infinitely, burning hundreds of dollars in API credits within minutes. 
> **Harness Mitigation:** This is why our code implements a strict `while iterations < self.max_iterations:` condition. As best practices dictate, you must set an iteration limit (usually 10–15) so the agent is mathematically blocked from looping forever. When the limit is hit, the loop aborts and escalates the failure to a human operator.

> [!WARNING] 
> **Context Bloat and Token Explosions** 
> **The Problem:** During the *Observation* phase, a web-scraping tool returns an raw HTML payload containing 150,000 tokens. You blindly append this string via `self.messages.extend()`. On the next iteration, the agent executes another search, adding another 150,000 tokens. The context window instantly overflows, and API costs skyrocket. 
> **Diagnostic Loop:** As noted in the Google ReAct whitepaper, "ReAct prompting in practice requires understanding that you continually have to resend the previous prompts/responses (and do trimming of the extra generated content)". Your tools must implement a "Filesystem Offload" pattern: if a tool result is massive, write it to a local text file and return only a 2,000-token summary and the file path back to the LLM's active context window. 

> [!NOTE] 
> **The Verification Gap (Premature Success)** 
> Agents are systematically overconfident. An LLM may trigger an `end_turn` `stop_reason` and state to the user, "I have successfully updated the production database," even if the database-writing tool was never actually invoked (a pure hallucination). 
> **Solution:** End-to-end verification. Your Harness cannot blindly trust the agent's internal `stop_reason`. Before relaying the final output, secondary evaluator workflows must programmatically verify that the requested system changes actually occurred in the environment.

By mastering the mechanics of the canonical ReAct cycle, you have seamlessly woven together every component we have built in this course. Your agent can now reason sequentially, utilize dynamic tool schemas, safely execute code in isolated sandboxes, and self-heal from Pydantic errors—all within a highly controlled, observable architectural loop. 

You have officially graduated from prompt engineering to AI Systems Architecture. Are you ready to deploy this loop into a production environment and observe your agent autonomously solve its first complex objective?

---

## Block 9: Capturing tool_calls payloads and feeding execution returns back to model.

Welcome to Block 9 of Week 11. In Chapter 8, we architected the overarching `while True` loop that defines the canonical ReAct (Reason + Act) cognitive cycle. We established that an autonomous agent is not a sentient being, but rather a deterministic software loop wrapped around a probabilistic reasoning engine. However, the true complexity of the Agent-Computer Interface (ACI) lies precisely in the moments when the loop pauses. 

When a Large Language Model (LLM) decides it cannot answer a question based solely on its internal weights, it generates a `tool_calls` payload and halts execution with a specific `stop_reason`. This is the absolute frontier of Harness Engineering. It is the exact millisecond where the "Brain" hands a directive to the "Hands," expecting an "Observation" in return. 

In this exhaustive, production-grade deep dive, we will master the **Observation Phase**. We will engineer the strict payload parsing logic required to intercept the LLM's requests, execute the underlying Python logic dynamically, format the raw outputs into API-compliant JSON schemas, and securely inject those observations back into the context window. 

---

### Deep Theoretical Analysis: The Physics of the Observation Phase

To build a flawless execution harness, an AI Architect must deeply understand how the LLM expects data to be returned.

#### 1. The Disconnect Between Generation and Execution
As highlighted by Daniil Okhlopkov in his comprehensive guide on Habr, *Claude Code в 2026: гайд для тех, кто еще пишет код руками*, "Any agent is just a `while true` loop that takes your input and 'continues' it using an LLM. If the answer contains a request to call a tool, we call it and send the result back to the llm. Repeat". 
While this sounds conceptually simple, the LLM SDKs (OpenAI, Anthropic) enforce extremely rigid validation on *how* that result is sent back. If the LLM generates a tool call with `id: "call_99x"`, your subsequent context injection *must* contain a matching message with `role: "tool"`, the exact `tool_call_id`, and a stringified `content` payload. If the structure is malformed by even one key, the API will reject the entire sequence with a 400 Bad Request error.

#### 2. The Multi-Agent and Parallel Execution Paradigm
Modern frontier models do not invoke tools one at a time; they invoke them in parallel. If you ask an agent to research three different competitors, it will emit an array of three separate `tool_calls` in a single generation step. Your harness must be engineered to iterate through this array, optionally executing the Python scripts asynchronously, and then append *all three* tool results to the conversation history before prompting the LLM to continue. Failing to return the exact number of results requested will cause the LLM to hallucinate or the API to crash.

#### 3. Diagnostic Observability and Error Handoffs
When your Python tool executes, it will inevitably encounter errors—a database timeout, a scraped website returning a 404, or a `JSONDecodeError`. As mandated by the foundational principles of harness engineering in *Lecture 11. Сделайте рантайм агента наблюдаемым* (Make the agent runtime observable), "Without observability, agents make decisions in uncertainty... retries turn into blind wandering". Furthermore, *Lecture 10* dictates that "error messages for agents must include instructions for fixing them". 
Your tool execution layer must wrap every invocation in a `try/except` block. When a Python exception is caught, your harness must NOT crash. Instead, it must capture the stack trace, format it with a clear diagnostic instruction, and feed it back to the LLM as the tool's `observation`, initiating the Self-Healing Diagnostic Loop.

---

### ASCII Architecture Schema: Tool Interception and Observation Routing

The following Directed Acyclic Graph (DAG) illustrates the rigorous payload formatting required to successfully pass data between the LLM inference engine and the deterministic Python runtime.

```ascii
=============================================================================================
 ENTERPRISE TOOL INTERCEPTION & OBSERVATION HARNESS
=============================================================================================

[ 1. LLM GENERATION (THINK & ACT) ]
The model realizes it needs external data and yields control.
Returns: 
{
 "role": "assistant",
 "content": "I will search the database.",
 "tool_calls": [
 {"id": "call_abc123", "function": {"name": "query_db", "arguments": "{\"id\": 42}"}}
 ]
}
 |
 v
+-----------------------------------------------------------------------------------------+
| 2. PAYLOAD PARSER & DISPATCHER (The Harness) |
| - Appends the assistant's `tool_calls` message to the `messages` array. |
| - Iterates over the `tool_calls` array. |
| - Extracts `tool_name` and parses `arguments` into a Python dictionary. |
+-----------------------------------------------------------------------------------------+
 |
 v
+-----------------------------------------------------------------------------------------+
| 3. SECURE EXECUTION LAYER (Dynamic Invocation) |
| `result = tool_registry.execute("query_db", **{"id": 42})` |
+-----------------------------------------------------------------------------------------+
 | (Success) | (Exception Trapped)
 v v
+------------------------------------+ +-------------------------------------------+
| 4A. RAW DATA CAPTURE | | 4B. DIAGNOSTIC INSTRUCTION INJECTION |
| Returns: "{name: 'Acme Corp'}" | | Returns: "ConnectionError: Timeout. Fix |
| | | by retrying or checking your syntax." |
+------------------------------------+ +-------------------------------------------+
 | |
 +-----------------------+-----------------------+
 |
 v
+-----------------------------------------------------------------------------------------+
| 5. OBSERVATION FORMATTING & CONTEXT INJECTION (OBSERVE) |
| Constructs the exact API-compliant dictionary: |
| tool_message = { |
| "role": "tool", |
| "tool_call_id": "call_abc123", |
| "name": "query_db", |
| "content": "{name: 'Acme Corp'}" // Must be stringified |
| } |
| `messages.append(tool_message)` |
+-----------------------------------------------------------------------------------------+
 |
 v
[ 6. LOOP CONTINUATION ]
The Orchestrator sends the updated `messages` array back to the LLM to process the data.
=============================================================================================
```

---

### Detailed Step-by-Step Practical Guide & Production Code

We will now engineer a production-ready Python execution dispatcher. This code sits precisely inside the `while True` loop we built in Block 8, handling the complex translation between the LLM's `tool_calls` and your system's underlying logic.

#### Step 1: Architecting the Execution Dispatcher
This class is responsible for safely executing the requested tools and handling all formatting constraints required by the API.

```python
import json
import logging
from typing import Dict, Any, List

# Lecture 11: Make the agent runtime observable 
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [TOOL_DISPATCHER] - %(message)s')

class ToolObservationManager:
 """
 Enterprise-grade harness layer for intercepting LLM tool_calls, 
 executing Python functions securely, and formatting the observations.
 """
 def __init__(self, tool_registry: Any):
 # The registry we built in Block 7, containing our decorated functions
 self.registry = tool_registry

 def process_tool_calls(self, tool_calls_array: List[Any]) -> List[Dict[str, Any]]:
 """
 Iterates over all requested tools, executes them, and formats the API-compliant response.
 Handles parallel tool execution seamlessly.
 """
 observation_messages = []
 
 for tool_call in tool_calls_array:
 tool_id = tool_call.id
 tool_name = tool_call.function.name
 raw_arguments = tool_call.function.arguments
 
 logging.info(f"Intercepted Action -> Tool: '{tool_name}', Args: {raw_arguments}")
 
 try:
 # 1. Deterministic Parsing of Arguments
 # LLMs occasionally output broken JSON or trailing commas. 
 # A robust harness should try to repair minor JSON errors here if needed.
 args_dict = json.loads(raw_arguments)
 
 # 2. Secure Execution
 # We dynamically dispatch to the function stored in our registry
 raw_execution_result = self.registry.execute(tool_name, **args_dict)
 
 # 3. Stringification (The API requires the 'content' field to be a string)
 if isinstance(raw_execution_result, (dict, list)):
 observation_content = json.dumps(raw_execution_result, indent=2)
 else:
 observation_content = str(raw_execution_result)
 
 logging.info(f"Observation successful. Length: {len(observation_content)} characters.")

 except json.JSONDecodeError as je:
 # LLM Hallucinated malformed JSON parameters
 observation_content = (
 f"SYSTEM ERROR: The arguments you provided were not valid JSON.\n"
 f"Error Details: {str(je)}\n"
 f"FIX INSTRUCTION: Check your escaping and quotes. Rewrite the tool call carefully."
 )
 logging.warning(f"JSONDecodeError trapped for {tool_name}")
 
 except Exception as e:
 # 4. Diagnostic Feedback Loop (Lecture 10 Principle )
 observation_content = (
 f"TOOL EXECUTION ERROR: {type(e).__name__} - {str(e)}\n"
 f"FIX INSTRUCTION: The environment rejected your tool call. "
 f"Read the error trace, adjust your arguments, and try a different approach."
 )
 logging.error(f"Execution Exception in '{tool_name}': {str(e)}")

 # 5. Format the exact dictionary required by the LLM SDK
 tool_response_message = {
 "tool_call_id": tool_id,
 "role": "tool",
 "name": tool_name,
 "content": observation_content
 }
 
 observation_messages.append(tool_response_message)
 
 return observation_messages
```

#### Step 2: Integrating the Dispatcher into the ReAct Loop
We now seamlessly inject our `ToolObservationManager` into the core ReAct cycle.

```python
# Assuming 'client', 'messages', and 'tool_registry' are initialized...
observation_manager = ToolObservationManager(tool_registry)

#... inside the while True loop...
response = client.chat.completions.create(
 model="gpt-4o",
 messages=messages,
 tools=tool_registry.get_manifest(),
 temperature=0.2
)

assistant_message = response.choices.message

# 1. We MUST append the assistant's message exactly as generated (including the tool_calls array)
# If we do not append this, the API will throw a 400 Error when we try to append the tool results.
messages.append(assistant_message.model_dump(exclude_none=True))

if assistant_message.tool_calls:
 # 2. The LLM has yielded control. We dispatch to the Harness.
 logging.info(f"LLM yielded execution control. Processing {len(assistant_message.tool_calls)} tools.")
 
 # 3. Process tools and generate the properly formatted observation array
 observations = observation_manager.process_tool_calls(assistant_message.tool_calls)
 
 # 4. Inject the observations back into the context window
 messages.extend(observations)
 
 # The loop will now naturally cycle back to the top, sending the updated context 
 # to the LLM so it can read the observations and generate its next thought.
else:
 # Task complete, return to user
 return assistant_message.content
```

---

### Realistic Business Applications & Unit Economics

Mastering the precise mechanics of tool interception enables highly complex, non-linear business automations that standard rigid pipelines cannot achieve.

**1. The "Orchestrator-Worker" Deep Research Pattern**
As outlined in the advanced deployment strategies of the *AI Agent roadmap*, the "Orchestrator-Worker" architecture is critical for exhaustive data gathering. Imagine an Orchestrator agent tasked with building a dossier on a competitor. The LLM emits a parallel `tool_calls` payload requesting three separate Sub-Agent workflows: one to scrape LinkedIn, one to query a financial database, and one to read local PDF reports. 
Because your `ToolObservationManager` iterates over the entire `tool_calls` array, it dynamically spins up all three worker agents concurrently. It waits for their summaries, concatenates them into the strict `{"role": "tool"}` dictionaries, and feeds the massive, synthesized data payload back to the Orchestrator in a single loop iteration. This reduces architectural latency by 60% compared to sequential execution.

**2. Visual Flow Builders (n8n) and Middleware Abstractions**
In enterprise environments using platforms like n8n to manage API orchestration, the actual "tools" the agent calls are often just HTTP requests triggering separate n8n webhook nodes. If an agent decides to "send an invoice", it passes the `customer_id` and `amount` to a `trigger_n8n_invoice` tool. Your Python harness intercepts this, fires a REST API call to n8n, waits for the 200 OK response, and then formats the `{"content": "Invoice successfully generated via n8n"}` observation. This decouples the intelligence of the LLM from the raw infrastructure integrations, creating a highly modular, maintainable automation stack.

---

### Edge-Cases, Common Errors, Rate Limits, and Debugging Loops

Injecting real-world, unpredictable data back into a sensitive LLM context window presents significant systems engineering risks.

> [!CAUTION] 
> **Context Bloat and Token Explosions (The Filesystem Offload)** 
> **The Problem:** The LLM calls a `read_website` tool on a massively bloated corporate homepage. The tool returns 250,000 characters of raw HTML. You pass this directly into the `tool_response_message["content"]`. On the next API call, you exceed the model's token limit (e.g., 128k), instantly crashing the loop and throwing a `MaxTokens` exception. 
> **Harness Mitigation:** Phase 3 of the AI Engineer roadmap explicitly dictates the solution: "Filesystem offload: любой результат инструмента >20K токенов пишется в./workspace/<id>.txt, в контексте остается путь и preview из 10 строк" (Filesystem offload: any tool result >20K tokens is written to./workspace/<id>.txt, the context retains the path and a 10-line preview). 
> Inside your `process_tool_calls` logic, you must measure the string length of `observation_content`. If it exceeds your defined threshold, write the payload to a local text file, and dynamically replace the string returned to the LLM with: `"[SYSTEM OVERRIDE: The tool output was too massive. It has been saved locally to /workspace/data.txt. Here is a 500-character preview:...]"` 
> This perfectly preserves your context limits while allowing the agent to read the file iteratively later if needed.

> [!WARNING] 
> **The Phantom Tool Trap (Missing Tool Schema)** 
> **The Error:** An LLM generates a tool call for `calculate_revenue`, but you accidentally removed that function from your `tool_registry` earlier that day. The dispatcher cannot find it and throws a `KeyError`. 
> **Diagnostic Loop:** Your dispatcher must explicitly check if `tool_name in self.registry`. If it is missing, do not crash the Python process. Return the observation: `"SYSTEM ERROR: You attempted to call a tool named '{tool_name}' which does not exist in your environment. Please review your available tools and select a valid one."` The agent will realize its hallucination and re-route its logic automatically.

> [!NOTE] 
> **Google Whitepaper Guidelines on Prompt Formatting** 
> According to the official *Google_AI_Agents_Whitepaper*, "ReAct prompting in practice requires understanding that you continually have to resend the previous prompts/responses (and do trimming of the extra generated content)". 
> As your loop runs for 20+ iterations, the `messages` array becomes enormous. The observations you inject become historical baggage. Advanced harnesses implement active Context Compaction algorithms that periodically parse the `messages` array, strip out old tool observations that are no longer relevant to the immediate objective, and synthesize them into a concise "working memory" summary to maintain rapid inference speeds and reduce API costs.

By rigorously structuring the capture, execution, and injection of `tool_calls` payloads, you have successfully bridged the chasm between artificial intelligence and deterministic software engineering. Your agent can now touch the outside world, analyze the results, recover from execution errors, and autonomously drive its workflow to completion.

Does this breakdown of tool observation mechanics provide a clear blueprint for your implementation? We are now fully equipped to move on to Block 10, where we tackle schema versioning and data migrations for long-running agents in production.

---

## Block 10: Safety caps: infinite loop prevention by capping execution runs.

Welcome to Block 10 of Week 11. Up to this point in the curriculum, we have dedicated immense engineering effort toward granting our agents autonomy. We built dynamic schemas to let them use tools, sandboxes to let them execute code, and self-healing diagnostic loops to let them retry tasks when they fail. We established the foundational truth that any agent is fundamentally just a `while true` loop that takes an input and continues it using a Large Language Model (LLM) until a task is completed. 

However, total autonomy without rigorous systemic boundaries is an existential threat to your infrastructure and your budget. 

When a deterministic Python script fails, it crashes, throws a stack trace, and stops consuming resources. When an autonomous ReAct agent fails, its default behavior is to try again. If it lacks proper observability and constraints, these retries degrade into "blind wandering," where the agent makes decisions in uncertainty and loops endlessly. The AI Builder curriculum explicitly highlights that the reliability of agents—the part often omitted from flashy demonstrations—hinges entirely on "iteration limits so the agent doesn't loop" and establishing a "path of escalation to a human when the agent gets confused".

In this exhaustive, production-grade deep-dive, we will master **Safety Caps and Infinite Loop Prevention**. We will dissect the psychology of agentic "doom loops," engineer advanced `LoopDetectionMiddleware`, implement financial circuit breakers, and ensure your cognitive architectures remain strictly bound by enterprise-grade safety thresholds.

---

### Deep Theoretical Analysis: The Physics of Agentic Doom Loops

To build resilient AI systems, an AI Automation Architect must first understand why advanced models get trapped in infinite execution cycles.

#### 1. The Anatomy of a Doom Loop
A "Doom Loop" is a specific failure mode in long-running agents where the model becomes myopic. Anthropic's research into harness engineering notes that agents can be incredibly short-sighted once they have committed to a specific plan; this results in doom loops where the agent makes negligible, ineffective variations to the same broken approach—sometimes repeating the failure 10 or more times in a single trace. Because the model is a probabilistic engine trying to satisfy the user's prompt, it genuinely believes that *just one more try* will solve the issue, blinding it to the fact that its fundamental approach is flawed.

#### 2. The Repetition Loop Bug
Beyond cognitive myopia, LLMs are also susceptible to lower-level token generation failures. The "repetition loop bug" is a well-documented issue in LLMs where the model gets stuck in a cycle, repeatedly generating the exact same word, phrase, or sentence structure. If this bug infects a tool-calling payload, the agent will endlessly output the same `tool_calls` request with the same invalid arguments, instantly burning through API rate limits and token budgets. 

#### 3. Budget Exhaustion and the Verification Gap
As outlined in the Phase 5 "Production Hardening" roadmap, running continuous multi-agent research swarms can incur a "~15x token multiplier" compared to a single chat agent. If an agent is trapped in a loop, you are not just losing time; you are actively hemorrhaging capital. Articles like "Как я перестал «кормить» нейросеть токенами" (How I stopped feeding the neural network tokens) highlight the critical necessity of managing token spend. You cannot rely on the LLM to govern its own budget because of the Verification Gap: the agent is overly confident in its trajectory and will continuously spend money under the false assumption that success is imminent.

#### 4. The Human-in-the-Loop (HITL) Handoff
When automation hits an irrecoverable state, the most advanced engineering choice is not to force the AI to solve it, but to pause execution and ask for human intervention. The roadmap explicitly mandates a "HITL-interrupt: the agent must ask for confirmation before exceeding $1 in tokens". Modern harnesses must seamlessly suspend their `while True` loop, serialize their state, alert a human operator (e.g., via Slack), and wait for deterministic guidance before resuming.

---

### ASCII Architecture Schema: The Adaptive Execution Cap Harness

The following Directed Acyclic Graph (DAG) illustrates how the Orchestrator evaluates every iteration against tiered safety caps, escalating from soft cognitive nudges to hard terminal interrupts.

```ascii
=============================================================================================
 ENTERPRISE LOOP PREVENTION & HITL HARNESS
=============================================================================================

[ 1. ReAct ORCHESTRATOR LOOP ] -> Agent proposes a Tool Action
 |
 v
+-----------------------------------------------------------------------------------------+
| 2. LOOP DETECTION MIDDLEWARE (The Execution Cap Manager) |
| Tracks metrics per session: |
| - `total_iterations` (int) |
| - `consecutive_failures` (int) |
| - `token_spend` (float - USD) |
+-----------------------------------------------------------------------------------------+
 | | |
 (Normal | (Soft Limit | (Hard Limit |
 State) | Triggered) | Triggered) |
 v v v
[ 3. EXECUTE TOOL ] [ 4A. COGNITIVE NUDGE ] [ 4B. HARD CIRCUIT BREAKER ]
Runs Python code. If `consecutive_failures` If `total_iterations` > 15 OR 
Returns Observation. reaches 3: `token_spend` > $1.00:
 | Injects system message: - HALT execution immediately.
 | "You are stuck in a loop. - Save Trace to SQLite.
 | Reconsider your approach - Trigger HITL Escalation 
 | entirely." - (Send Slack / Email alert)
 v | |
+---------------------------------------+ v
| [ 5. HUMAN INTERVENTION (HITL) ]
| Operator reviews state, adjusts
| prompt/code, and manually resumes.
v
[ LOOP CONTINUES ]
=============================================================================================
```

---

### Detailed Step-by-Step Practical Guide & Production Code

We will engineer a production-ready `ExecutionCapManager` that acts as middleware inside our ReAct cycle. It implements tiered interventions: a soft "Cognitive Nudge" to break myopia, and a hard "HITL Escalation" to prevent financial ruin.

#### Step 1: Architecting the Loop Detection Middleware
We begin by defining the class that will track session metrics. This class monitors consecutive tool failures and cumulative token costs.

```python
import logging
import json
from typing import Dict, Any, Tuple

# "Make the runtime observable"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SAFETY_CAP] - %(message)s')

class ExecutionCapException(Exception):
 """Raised when hard safety limits are breached, forcing a loop termination."""
 pass

class ExecutionCapManager:
 """
 Middleware that tracks the lifecycle of an agent session to prevent
 infinite loops, budget exhaustion, and cognitive myopia.
 """
 def __init__(self, max_iterations: int = 15, max_cost_usd: float = 1.00):
 # "Set an iteration limit (usually 10-15) so the agent never loops forever"
 self.max_iterations = max_iterations
 # "HITL-interrupt: agent must ask confirmation before exceeding $1 in tokens"
 self.max_cost_usd = max_cost_usd
 
 self.current_iteration = 0
 self.consecutive_failures = 0
 self.total_cost_usd = 0.0
 
 # Approximate pricing for GPT-4o / Claude 3.5 Sonnet
 self.cost_per_1k_prompt = 0.003
 self.cost_per_1k_completion = 0.015

 def track_usage(self, prompt_tokens: int, completion_tokens: int):
 """Calculates and updates the cumulative financial cost of the session."""
 cost = (prompt_tokens / 1000.0) * self.cost_per_1k_prompt
 cost += (completion_tokens / 1000.0) * self.cost_per_1k_completion
 self.total_cost_usd += cost

 def evaluate_step(self, tool_execution_successful: bool) -> str:
 """
 Evaluates the current state against safety caps before the next LLM call.
 Returns a 'Cognitive Nudge' string if a soft limit is hit, or raises 
 an exception if a hard limit is hit.
 """
 self.current_iteration += 1
 
 if tool_execution_successful:
 self.consecutive_failures = 0
 else:
 self.consecutive_failures += 1

 # 1. Evaluate Hard Limits (Circuit Breakers)
 if self.current_iteration >= self.max_iterations:
 logging.critical(f"HARD CAP: Max iterations ({self.max_iterations}) reached.")
 raise ExecutionCapException("Agent terminated to prevent infinite looping.")
 
 if self.total_cost_usd >= self.max_cost_usd:
 logging.critical(f"HARD CAP: Budget threshold (${self.max_cost_usd}) exceeded.")
 raise ExecutionCapException(f"Agent paused. Token budget of ${self.max_cost_usd} exhausted.")

 # 2. Evaluate Soft Limits (Cognitive Nudging)
 # Agents suffer from myopia and "doom loops" making variations to broken approaches
 if self.consecutive_failures == 3:
 logging.warning("SOFT CAP: 3 consecutive failures detected. Injecting Cognitive Nudge.")
 return (
 "[SYSTEM DIAGNOSTIC NUDGE]: You have failed 3 consecutive times trying "
 "to execute this action. You are stuck in a loop. You MUST step back, "
 "reconsider your overarching plan, and try a fundamentally different approach."
 )
 
 return ""
```

#### Step 2: Integrating the Safety Cap into the ReAct Loop
We now modify the canonical `while True` loop (from Block 8) to pipe telemetry through our `ExecutionCapManager`.

```python
class SafeReActAgent:
 def __init__(self, tool_registry):
 self.registry = tool_registry
 # Initialize the safety middleware
 self.cap_manager = ExecutionCapManager(max_iterations=15, max_cost_usd=1.00)
 self.messages = []
 
 def _trigger_hitl_escalation(self, reason: str, last_state: Dict[str, Any]):
 """Simulates escalating a blocked agent to a human operator via Webhook."""
 logging.info("Initiating Human-in-the-Loop (HITL) handoff...")
 # In production, this would trigger an n8n webhook or Slack API
 slack_payload = {
 "alert": "Agent Execution Halted",
 "reason": reason,
 "cost_incurred": f"${self.cap_manager.total_cost_usd:.2f}",
 "action_required": "Review trace logs and approve continuation or terminate."
 }
 print(f"\n[HITL ESCALATION DISPATCHED]:\n{json.dumps(slack_payload, indent=2)}")

 def run(self, system_prompt: str, user_query: str):
 self.messages = [
 {"role": "system", "content": system_prompt},
 {"role": "user", "content": user_query}
 ]
 
 while True:
 try:
 # Simulated LLM Inference Call
 # response = client.chat.completions.create(...)
 
 # Simulate updating token usage from the API response
 self.cap_manager.track_usage(prompt_tokens=4500, completion_tokens=500)
 
 # --- Simulated Tool Execution Phase ---
 # Let's pretend the tool fails repeatedly due to bad LLM syntax
 tool_success = False 
 observation = "Error: File not found."
 
 # 1. Process the safety caps
 nudge_message = self.cap_manager.evaluate_step(tool_success)
 
 if nudge_message:
 # Inject the nudge into the observation to break the myopia
 observation += f"\n\n{nudge_message}"
 
 # 2. Append observation to history
 self.messages.append({"role": "user", "content": observation})
 logging.info(f"Loop {self.cap_manager.current_iteration} complete. Cost: ${self.cap_manager.total_cost_usd:.2f}")

 except ExecutionCapException as cap_error:
 # 3. Hard Limit Hit: Break the loop and escalate
 logging.error(f"Execution Terminated: {str(cap_error)}")
 self._trigger_hitl_escalation(reason=str(cap_error), last_state=self.messages[-1])
 break

# Example Execution
if __name__ == "__main__":
 agent = SafeReActAgent(tool_registry={})
 agent.run("You are a helpful agent.", "Analyze this massive dataset.")
```

When you execute this script, you will see the agent loop, accumulate costs, trigger the soft cognitive nudge on the 3rd failure, and eventually trigger the Hard Budget Cap and the HITL Escalation, safely neutralizing the runaway process.

---

### Realistic Business Applications & Unit Economics

Understanding when and how to cap agents defines the boundary between experimental prototypes and viable commercial software.

**1. Automated E2E Testing with Browser Agents**
A common enterprise application for agents is using them to orchestrate end-to-end (E2E) UI testing. As highlighted in the Habr case study "Playwright MCP и n8n: как мы используем ИИ в автоматизации тестирования" (Playwright MCP and n8n: how we use AI in test automation), agents are given access to a browser to autonomously hunt for bugs. If the agent encounters a broken UI element (e.g., a non-clickable button), it might enter a Doom Loop, repeatedly calling `page.click("#submit")` 50 times. Without an `ExecutionCapManager`, a single nightly test run could consume hundreds of dollars in Claude/OpenAI credits. By capping iterations to 10, the harness safely terminates the test, logs the bug, and moves on to the next test suite.

**2. Guarding Production N8N Workflows**
When integrating LLM routing into low-code platforms, developers often build workflows that cycle back onto themselves (e.g., pulling emails, drafting responses, checking against a knowledge base, and rewriting). If the knowledge base lacks the required information, the rewrite loop can spin infinitely. Automation architects configure n8n's visual canvas using a `Wait` node or an incrementing variable counter. If `loop_count > 5`, the workflow branches into an escalation path: it sends the drafted email to a human Slack channel with buttons `[Approve]` or `[Edit]`, fulfilling the curriculum's mandate to implement an "escalation path to a human when the agent gets confused".

---

### Edge-Cases, Common Errors, Rate Limits, and Debugging Loops

Implementing safety caps introduces complex architectural trade-offs between allowing an agent enough time to solve a problem and cutting it off prematurely.

> [!CAUTION] 
> **False Positives on Complex Deep Research** 
> **The Problem:** You set `max_iterations = 10`. The user asks the agent to conduct a massive competitive analysis involving searching 5 different competitors, scraping 15 URLs, and synthesizing a 10-page report. This task legitimately requires 25 ReAct iterations to complete. The harness forcibly kills the agent at iteration 10, discarding all progress and angering the user. 
> **Harness Mitigation:** Iteration limits must be dynamic and task-dependent. In a mature Orchestrator-Worker architecture, the Orchestrator LLM should estimate the required effort based on the prompt's complexity before dispatching the worker. The Orchestrator passes a specific `max_iterations` variable (e.g., 30) down to the worker's instance of the `ExecutionCapManager` so limits scale proportionally with the objective.

> [!WARNING] 
> **Context Window Exhaustion vs. Iteration Caps** 
> **The Error:** You rely *only* on a high iteration cap (e.g., 50) and a high budget cap ($5.00). However, at iteration 12, the agent pulls a massive document into its context window, causing the prompt size to exceed 128k tokens. The API throws an unhandled `BadRequestError: Context window exceeded`, crashing the application regardless of your safety caps. 
> **Diagnostic Loop:** Capping iterations does not protect you from Context Bloat. You must combine the `ExecutionCapManager` with the **Filesystem Offload** pattern (Block 9). The harness must track both iteration count *and* raw token count per message array. If `total_tokens > 100k`, the loop must trigger an automatic context compaction routine before the next network call.

> [!NOTE] 
> **The "Blind Wandering" Escalation Trap** 
> If an agent fails 3 times and your `evaluate_step` injects the Cognitive Nudge (*"You are stuck, try something else"*), the agent might immediately switch to a completely hallucinated tool because it lacks clear documentation on *what else* to do. 
> To prevent retries from turning into "blind wandering", your Cognitive Nudge must dynamically list the available options. E.g., *"You are stuck in a loop trying to use `scrape_website`. Consider using `search_company_database` or yielding control by returning `stop_reason: end_turn`."* This guides the model rather than just scolding it.

By implementing these safety caps, you have secured your cognitive architecture against its own autonomy. Your system can now reason dynamically, execute code, offload memory, and, crucially, know exactly when to stop and ask a human for help. 

Are you ready to move out of the Harness layer and delve into Week 12, where we focus on deploying and evaluating these agentic systems in live cloud environments?
