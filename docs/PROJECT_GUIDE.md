# Project Guide: AI Automation & AI Agent Builder Course Platform

Welcome to the official technical guide and architecture documentation for the **AI Automation & AI Agent Builder** course platform. This platform is designed to provide a comprehensive, 6-month (26-week) professional curriculum that transforms tech-literate students into proficient AI Automation Engineers and AI Agent Architects.

---

## 📖 1. Project Vision & Target Audience

- **Core Goal:** Build a state-of-the-art, high-premium, responsive, and bilingual (RU/EN) learning platform containing a rigorous 6-month roadmap, interactive readiness checklists, self-validating quizzes, detailed homework projects, and exhaustive lesson content (including lectures, slide outlines, and video scripts).
- **Target Audience:** Tech-literate professionals (e.g., product managers, business analysts, operations managers, hobbyists) who understand LLMs and basic computers but do not have a formal computer science or deep coding background.
- **Tone & Style:** Explanations must be highly accessible, relying on vivid real-world analogies, step-by-step logic, and clear schematics, without over-complicating technical jargon.
- **Time Commitment & Depth Rule:** Designed for a 6-month study path requiring **10-12 hours per week** (total ~260-300 hours).
  > [!IMPORTANT]
  > **Crucial Volume & Depth Rule:** To guarantee a true 10-12 hours weekly study density, each week's materials must be **extremely comprehensive, highly detailed, and voluminous**. Brief summaries or 20-minute overviews are strictly unacceptable. Lectures must contain exhaustive step-by-step tutorials, extensive real-world business cases, full and detailed code or n8n configuration blocks, and clear deep-dive breakdowns.
- **Source Exhaustiveness Rule:** Every single one of the **211 source references loaded in the NotebookLM workspace** (including all 12 Harness Engineering Lectures, vc.ru articles, Habr tutorials, and PDF roadmaps) must be fully digested, referenced, and utilized across the weekly curriculum to ensure that the core essence, value, and practical automation hacks are completely transmitted to the student.

---

## 🛠️ 2. Technology Stack & Vercel Readiness

The platform is designed to compile statically to ensure **instant load times, perfect SEO, and zero-cost scaling on Vercel**:

1. **Framework:** Next.js 16 (App Router) + React 19 + TypeScript.
2. **Styling:** Tailwind CSS v4 utilizing high-end HSL design variables.
   - **Light Mode (Claude Warmth):** Cozy, paper-like cream-beige backgrounds (`#F7F4EF`), soft warm gray panels (`#F1ECE4`), and dark charcoal typography (`#1F1F1F`).
   - **Dark Mode (n8n High-Tech):** Deep obsidian-black backgrounds (`#0D0D11`), steel-gray borders (`#1F2026`), and bright neon-red/orange accents (`#FF5E4B`).
3. **Icons:** Lucide React (sleek outline stroke icons).
4. **Build Strategy:** Statically pre-rendered (SSG) via `generateStaticParams` for all 58 routes (`/`, `/ru`, `/en`, and `/ru/week-1` to `/en/week-26`), ensuring it deploys seamlessly to Vercel.

---

## 📂 3. Codebase Structure

```
AI learning/
├── package.json                    # Dependencies: React 19, Next.js 16, Lucide
├── tsconfig.json                   # TypeScript config
├── next.config.ts                  # Static optimization settings
├── globals.css                     # Premium global variables & animations
├── docs/
│   └── PROJECT_GUIDE.md            # This project guide & documentation
├── public/                         # Static assets & images
├── scripts/
│   ├── generate_lessons.py         # NotebookLM CLI lesson generator (uv run)
│   └── generate_native_artifacts.py # Slides & video pipeline
└── src/
    ├── app/
    │   ├── page.tsx                # Root redirect (/ -> /ru)
    │   └── [lang]/
    │       ├── layout.tsx          # Localized application shell & header
    │       ├── page.tsx            # Server Component dashboard (RU/EN)
    │       └── [week]/
    │           └── page.tsx        # Server Component week detail loader
    ├── components/
    │   ├── DashboardClient.tsx     # Localized timeline & monthly course roadmap
    │   └── WeekDetailClient.tsx    # Interactive lesson page with dynamic tabs
    └── data/
        ├── curriculum.ts           # 26-week database of meta, quizzes, and homeworks
        └── lessons/                # Detailed lecture, presentation & video markdown data
            ├── ru/
            │   ├── week-1/
            │   │   ├── lecture.md  # Full lecture text (RU)
            │   │   ├── slides.md   # Slide deck source
            │   │   └── video.md    # Video script
            │   └── ...             # Weeks 1-20 populated (see content status below)
            └── en/
                └── ...             # Mirror structure (not yet generated)
```

