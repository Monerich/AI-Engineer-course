# Презентация: n8n AI Nodes and LangChain Integration

📊 Slide 1. Block 1 (AI Engineer / Automation): n8n AI Nodes Architecture — how LangChain structures chains and agents under the hood.
* **Visual Layout Concept:** Dark mode `HSL(220, 15%, 16%)`. A hierarchical tree diagram showing a root node connected to interchangeable sub-nodes. Top-right icon: Lucide `Network`.
* **Key Technical Facts:**
 * n8n’s Advanced AI nodes are built directly on top of the LangChain framework.
 * The architecture is heavily modular, separating the cognitive engine (LLM) from memory, execution tools, and parsers.
 * Root nodes (like Agents or Chains) orchestrate the flow, dynamically calling attached sub-nodes to assemble complex cognitive pipelines without writing boilerplate code.

---

📊 Slide 2. Block 2 (AI Engineer / Automation): AI Agent Node in n8n — setting up n8n agents in Conversational Agent mode.
* **Visual Layout Concept:** Light mode `HSL(210, 20%, 98%)`. Flowchart: User Chat Trigger -> AI Agent Node -> LLM Provider. Top-right icon: Lucide `Bot`.
* **Key Technical Facts:**
 * The native AI Agent node operates in multiple modes, including Conversational and ReAct.
 * It autonomously processes incoming queries, manages conversation history, and determines when to retrieve external data via tools.
 * The agent's identity, operational constraints, and tool usage rules are strictly defined within its System Message prompt.

---

📊 Slide 3. Block 3 (AI Engineer / Automation): Advanced n8n Tools — creating custom tools via HTTP requests and JavaScript.
* **Visual Layout Concept:** Dark mode `HSL(222, 20%, 18%)`. Split screen showing an n8n UI node next to a TypeScript code snippet. Top-right icon: Lucide `Wrench`.
* **Key Technical Facts:**
 * When native tools are insufficient, architects use Custom Code Tools or HTTP Request nodes to execute bespoke API logic.
 * Developing custom community nodes requires wrapping API logic inside a TypeScript class utilizing the `execute()` method.
 * These custom tools securely interface with third-party systems using n8n's centralized Credentials vault, keeping API keys out of raw code.

---

📊 Slide 4. Block 4 (AI Engineer / Automation): Bot Memory — chat session persistence: Window Buffer Memory vs external DBs.
* **Visual Layout Concept:** Light mode `HSL(215, 25%, 95%)`. Schema comparing volatile RAM (Buffer) to durable storage (PostgreSQL). Top-right icon: Lucide `Database`.
* **Key Technical Facts:**
 * `Window Buffer Memory` stores context temporarily in volatile memory, tracking sessions via dynamic Session IDs.
 * Long-running agents require durable state control; this is achieved by connecting `Postgres Chat Memory` or `Redis Chat Memory` sub-nodes.
 * External databases prevent LLM "amnesia," allowing conversations to persist across container restarts or delayed user replies.

---

📊 Slide 5. Block 5 (AI Engineer / Automation): Ingesting Documents — loading PDFs, CSVs, and TXT files via Document Loaders.
* **Visual Layout Concept:** Dark mode `HSL(210, 10%, 20%)`. Graphic of various file types funneled into a single JSON extraction pipeline. Top-right icon: Lucide `FileText`.
* **Key Technical Facts:**
 * The `Default Data Loader` converts raw binary file data into structured LangChaAccording to the sources, objects.
 * Unstructured formats (PDFs, TXT) and structured data (CSVs) are parsed into raw `page_content` arrays.
 * This is the mandatory first step for Retrieval-Augmented Generation (RAG), and preserving file metadata during this stage is critical for downstream citation.

---

📊 Slide 6. Block 6 (AI Engineer / Automation): Text Splitting Strategies — chunking files via Text Splitters (header, character split).
* **Visual Layout Concept:** Light mode `HSL(205, 30%, 96%)`. Scissors icon slicing a large document block into smaller, overlapping segments. Top-right icon: Lucide `Scissors`.
* **Key Technical Facts:**
 * Feeding massive documents directly to an LLM triggers "Instruction Bloat" and the "Lost in the Middle" effect.
 * `Recursive Character Text Splitters` and `Token Splitters` mathematically divide text, using "Chunk Overlap" to prevent severing semantic context.
 * Advanced architectures utilize custom Python scripts to split documents strictly by Markdown headers, ensuring conceptual boundaries remain intact.

---

📊 Slide 7. Block 7 (Python Development): Professional OpenAI/Anthropic Python SDK usage • dot-env and clients timeout.
* **Visual Layout Concept:** Dark mode `HSL(225, 15%, 15%)`. Code editor displaying a `try/except` block with an SDK client instantiation. Top-right icon: Lucide `TerminalSquare`.
* **Key Technical Facts:**
 * Enterprise orchestration often bypasses visual nodes in favor of pure Python scripts utilizing the official Anthropic or OpenAI SDKs.
 * Security mandates using the `dotenv` library to inject API keys into the runtime environment without hardcoding them into scripts.
 * Production scripts must define explicit client `timeout` thresholds and implement `max_retries` to survive transient HTTP errors.

---

📊 Slide 8. Block 8 (AI Agent Builder / Agents & Harness): Tool JSON schemas — prompt strategies for deterministic tool selection.
* **Visual Layout Concept:** Light mode `HSL(210, 15%, 98%)`. A JSON object showcasing strict `enum` parameters next to a funnel graphic. Top-right icon: Lucide `FileJson`.
* **Key Technical Facts:**
 * LLMs do not "click" tools; they generate structured text based on the Tool JSON Schema injected into their prompt.
 * Tool descriptions act as behavioral instructions detailing exactly *when* to use and *when not to use* the tool.
 * Utilizing strict parameter constraints (like arrays of `enum` values) forces probabilistic models into highly deterministic execution paths.

---

📊 Slide 9. Block 9 (AI Agent Builder / Agents & Harness): Prompt injection shields via strict tool schemas and input validation.
* **Visual Layout Concept:** Dark mode `HSL(0, 20%, 15%)`. A shield graphic deflecting a red, malicious JSON payload. Top-right icon: Lucide `ShieldCheck`.
* **Key Technical Facts:**
 * Granting agents access to external tools introduces severe prompt injection vulnerabilities (e.g., unauthorized data deletion).
 * Architects must deploy input sanitization middleware to scrub malicious trigger phrases before they enter the LLM context.
 * `PreToolUse` Python hooks intercept the agent's tool execution request, programmatically validating the parameters and blocking destructive actions before the API is pinged.

---

📊 Slide 10. Block 10 (AI Agent Builder / Agents & Harness): Tracing agent reasoning during multi-tool execution chains.
* **Visual Layout Concept:** Light mode `HSL(220, 10%, 96%)`. A dashboard graphic rendering an expanding tree of OTEL spans. Top-right icon: Lucide `Activity`.
* **Key Technical Facts:**
 * Without observability, debugging multi-step agent failures relies on guesswork.
 * OpenTelemetry (OTEL) platforms like LangSmith or Phoenix log every model invocation, tool payload, latency span, and token count.
 * This telemetry enables the "Diagnostic Loop," allowing architects to pinpoint exactly whether an error originated from a faulty prompt, a malformed JSON schema, or a failed external API.

---

This provides the complete presentation outline for the Week 6 curriculum! Would you like me to move on to generating the video/teleprompter script for this same module, or are you ready to transition to Week 7?