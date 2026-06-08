# Презентация: Advanced n8n: Sub-workflows and Data Arrays

📊 Slide 1. Block 1 (AI Engineer / Automation): n8n Item Lists Concept — parallel executions, data loops, and item iteration.
* **Visual Layout Concept:** Dark mode background `HSL(220, 15%, 16%)` with contrasting cyan accents. Include an ASCII schema showing an array `[ {json:...}, {json:...} ]` passing through a node. Top-right icon: Lucide `ListTree`.
* **Key Technical Facts:**
 * All data inputs and outputs in n8n are strictly structured as an array of JSON objects. 
 * By default, n8n implicitly iterates over this array, running a node once per item if you are referencing specific items within the object.
 * When utilizing multiple branches (paths) originating from a single node, n8n executes the branches in a specific order: from topmost to bottommost, and if at the same height, from leftmost to rightmost.
 * A branch will execute completely through its node sequence before n8n moves to execute the next parallel branch.

---

📊 Slide 2. Block 2 (AI Engineer / Automation): Loops & Batches — processing item arrays through Split In Batches node.
* **Visual Layout Concept:** Clean light mode `HSL(210, 20%, 98%)`. Display a cyclical graph highlighting the dual outputs (`Loop` and `Done`). Top-right icon: Lucide `Repeat`.
* **Key Technical Facts:**
 * To process massive datasets without crashing the system, n8n utilizes the "Loop Over Items" (formerly Split in Batches) node.
 * This node features a `loop` route which passes a specific batch size (e.g., 1 item at a time) forward, and a `done` route which triggers only after all iterations are complete,.
 * The loop route must physically connect back to the input of the "Loop Over Items" node to complete the cycle.
 * It is best practice to pair this node with an "Execute Once" setting on subsequent nodes if you wish to halt repetitive execution.

---

📊 Slide 3. Block 3 (AI Engineer / Automation): Modular Workflows — executing sub-workflows using Execute Workflow node.
* **Visual Layout Concept:** Dark mode `HSL(220, 15%, 16%)`. Network tree diagram showing a "Parent" workflow spawning multiple isolated "Child" workflow blocks. Top-right icon: Lucide `Network`.
* **Key Technical Facts:**
 * The "Execute Workflow" node allows developers to call one workflow from another, extracting logic into dedicated, reusable sub-workflows.
 * Sub-workflows must start with a specific trigger: the "When called by another workflow" node (Execute Sub-workflow Trigger).
 * Data passed into the sub-workflow executes item-by-node-by-item, and the items from the final node of the child workflow are synchronously returned back to the parent workflow.
 * This architectural pattern drastically increases workflow building speed and enterprise scalability.

---

📊 Slide 4. Block 4 (AI Engineer / Automation): Variable Isolation — managing parent/child variables and scope persistence.
* **Visual Layout Concept:** Light mode `HSL(210, 20%, 98%)`. Use bounding boxes representing memory scopes, highlighting variables traversing from Parent Box to Child Box. Top-right icon: Lucide `Box`.
* **Key Technical Facts:**
 * When utilizing the "Call n8n Workflow Tool" or standard "Execute Workflow", the variables of the child workflow are strictly isolated from the parent to prevent scope contamination.
 * Developers explicitly pass variables into the sub-workflow by selecting "Define using Fields below" and mapping expressions like `{{ $json.title }}` to specific input keys,.
 * Inside the sub-workflow, the "When called by another workflow" trigger receives these exact keys as its initial JSON payload, allowing clean state handoffs,.

---

📊 Slide 5. Block 5 (AI Engineer / Automation): Practice: Loop News Digest — RSS trigger, top 5 items filter, sub-workflow summaries.
* **Visual Layout Concept:** Dark mode `HSL(220, 15%, 16%)`. A linear pipeline schema mapping: RSS -> Split Out -> Loop -> AI Summary -> Output. Top-right icon: Lucide `Rss`.
* **Key Technical Facts:**
 * Ingestion begins via an RSS Read Node to pull the latest feed articles into an n8n array.
 * The raw array is processed using a "Limit" or "Split Out" node to restrict the payload to the Top 5 items, preventing excessive LLM token usage,.
 * These 5 items are fed into a "Loop Over Items" node. Inside the loop, an OpenAI node acts as an Information Extractor to generate individual summaries,.
 * An "Aggregate" node can then merge the five individual summary iterations back into a single unified JSON item for dispatch via Slack or Gmail,,.