---

## 📊 4. Content Status

### Russian lecture files (`src/data/lessons/ru/`)

| Weeks | Status |
|-------|--------|
| 1-15, 18, 20 | Complete: lecture (~1500-2700 lines) + curriculum.ts (checklist 10 items, quiz 3-4 questions, homework 5-6 steps) |
| 16 | Lecture exists but only 5 of 10 blocks (NotebookLM rate limit hit during generation). Curriculum complete. |
| 17 | Stub only (~184 lines). Curriculum exists. |
| 19 | No lecture. Curriculum exists. |
| 21-25 | No lectures. Curriculum exists. |
| 26 | Stub only (~148 lines). Curriculum exists. |

### English lecture files
Not yet generated. Mirror structure expected.

---

## 📚 5. Exhaustive 6-Month Bilingual Syllabus

The course blends **No-Code Automation** (Months 1-2) with **AI Agentic Coding** (Months 3-6):

| Month | Focus | Modules | Core Projects |
| :--- | :--- | :--- | :--- |
| **Month 1** | **Foundations of AI & API Integration** | **W1:** Web Tech (APIs, REST, JSON, Webhooks)<br>**W2:** Context Engineering & Prompts<br>**W3:** n8n Foundations, Docker, PostgreSQL<br>**W4:** Case Study: Telegram Parser + LLM Routing | **Project 1:** Build a personal automated Telegram message classifier in n8n. |
| **Month 2** | **No-Code AI Workflows & Orchestration** | **W5:** n8n Loops, Sub-workflows, Queue Mode<br>**W6:** n8n AI Nodes, Memory, Custom Tools<br>**W7:** Vector Databases & RAG in n8n<br>**W8:** Cold Outreach Automation Case | **Project 2:** Knowledge-based customer support chat assistant with Pinecone + n8n. |
| **Month 3** | **Python & Custom Agentic Programming** | **W9:** Web Scraping (Playwright, BeautifulSoup)<br>**W10:** OpenAI/Anthropic SDK, Structured Outputs, Pydantic V2<br>**W11:** ReAct Loop from scratch, Tool Registry, FastAPI<br>**W12:** Autonomous CLI Agent with Rich UI, SQLite memory | **Project 3:** Custom CLI search and file organizer agent running locally in Python. |
| **Month 4** | **Multi-Agent Orchestration & Graphs** | **W13:** CrewAI — Agents, Tasks, Crews, memory=True<br>**W14:** Advanced CrewAI — DB tools, QA chains, eval<br>**W15:** LangGraph — StateGraph, checkpointers, PostgresSaver<br>**W16:** Advanced LangGraph — HITL, Time-Travel (5 blocks) | **Project 4:** Multi-agent research & copywriter department running locally. |
| **Month 5** | **Production Observability & State Management** | **W17:** Hybrid Search & Chunking Strategy *(stub)*<br>**W18:** Observability — OTEL, @traceable, LangSmith, Langfuse<br>**W19:** Prompt Monitoring & Guardrails *(no lecture)*<br>**W20:** State Discipline, Session Handover, PostgreSQL checkpoints | **Project 5:** Fully monitored and evaluated enterprise support agent. |
| **Month 6** | **Deployment, Security & Capstone** | **W21:** Docker, FastAPI & Cloud Deployment *(no lecture)*<br>**W22:** Prompt Injection & Security Guardrails *(no lecture)*<br>**W23:** Voice Agents & Multimodal *(no lecture)*<br>**W24-26:** Capstone Project *(no lecture)* | **Capstone Project:** Production-grade autonomous multi-agent department solving a business case. |

