# Slides: Advanced Crews and Custom Tools in CrewAI

📊 Slide 1. Block 1 (AI Engineer / Automation): DB Tooling — wrapping complex SQL lookups as agent tools safely
**Visual Layout Concept:** HSL Dark Mode (`hsl(222, 47%, 11%)`). Lucide icons: `Database`, `ShieldCheck`. Schema showing an LLM natural language input converting to a secure SQL query.
* Agents can use specialized tools, such as an SQL executor, to securely convert natural language inputs into database queries.
* Safe database tooling requires strict access controls; never grant agents destructive permissions (e.g., DROP TABLE) and default to read-only access for data lookups.
* Provide the agent with precise database schemas and expected output formats so it can independently construct accurate SQL statements.

---
📊 Slide 2. Block 2 (AI Engineer / Automation): CRM Integrations — API tool hooks for multi-agent connections with HubSpot
**Visual Layout Concept:** HSL Light Mode (`hsl(210, 40%, 98%)`). Lucide icons: `Briefcase`, `Link`. Flowchart connecting an AI Agent node to a HubSpot API node.
* CRM platforms like HubSpot can be integrated as direct action nodes or custom agent tools within automated workflows.
* By packaging API requests into distinct tools, agents can dynamically decide when to pull customer records or update pipeline statuses during a conversation.
* Connecting a multi-agent system to a CRM enables complex workflows, such as autonomous lead qualification and automated email drafting based on live client data.

---
📊 Slide 3. Block 3 (AI Engineer / Automation): Context Passing — managing clean interim variables mapping
**Visual Layout Concept:** HSL Dark Mode (`hsl(222, 47%, 11%)`). Lucide icons: `ArrowRightLeft`, `Variable`. Stacked blocks demonstrating output variables mapping to the next agent's input.
* Prompt chaining involves passing the direct output of one specialized agent as the input for the next agent in the sequence.
* Breaking tasks down and passing limited, relevant context prevents the primary orchestrator agent from becoming overwhelmed by excessive data.
* Clean context passing ensures specialized agents (like an email drafter) only receive the precise variables they need, reducing hallucinations and API costs.

---
📊 Slide 4. Block 4 (AI Engineer / Automation): API Capping — rate limit managers preventing concurrent request bans
**Visual Layout Concept:** HSL Light Mode (`hsl(0, 0%, 100%)`). Lucide icons: `Timer`, `ShieldAlert`. Traffic light diagram showing request throttling.
* When spawning dozens of parallel agents (e.g., scraping hundreds of web pages simultaneously), you risk instantly hitting provider API rate limits.
* Implementing batching requests and controlled delays prevents wasted operations and ensures your concurrent requests do not trigger temporary bans.
* Utilizing tools with robust error handling and exponential backoffs allows the system to gracefully pause and retry rather than failing catastrophically.

---
📊 Slide 5. Block 5 (AI Engineer / Automation): Crew Economics — tracking and optimizing token fees per run
**Visual Layout Concept:** HSL Dark Mode (`hsl(222, 47%, 11%)`). Lucide icons: `Coins`, `TrendingDown`. Line chart comparing single-agent vs. multi-agent token burn.
* Multi-agent architectures (the orchestrator-worker pattern) typically burn around 15 times more tokens than a standard single-agent chat session.
* Use observability platforms like Langfuse to trace every LLM call, actively logging inputs, outputs, latency, and exact token costs per run.
* Optimize economics by routing simpler tasks to cheaper, faster models (e.g., Flash or Haiku) while reserving expensive reasoning models strictly for the orchestrator.

---
📊 Slide 6. Block 6 (AI Engineer / Automation): Visual Exports — compiling multi-agent outputs into markdown and PDF
**Visual Layout Concept:** HSL Light Mode (`hsl(210, 40%, 98%)`). Lucide icons: `FileText`, `LayoutTemplate`. Split screen showing raw JSON transforming into styled Markdown.
* You can explicitly define output formats in your system prompts, instructing the agent to generate well-structured Markdown with headers, bold text, and lists.
* For client-facing deliverables, prompt the agent to strictly follow HTML or Markdown formatting rules to ensure the final document compiles perfectly.
* Automated visual exports eliminate the need for manual data entry by taking raw agent reasoning and converting it instantly into polished reports or presentations.

---
📊 Slide 7. Block 7 (Python Development): Multi-agent State persistence utilizing PostgreSQL backends
**Visual Layout Concept:** HSL Dark Mode (`hsl(222, 47%, 11%)`). Lucide icons: `DatabaseZap`, `Save`. Database schema showing checkpoint saves.
* Production-grade multi-agent systems require durable execution, commonly implemented by saving the graph's state to a PostgreSQL database (e.g., PostgresSaver).
* Persistent state backends allow you to track the exact progression of a complex agent crew, enabling you to pause, rewind, or recover the workflow if a script crashes.
* Utilizing relational databases ensures memory and context are safely stored between sessions without permanently clogging the active LLM context window.

---
📊 Slide 8. Block 8 (AI Agent Builder / Agents & Harness): Resolving conflicts and contradictions in competing agent outputs
**Visual Layout Concept:** HSL Light Mode (`hsl(0, 0%, 100%)`). Lucide icons: `GitMerge`, `Scale`. Diagram of two worker nodes converging on a supervisor node.
* Deploying stochastic multi-agent consensus allows you to spawn multiple agents with the same prompt to debate, disagree, and statistically converge on the best solution.
* By parallelizing analyst agents with different framings or parameters, a lead agent can aggregate their competing recommendations to find edge cases.
* This debate framework pushes agents to higher-quality answers by forcing them to review each other's work and rectify contradictory logic.

---
📊 Slide 9. Block 9 (AI Agent Builder / Agents & Harness): QA loops in Crews: Writer agent -> Verifier agent -> Editor reviews
**Visual Layout Concept:** HSL Dark Mode (`hsl(222, 47%, 11%)`). Lucide icons: `ListChecks`, `UserCheck`. Linear flowchart passing from Writer -> Evaluator -> Editor.
* Sequential handoffs greatly improve accuracy by breaking a task into a specialized assembly line, such as an outline writer, an outline evaluator, and a final blog writer.
* A dedicated "Verifier" or "Evaluator" agent acts as a quality assurance gate, reviewing the previous agent's output against strict criteria before it moves forward.
* This focused QA loop reduces hallucinations and logic errors because the reviewing agent is solely prompted to find flaws, rather than trying to write and edit simultaneously.

---
📊 Slide 10. Block 10 (AI Agent Builder / Agents & Harness): Metrics and automated evaluations for complex crew completions
**Visual Layout Concept:** HSL Light Mode (`hsl(210, 40%, 98%)`). Lucide icons: `BarChart`, `TestTube`. CI/CD pipeline graphic displaying pass/fail metrics.
* Iterative improvement of multi-agent crews is impossible without deploying rigorous, automated evaluations (Evals).
* Build a "Golden Dataset" of 30-50 manually labeled questions, and use a superior model as an "LLM-as-a-judge" to score your crew's outputs against a strict rubric.
* Embedding trajectory evaluations directly into your CI/CD pipeline ensures that code merges are blocked if the agent's performance or pass rate regressions drop below an acceptable baseline.

***
Here is the complete outline for Week 14. Let me know if you are ready to expand on the specific code implementations for these multi-agent workflows, or if you'd like to move on to the next topic!