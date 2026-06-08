# Презентация: n8n Foundations and Your First Workflow

📊 Slide 1. Block 1: n8n Infrastructure
* **Visual Layout Concept:** Dark mode background, Docker & Database Lucide icons.
* **Key points:**
 * n8n can be deployed locally using Docker Compose alongside a PostgreSQL database.
 * Self-hosting provides absolute control over data privacy and bypasses cloud-tier execution limitations.
 * Deployment tools like Railway offer simple one-click environments for hosting n8n.

---

📊 Slide 2. Block 2: Canvas & n8n Triggers
* **Visual Layout Concept:** Light mode interface mockup, Lightning bolt (trigger) and Action icons.
* **Key points:**
 * Workflows initiate with Trigger nodes, which listen for Webhooks, Cron schedules, or App events.
 * Manual triggers enable developers to test flows rapidly directly from the canvas.
 * Action nodes systematically execute downstream operations following the initial trigger event.

---

📊 Slide 3. Block 3: n8n Data & Expressions
* **Visual Layout Concept:** Code snippet block, Braces `{}` icon.
* **Key points:**
 * Dynamic data is injected into nodes using Expression fields rather than static Fixed fields.
 * Variables can map data from earlier nodes using the `$json` syntax.
 * n8n leverages standard JavaScript dot notation to reference nested JSON items.

---

📊 Slide 4. Block 4: Branching Logic
* **Visual Layout Concept:** Flowchart layout, Split/Merge arrows.
* **Key points:**
 * IF and Switch nodes route data down distinct conditional paths based on logical rules.
 * Nodes execute sequentially from left to right, and top to bottom in the visual canvas.
 * Merge nodes combine multiple incoming execution branches back into a single unified data stream.

---

📊 Slide 5. Block 5: Practice: Automated Welcome Pipeline
* **Visual Layout Concept:** 3-step pipeline graphic, Mail and Form Lucide icons.
* **Key points:**
 * A typical pipeline intercepts a form submission trigger and processes the payload.
 * An action node securely routes the parsed contact data into a Gmail node.
 * AI nodes can be inserted mid-flow to generate highly personalized greeting text based on the form inputs.

---

📊 Slide 6. Block 6: API Authentication in n8n
* **Visual Layout Concept:** Secure lock icon, Key symbol, dark mode UI.
* **Key points:**
 * n8n Credentials safely store API keys and tokens away from the visual canvas.
 * Developers must never hardcode API keys directly into HTTP request headers to prevent security leaks.
 * OAuth2 integrations require configuring redirect URLs in the third-party provider's developer console.

---

📊 Slide 7. Block 7: Python Development
* **Visual Layout Concept:** Python code block, Bug/Shield icons.
* **Key points:**
 * Python scripts act as deterministic execution engines that do not hallucinate.
 * The `try` and `except` blocks intercept potential execution crashes gracefully.
 * The `finally` block is utilized to clean up system resources after execution, regardless of success or failure.

---

📊 Slide 8. Block 8: Designing Self-Healing Paths
* **Visual Layout Concept:** Circular loop diagram, First-aid/Refresh icons.
* **Key points:**
 * Activating "Retry On Fail" settings helps bypass temporary API rate limits and network shocks.
 * A global Error Trigger node intercepts failures across all workspace workflows for unified observability.
 * Self-healing diagnostic loops catch errors and prompt an LLM with instructions to dynamically correct the failure.

---

📊 Slide 9. Block 9: State Transition Architectures
* **Visual Layout Concept:** Finite state machine node diagram, Pause/Play icons.
* **Key points:**
 * Long-running tasks must utilize durable execution and persistent database checkpoints.
 * Human-in-the-loop wait nodes pause executions indefinitely until a human manager provides approval.
 * Database nodes preserve context and global state between asynchronous execution sessions.

---

📊 Slide 10. Block 10: Linear Workflows vs Cyclic Graphs
* **Visual Layout Concept:** Split comparison (straight line vs circle), Scale/Balance icons.
* **Key points:**
 * Linear workflows execute deterministically based on hard-coded developer routing.
 * Agentic cyclic graphs grant the LLM complete autonomy to route tasks iteratively until a goal is met.
 * When multi-agent loop complexity outgrows n8n, developers must transition to code-first frameworks like LangGraph.

Would you like to draft the script for the first slide now?