> **Note on missing topics:** Prompt Caching and Fine-tuning vs RAG decision framework are not yet covered in any existing lecture. These should be added to W19 or W20 when those lectures are generated.

---

## 📝 6. Lecture File Format & Conventions

### Required structure for every `lecture.md`

```markdown
# Неделя N: Название недели

## О чём эта неделя

[2-3 paragraphs describing what the week covers across the two tracks]

**Треки 1-6 (AI Automation / n8n):** ...
**Треки 7-10 (Python / AI Agent Builder):** ...

После этой недели вы сможете:
- ...

---

## Блок 1: Название блока

[content]

## Блок 2: Название блока
...
## Блок 10: Название блока
```

**Rules:**
- Exactly one `# Неделя N:` title at the top — never repeated inside the file
- Exactly 10 `## Блок N:` headings per week (with a colon after the number)
- One `## О чём эта неделя` section between title and first block
- Blocks 1-6: n8n / automation track; Block 7: Python; Blocks 8-10: AI agents / Harness

### Block navigation (how clickable topics work)

1. `curriculum.ts` → `topics[]` strings matching `"Блок N (...): title"` pattern
2. `WeekDetailClient.tsx` regex `^(?:Блок|Block)\s+(\d+)` → renders topic as a scroll button
3. `[week]/page.tsx` post-processes HTML after `marked.parse()` to inject `id="lecture-block-N"` into matching `<h2>` tags
4. Click: switches to lecture tab, then `scrollIntoView({ behavior: "smooth" })` with 50ms delay

### `cleanNotebookLmMarkdown()` — NotebookLM output cleaner

Located in `src/app/[lang]/[week]/page.tsx`. Runs on every `.md` file before `marked.parse()`. Handles:
- **JSON unwrapping:** NotebookLM sometimes returns content as `{"value": {"answer": "..."}}` — extracted automatically
- **Footnote stripping:** `[1]`, `[1, 2]` references removed
- **PDF filename replacement:** Internal PDF names (`agent_roadmap_ru.pdf`) replaced with readable phrases

### Known NotebookLM output artifacts to fix manually

When generating new weeks via NotebookLM/`generate_lessons.py`, check for and fix:
- `## Глава N:` headings → rename to `## Блок N:`
- `# Неделя N.` title repeated before every block → keep only the first
- `## N. Блок N (Role): title` numbered heading format → clean to `## Блок N: title`
- `# Лекция N.` + `# Неделя N.` double title at top → remove the `# Неделя N.` line
- `**Лекция 11: ...**` inside Python code blocks → convert to `# Лекция 11: ...` (Python comment)
- Markdown links `[Text](url")` inside Python string literals → replace with plain URL

### Known code quality issues to check in generated lectures

- `response.choices.message.content` → must be `response.choices[0].message.content`
- `Field(enum=[...])` in Pydantic V2 → use `Literal["a", "b"]` instead
- `$input.item.json` in n8n Code Node → use `$input.first().json`
- `_input.all()` in n8n Code Node → use `$input.all()`
- `from langgraph.checkpoint.sqlite import SqliteSaver` → use `MemorySaver` or `langgraph-checkpoint-sqlite` package
- All fields accessed via `state.get("field_name")` in LangGraph nodes must be declared in `AgentState`

---

## 🎯 7. NotebookLM CLI & Lesson Generation Pipeline

To gather granular material from the 211 private sources loaded in your NotebookLM workspace (ID: `5a520c9c-d47f-4354-95b1-8d208079f55d`), we utilize the fast package manager `uv` and the command-line interface `nlm`:

- **Command Syntax:**
  `nlm query notebook 5a520c9c-d47f-4354-95b1-8d208079f55d "<PROMPT>"`
- **Generate lessons script:**
  `uv run python scripts/generate_lessons.py 3,4` (comma-separated week numbers)
- **Semantic Extraction & 10-12 Hours Study Volume Strategy:**
  We query the notebook to extract precise concepts and methodologies, including:
  1. *n8n workflows* from Russian vc.ru and Habr articles.
  2. *Harness Engineering architectures* (Lecture 1-12 of "Learn Harness Engineering"): time-travel, checkpoints, evaluations, states, and debugging.
  3. *Prompt/context parameters* for n8n AI integrations.
- **Upgraded High-Volume Lectures Prompt:**
  To guarantee that the learning materials represent a real 10-12 hours of weekly study density, the generator prompt forces NotebookLM to write extremely comprehensive, structured lectures in 6 required chapters:
  1. *Conceptual Overview & Analogies* (historical context, real-world analogies, why this matters).
  2. *Deep Theoretical Analysis* (fundamental principles, core concepts, edge cases).
  3. *Step-by-step Technical Manuals* (fully functional code or n8n configuration blocks).
  4. *Real Business Cases* (minimum 2 detailed real-world scenarios showing the exact problem, step-by-step solution, and results).
  5. *Failures, Errors & Blind Spots* (prompt injections, rate limits, state discipline, and debug loops).
  6. *Summary & Self-check Questions* (review questions with answers explained).

---

## 🖥️ 8. Lesson Presentation Layout (The Tab System)

Each `week` detail view renders a beautiful, premium **Tab Controller** with three main tabs:

1. **📖 Lecture (Лекция):** Exhaustive text explanation of the weekly topics with interactive sidebars, diagrams, and clear real-world examples.
2. **📊 Presentation Slides (Презентация):** A slide-by-slide learning carousel outlining key concepts with highly legible bullet points, ideal for review or teaching.
3. **🎥 Video Tutorial Script (Сценарий видео):** A professional script/outline for a video lesson, including spoken text and visual cues (e.g., "[Show Screen: n8n Editor]").

---

## 📊 9. curriculum.ts Quality Standard

Every week entry in `curriculum.ts` must have:

```typescript
{
  checklist: [
    "Блок 1: Я [concrete action]...",  // 10 items, one per block, action-oriented
    // ...
  ],
  quiz: [
    {
      question: "...",
      options: ["A", "B", "C", "D"],  // exactly 4 options
      answerIndex: 1,                  // 0-indexed (NOT "correct" or "correctAnswer")
      explanation: "..."
    }
    // 3-4 questions
  ],
  homework: {
    title: "...",
    description: "...",
    steps: [
      "Step 1...",  // 5-6 steps, verifiable actions
    ]
  },
  resources: [
    { name: "...", url: "https://..." },  // 5-6 items with real URLs
  ]
}
```

---

## 📋 10. Verification & Quality Assurance Checklist

To guarantee absolute professional quality before launching to Vercel:
- [ ] **Build Validation:** Run `npm run build` to confirm zero TypeScript compilation warnings and successful generation of all 58 dynamic routes.
- [ ] **Lecture format:** Each week has `# Неделя N:`, `## О чём эта неделя`, exactly 10 `## Блок N:` headings.
- [ ] **Curriculum quality:** 10-item checklist, 3-4 quiz questions with `answerIndex`, 5-6 step homework, 5-6 resources.
- [ ] **Code correctness:** No `response.choices.message` without `[0]`, no `Field(enum=[...])`, no `_input.all()`.
- [ ] **State Persistence:** Verify that ticking a checklist item or completing a quiz successfully updates `localStorage` and reflects in the main dashboard's progress bar.
- [ ] **Bilingual Mirroring:** Ensure all 26 weeks are completely filled out in both Russian and English, maintaining an identical level of detail and formatting.
- [ ] **Responsiveness:** Test layout sizing from standard mobile screens (375px) up to ultra-wide desktop monitors (2560px).