---

📊 Slide 6. Block 6 (AI Engineer / Automation): Scaling n8n — self-hosted n8n Redis Queue Mode configuration for worker nodes.
* **Visual Layout Concept:** Light mode `HSL(210, 20%, 98%)`. Load balancer diagram showing a central n8n instance pushing tasks to a Redis queue, read by multiple worker nodes. Top-right icon: Lucide `Server`.
* **Key Technical Facts:**
 * For enterprise environments, standard n8n deployments are transitioned to "Queue Mode" utilizing external Redis memory.
 * This architecture decouples the main web process from execution by introducing multiple background worker processes (воркеры) that pull tasks from the Redis queue.
 * Queue mode enables infinite horizontal scaling, ensuring that high-volume parallel executions do not crash the primary Node.js memory heap,.

---

📊 Slide 7. Block 7 (Python Development): Writing Python scripts inside the n8n Code Node for complex data mappings.
* **Visual Layout Concept:** Dark mode `HSL(220, 15%, 16%)`. Monospace font snippet displaying Python `_input.all()` logic with syntax highlighting. Top-right icon: Lucide `Terminal`.
* **Key Technical Facts:**
 * While visual nodes excel at routing, complex ETL data transformations should be handled by the built-in "Code" node supporting Python or JavaScript,.
 * Executing the node "Run Once for All Items" allows Python to access the entire incoming dataset array via the `_input.all()` method,.
 * By writing defensive Python scripts utilizing `try/except` blocks and `.get()` dictionary methods, architects can programmatically map messy CSV/JSON inputs into sanitized formats, maximizing the LLM Signal-to-Noise Ratio,.

---

📊 Slide 8. Block 8 (AI Agent Builder / Agents & Harness): Designing Event-Driven visual automation architectures.
* **Visual Layout Concept:** Light mode `HSL(210, 20%, 98%)`. Directed Acyclic Graph (DAG) visualizing a Webhook triggering multiple parallel routes. Top-right icon: Lucide `Zap`.
* **Key Technical Facts:**
 * Production architectures abandon polling in favor of Event-Driven webhooks which listen passively on a URL,.
 * The fundamental event-driven skeleton is: Trigger (webhook) -> AI Decision (routing/extraction) -> Action -> Output.
 * To prevent the external sending system from timing out, n8n webhook nodes must be configured to respond immediately (HTTP 200 OK) rather than waiting for the entire cognitive AI loop to finish.

---

📊 Slide 9. Block 9 (AI Agent Builder / Agents & Harness): Managing API task queues to prevent Rate Limit (429) lockouts.
* **Visual Layout Concept:** Dark mode `HSL(220, 15%, 16%)`. Token bucket diagram illustrating throttled execution flow. Top-right icon: Lucide `ShieldAlert`.
* **Key Technical Facts:**
 * Executing hundreds of parallel API requests inside n8n will exhaust external token buckets, triggering HTTP 429 "Too Many Requests" errors,.
 * Architects must throttle workflows using a "Loop Over Items" node (Batch Size: 1) connected sequentially to a "Wait" node (e.g., 5 seconds) to respect provider limits,.
 * HTTP Request nodes must enable the "Retry On Fail" setting with Exponential Backoff, ensuring transient network rejections are gracefully re-attempted without crashing the entire DAG,.

---

📊 Slide 10. Block 10 (AI Agent Builder / Agents & Harness): Distributed state control: preventing data loss on crash.
* **Visual Layout Concept:** Light mode `HSL(210, 20%, 98%)`. Architecture flow showing execution state being saved to a Postgres table checkpoint. Top-right icon: Lucide `DatabaseBackup`.
* **Key Technical Facts:**
 * Volatile Node.js heap memory is unsuitable for long-horizon agent tasks (>60 seconds). Durable execution via external databases (e.g., PostgreSQL or SQLite) is mandatory,.
 * If a sub-workflow fails, n8n uses the "Error Trigger" node as a global error handler to capture the execution ID, node name, and traceback.
 * The system must execute a database `UPSERT` using a unique `run_id` after every major step, ensuring that if a container crashes, the workflow can resume exactly from the last saved state rather than starting over,.