# Презентация: Introduction to Multi-Agent Systems: CrewAI

📊 Slide 1. Block 1 (AI Engineer / Automation): Multi-agent Primitives — role delegation, task breakdown, and tooling boundaries.
**Visual Layout Concept:** Dark mode background with neon blue accents. Use Lucide icons: `Users` (Roles), `ListTodo` (Tasks), and `Wrench` (Tools).
* **The Augmented LLM Foundation:** An agent is a language model enhanced with tools, memory, and an orchestration layer.
* **Role Delegation (Personas):** Assigning distinct personas (e.g., Product Manager, Programmer) dictates the perspective and outcomes of an agent's actions.
* **Task Breakdown & Boundaries:** Following "Lecture 07: Delineate clear task boundaries for agents," tasks must be rigidly scoped to prevent agents from attempting simultaneous, conflicting actions.
* **Tooling:** Tools act as the agent's keys to the outside world, allowing them to access real-time APIs, execute code, and perform actions beyond their training data.

---

📊 Slide 2. Block 2 (AI Engineer / Automation): Webhook Triggers — running CrewAI scripts via visual webhook calls.
**Visual Layout Concept:** Light mode layout with a webhook flowchart schema. Use the Lucide `Webhook` and `Play` icons.
* **Event-Driven Architecture:** Webhooks serve as the connective glue to initiate automated workflows from external software platforms.
* **n8n Trigger Integration:** Visual tools like n8n use Webhook Trigger nodes to capture incoming HTTP requests and start the execution cycle.
* **Passing Context:** The webhook payload captures the initial intent and data parameters, securely passing them to the Python execution environment to ignite the CrewAI script.

---

📊 Slide 3. Block 3 (AI Engineer / Automation): Dashboards for Crews — sending execution statuses and outputs to UI.
**Visual Layout Concept:** Split-screen layout showing backend processing vs. frontend UI dashboard. Use the Lucide `LayoutDashboard` icon.
* **Closing the Loop:** Once a CrewAI process completes, the system uses an HTTP Request or "Respond to Webhook" node to transmit the final results back to the client.
* **Front-End Control Centers:** Complex systems utilize custom dashboards to display real-time statuses (e.g., "In Progress", "Completed") and present the final deliverables.
* **Human-in-the-loop (HITL):** Dashboards can intercept the agent's workflow, allowing a human user to review intermediate data before approving the final output execution.

---

📊 Slide 4. Block 4 (AI Engineer / Automation): Payload Mappings — normalizing output structures for inter-agent communications.
**Visual Layout Concept:** Code block visualization demonstrating JSON schema. Use the Lucide `FileJson` icon.
* **Clean Handoff Principle:** Enforcing "Lecture 12: Clean handoff at the end of every session" ensures agents deliver precise, structured outputs rather than unstructured text.
* **Structured Output Parsers:** Utilizing JSON/Pydantic schemas guarantees that the output of one agent perfectly aligns with the required input parameters of the next agent.
* **Verification:** Implementing strict schemas prevents the "Verification Gap," ensuring the pipeline crashes safely if an agent hallucinates a malformed data structure.

---

📊 Slide 5. Block 5 (AI Engineer / Automation): Async Webhook Receivers — dynamic workers handling concurrent task triggers.
**Visual Layout Concept:** Network queue diagram showing parallel data streams. Use the Lucide `Network` icon.
* **Handling Concurrency:** As multi-agent swarms scale, asynchronous webhook receivers ensure the system can process multiple incoming triggers simultaneously without dropping requests.
* **Batching & Limiting:** Using tools like "Loop Over Items (Split in Batches)" and "Limit" nodes manages the flow of incoming data to prevent system overload.
* **Rate Limit Protection:** Async queues act as a buffer to protect external APIs (like OpenAI or Anthropic) from "Thundering Herd" HTTP 429 Too Many Requests errors.

---

📊 Slide 6. Block 6 (AI Engineer / Automation): Cloud CrewAI — deploying local python crews to Railway/Render instances.
**Visual Layout Concept:** Cloud server rack illustration. Use the Lucide `Cloud` and `Container` icons.
* **Moving to Production:** Transitioning an agent from a local script to a cloud instance (like Render or Railway) is mandatory for 24/7 availability.
* **The Ephemeral Disk Trap:** Cloud containers frequently restart. Relying on local storage for agent state leads to catastrophic amnesia.
* **Durable Execution:** State management must be externalized to robust PostgreSQL databases or S3 buckets to survive cloud container reboots.

---

📊 Slide 7. Block 7 (Python Development): CrewAI Python classes setup — initializing Agents, Tasks, and Crews structures.
**Visual Layout Concept:** Code snippet highlighting object-oriented class instantiation. Use the Lucide `Code` icon.
* **Agent Classes:** Defining the identity. Avoid "Instruction Bloat" (Lecture 04) by keeping the backstory concise and progressively disclosing rules.
* **Task Classes:** The rigid execution boundary. Setting strict `expected_output` parameters forces the LLM to verify its own work before completion.
* **Crew Assembly:** Combining `Agents` and `Tasks` into a `Crew` and utilizing the `kickoff()` method to orchestrate the swarm.

---

📊 Slide 8. Block 8 (AI Agent Builder / Agents & Harness): Multi-agent coordination patterns in enterprise pipelines.
**Visual Layout Concept:** Directed Acyclic Graph (DAG) and topology illustrations. Use the Lucide `Workflow` icon.
* **Workflow vs. Agent:** Workflows have hardcoded routing, while agents determine routing dynamically via LLM logic.
* **The 15x Token Tax:** Multi-agent architectures achieve superior results but heavily multiply token costs as context is passed back and forth.
* **Core Topologies:** Deploying architectures like Sequential (linear), Hierarchical (manager-led), Collaborative, and Competitive setups depending on task ambiguity.

---

📊 Slide 9. Block 9 (AI Agent Builder / Agents & Harness): Sequential vs Hierarchical routing containing custom Supervisor configurations.
**Visual Layout Concept:** Star-topology node graph featuring a central "Supervisor" node. Use the Lucide `GitMerge` icon.
* **Sequential Routing:** Deterministic, linear pipelines ideal for standardized operations where Agent A directly feeds Agent B.
* **Hierarchical Routing:** A dynamic "Manager/Orchestrator" Agent autonomously delegates sub-tasks to worker agents.
* **Cost-Performance Routing:** Deploying a flagship model (like Claude 3.5 Opus) as the Orchestrator for complex reasoning, while utilizing fast, cheap models (like Haiku or 4o-mini) for simple worker tasks.

---

📊 Slide 10. Block 10 (AI Agent Builder / Agents & Harness): Shared Memory systems for data retention across agent groups.
**Visual Layout Concept:** Database schema interacting with agent brain vectors. Use the Lucide `Database` icon.
* **The Amnesiac Genius:** "Lecture 05: Maintain context between sessions" solves the issue of LLMs forgetting previous executions.
* **Filesystem Ledgers:** Using shared markdown files (e.g., ``) as a durable, human-readable ledger that all agents can read and write to.
* **Vector & Relational DBs:** Implementing LangGraph PostgresSavers or Chroma DBs to manage long-term semantic and episodic memory, preventing agents from endlessly repeating failed tasks.