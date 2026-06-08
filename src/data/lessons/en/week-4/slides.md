# Презентация: Case Study: Telegram Lead Filter and Parser

📊 Slide 1. Block 1: Ingesting AI Nodes in n8n
**Visual Layout Concept:** Dark mode background with subtle neon green accents. Use the Lucide `Brain` and `Cpu` icons to represent artificial intelligence nodes.
* **n8n Advanced AI Ecosystem:** Utilize n8n's dedicated Advanced AI nodes, including the AI Agent, Basic LLM Chain, and various model connectors.
* **Provider Integration:** Connect natively to leading LLM providers like Anthropic, OpenAI, and Google Gemini by securely configuring API credentials within the n8n interface.
* **Model Selection Criteria:** Optimize workflows by selecting specific chat models based on task requirements, balancing speed, reasoning capability, and cost.

---
📊 Slide 2. Block 2: Parsing Emails using LLMs
**Visual Layout Concept:** Clean light mode interface mimicking a split-screen email client and code editor. Use Lucide `Mail` and `FileJson` icons.
* **Unstructured Data Ingestion:** Connect a Gmail or IMAP trigger to read incoming emails automatically.
* **Targeted Extraction:** Use an LLM node to extract specific entities from the email body, such as names, phone numbers, or inquiry intents.
* **Structured Output Parsers:** Enforce a deterministic output format by instructing the LLM to return data strictly as a JSON object, enabling seamless downstream processing.

---
📊 Slide 3. Block 3: Telegram Bot API Configuration
**Visual Layout Concept:** Telegram's signature blue color palette (`#0088cc`). Use Lucide `MessageCircle` and `Bot` icons.
* **BotFather Setup:** Generate a unique Telegram Bot API token via BotFather to authenticate your n8n workflows.
* **Webhook Triggers:** Configure the n8n Telegram Trigger node to listen for incoming chat messages in real-time.
* **Response Formatting:** Utilize the Telegram Send Message node to push automated replies, leveraging Markdown syntax to format text cleanly and efficiently.

---
📊 Slide 4. Block 4: Practice: Smart Telegram Lead Filter
**Visual Layout Concept:** High-contrast workflow diagram showing data flowing from a phone to a database. Use Lucide `Filter` and `Zap` icons.
* **End-to-End Parsing:** Combine the Telegram trigger with an AI Agent to immediately ingest and interpret user queries.
* **LLM Decision Making:** Configure the agent to identify the user's intent and determine if the lead is qualified.
* **Actionable Alerts:** Route the processed data to subsequent nodes, such as sending a direct Markdown alert to a human sales team or logging the lead in Google Sheets.

---
📊 Slide 5. Block 5: n8n Live Debugging
**Visual Layout Concept:** HSL dark theme resembling a developer terminal. Include Lucide `Bug` and `Activity` icons.
* **Execution Analysis:** Monitor successful and failed workflow runs using n8n's built-in executions tab and historical logs.
* **Pinning Data:** Pin specific JSON payloads to nodes during the development phase to rapidly test downstream logic without needing to re-trigger the entire workflow manually.
* **Error Tracing:** Implement the Error Trigger node to build global error workflows that catch failures, read stack traces, and notify administrators.

---
📊 Slide 6. Block 6: Token Economics
**Visual Layout Concept:** Financial dashboard aesthetic with green up-trend charts. Use Lucide `Coins` and `TrendingDown` icons.
* **The 15x Multiplier:** Understand that multi-agent systems process significantly more tokens than simple prompt chains, dramatically impacting API costs.
* **Volume vs. Cost:** Analyze the financial impact of processing thousands of concurrent leads using flagship models versus smaller, optimized models.
* **Token Optimization:** Minimize context bloat by aggressively filtering inputs, using Markdown over raw HTML, and relying on structured JSON outputs.

---
📊 Slide 7. Block 7: Async Python
**Visual Layout Concept:** Dark IDE theme (e.g., VS Code syntax highlighting). Use Lucide `Terminal` and `Server` icons.
* **Bypassing Visual Limits:** Transition from visual n8n execution to pure code for massive parallel processing requirements.
* **Non-Blocking Architecture:** Utilize Python's `asyncio` library to run multiple tasks concurrently without locking the main execution thread.
* **High-Speed Fan-Out:** Implement the `httpx` asynchronous HTTP client to blast hundreds of simultaneous API requests to LLM providers efficiently.

---
📊 Slide 8. Block 8: Model Routing (Cost-Performance)
**Visual Layout Concept:** Dynamic branching flowchart with split paths. Use Lucide `GitMerge` and `BrainCircuit` icons.
* **Complexity Assessment:** Deploy a fast, cheap frontline model (e.g., Haiku or GPT-4o-mini) to assess the cognitive complexity of an incoming lead.
* **The Model Selector:** Instruct the frontline agent to output a specific target model name based strictly on the required capabilities.
* **Deterministic Routing:** Use an n8n Switch node to read the selector's JSON output and physically route the payload to either a budget model or a premium flagship model (e.g., Claude 3.5 Sonnet).

---
📊 Slide 9. Block 9: Designing fallback nodes and exponential backoff retry patterns
**Visual Layout Concept:** Red and yellow warning color palette transitioning to green. Use Lucide `ShieldAlert` and `RefreshCw` icons.
* **Rate Limit Defense:** Protect infrastructure from `HTTP 429` rate limits by configuring exponential backoff with jitter to gracefully delay retries.
* **Provider Agnosticism:** Build systems that do not rely entirely on a single LLM provider.
* **Fallback Routing:** Use the "Continue On Fail" setting and IF nodes to detect `HTTP 500` server errors, dynamically routing the payload to a backup model from a different vendor to ensure 99.9% uptime.

---
📊 Slide 10. Block 10: E2E reasoning pipeline for lead qualification
**Visual Layout Concept:** Complete funnel graphic showing unstructured data converting to structured blocks. Use Lucide `CheckCircle` and `Target` icons.
* **Prompt Chaining:** Break down the complex goal into a linear sequence of distinct nodes: Parse, Evaluate, and Route.
* **The Parser & Evaluator:** Node 1 strictly extracts the entities into JSON. Node 2 evaluates that exact JSON against corporate qualification rubrics (e.g., BANT scoring).
* **The Routing Decision:** The final LLM outputs a hard numeric score, allowing a deterministic n8n Switch node to safely push the lead to the CRM or a rejection sequence.

Let me know if you are ready to proceed to the next module!