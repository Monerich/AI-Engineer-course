# Презентация: Security, Injections and Sandboxes

📊 Slide 1. Block 1 (AI Engineer / Automation): Conceptual LLM Security — categorizing major large language models vulnerabilities.
*Visual Layout Concept:* Dark mode (Slate 900) with red accents, Lucide `ShieldAlert` icon.
*Key bullet points:*
* Categorize threats into intrinsic (LLM brain vulnerabilities) and extrinsic (environment/memory interactions).
* Protect against primary attack vectors including jailbreaks, direct and indirect prompt injection, and data poisoning.
* Recognize that increased agent autonomy naturally expands the attack surface, requiring comprehensive threat mitigation.

---
📊 Slide 2. Block 2 (AI Engineer / Automation): Webhooks Sanitization — input filters checking webhook payloads for malicious content.
*Visual Layout Concept:* Light mode (Zinc 50), payload inspection flowchart, Lucide `Filter` icon.
*Key bullet points:*
* Mitigate indirect prompt injections originating from external webhooks, web pages, or retrieved RAG documents.
* Implement rigorous input sanitization and filtering at the system level to neutralize malicious patterns before they are processed by the LLM.
* Treat all incoming webhook data as untrusted until verified by a security classifier.

---
📊 Slide 3. Block 3 (AI Engineer / Automation): System Prompt Protections — prompt architecture guards against system leakage.
*Visual Layout Concept:* Split layout (attack vs defense), dark mode, Lucide `Lock` icon.
*Key bullet points:*
* Prevent attackers from extracting hidden instructions or defining personas via System Prompt Stealing attacks.
* Avoid exposing sensitive business logic, API routing instructions, or custom rules to end users.
* Utilize layered defenses and careful context management to ensure prompt architecture remains confidential.

---
📊 Slide 4. Block 4 (AI Engineer / Automation): OWASP Top 10 for LLMs — practical implementation of safety standards.
*Visual Layout Concept:* Ordered list layout, high-contrast HSL borders, Lucide `ListChecks` icon.
*Key bullet points:*
* Adhere strictly to the OWASP Top 10 for LLM Apps to establish production-ready security baselines.
* Enforce absolute rules: never commit keys to GitHub and utilize secure credential systems (e.g., n8n vault).
* Sanitize all user inputs before LLM processing and distrust LLM outputs for critical operations.

---
📊 Slide 5. Block 5 (AI Engineer / Automation): Setting up Guardrails — configuring Llama Guard and NeMo input/output rails.
*Visual Layout Concept:* Diagram showing an LLM centered with layered protective shields, Lucide `Shield` icon.
*Key bullet points:*
* Validate outputs for correctness, factual accuracy, and safety using tools like NeMo-Guardrails.
* Layer multiple specialized classifiers (e.g., relevance, PII filters, moderation) to proactively flag off-topic or unsafe queries [14-16].
* Treat guardrails as a layered defense mechanism where rules-based checks run concurrently with LLM-based safety evaluators.

---
📊 Slide 6. Block 6 (AI Engineer / Automation): Database Permission Capping — isolating agent access to tables and API keys.
*Visual Layout Concept:* Database architecture with locked tables, Lucide `Database` icon.
*Key bullet points:*
* Enforce the principle of least privilege to prevent unauthorized database migrations, malicious data extraction, or file deletions.
* Ensure agents only possess the exact database roles necessary to complete their specific assigned task.
* Isolate execution environments so agents cannot access or expose host environment variables and API keys.

---
📊 Slide 7. Block 7 (Python Development): Executing dynamically generated Python code inside E2B Sandbox or Daytona SDK.
*Visual Layout Concept:* Code terminal inside a container box, dark mode (Gray 800), Lucide `TerminalSquare` icon.
*Key bullet points:*
* Never execute `exec()` of model outputs directly in the main host process.
* Run all untrusted generated code within ephemeral, isolated sandboxes like Modal, E2B, or Daytona to prevent host compromise.
* Destroy the execution environment completely after the task to maintain strict session integrity.

---
📊 Slide 8. Block 8 (AI Agent Builder / Agents & Harness): Security-first agentic operating system interaction paradigms.
*Visual Layout Concept:* Dual-classifier Auto Mode pipeline schema, Lucide `Cpu` icon.
*Key bullet points:*
* Utilize Auto Mode architectures with fast transcript classifiers to gate dangerous or overeager tool calls before execution.
* Implement prompt-injection probes to screen external tool results before they re-enter the main agent's context window.
* Ensure credentials are never reachable from the sandbox where the agent's code runs.

---
📊 Slide 9. Block 9 (AI Agent Builder / Agents & Harness): Custom network policies and sandbox isolation boundaries.
*Visual Layout Concept:* Network VPC diagram with egress blocking, Lucide `Network` icon.
*Key bullet points:*
* Define strict network boundaries using custom container templates and precise unrestricted/restricted network parameters.
* Prevent server-side request forgery (SSRF) and data exfiltration by blocking lateral movement across your internal VPC.
* Control outbound traffic with proxies or DNS filters to allow only necessary package downloads.

---
📊 Slide 10. Block 10 (AI Agent Builder / Agents & Harness): Obligatory Human-in-the-loop triggers before file deletions or transactions.
*Visual Layout Concept:* User approval prompt intersecting an automated workflow line, Lucide `UserCheck` icon.
*Key bullet points:*
* Mandate Human-in-the-Loop (HITL) interrupts for any irreversible, destructive, or high-risk actions.
* Require manual confirmation before executing financial transactions, sending external emails, or modifying production schemas.
* Use mechanisms like LangGraph's `interrupt()` or Claude Agent SDK permission prompts to smoothly pause and resume execution.

---

Would you like to review specific implementation details for the E2B sandboxes, or should we proceed to the next module?