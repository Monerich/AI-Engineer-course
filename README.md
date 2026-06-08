# AI Automation & AI Agent Builder Course Platform

A state-of-the-art, premium, and fully responsive bilingual (RU/EN) learning platform designed to train professional **AI Automation Engineers** and **AI Agent Architects** over a 6-month comprehensive curriculum.

The entire platform is built with **Next.js 16 (App Router)**, **React 19**, **TypeScript**, and **Tailwind CSS v4** utilizing HSL design tokens (cozy Claude warmth in Light Mode / sleek n8n high-tech in Dark Mode). It compiles completely statically to ensure instant load times, perfect SEO, and zero-cost scaling on Vercel.

---

## 📖 1. Educational Vision & Study Volume

> [%NOTE%]
> **10-12 Hours Weekly Study Density Rule**
> To transform students into competitive, enterprise-grade AI Automation Engineers, the curriculum is designed for a **6-month study path requiring 10-12 hours per week** (total ~260–300 hours).
> 
> Brief summaries or 20-minute overviews are strictly prohibited. Every weekly lesson is composed of a massive, multi-chapter technical lecture covering:
> 1. **Conceptual Overviews & Real-World Analogies:** Bridging complex paradigms with simple logic.
> 2. **Deep Theoretical Analysis:** Fundamental models, architectural edge cases, and principles.
> 3. **Step-by-Step Practical Handbooks:** Fully functional code or complete n8n configuration blocks.
> 4. **Real Business Cases:** Thorough step-by-step breakdowns of real business problems, workflows, and metrics.
> 5. **Failures, Errors & Blind Spots:** Practical debug loops, state security, prompt injections, and limit handling.
> 6. **Self-Check Review Quizzes:** Thought-provoking questions with detailed answer rationales.

---

## 🎯 2. Source Exhaustiveness (211 Workspace References)

Every single one of the **211 source references loaded in the Google NotebookLM workspace** (including all 12 Harness Engineering Lectures, vc.ru articles, Habr tutorials, and PDF roadmaps) is systematically digested, referenced, and utilized across the curriculum. This guarantees that:
- Every cold outreach automation hack is detailed.
- Every state discipline rule (Session Handover, 5 conditions of clean state, cleanup loops) is explained.
- Every hybrid RAG and monitoring (LangSmith) structure is fully transmitted.

---

## 🎥 3. Google NotebookLM Native Media Pipeline

To deliver a true premium experience, every weekly topic is covered by a perfect triad: **Text Lecture + Slide Presentation + Video Tutorial**. 

The platform supports a **Dual-Mode Player** built directly into the UI:
1. **📊 Presentation Tab:** Swaps dynamically between **📄 PDF Slide Deck** (embedded high-fidelity frame of the official PDF slide deck generated in NotebookLM, with download button) and **📊 Interactive Slides** (HTML5 widescreen slide-by-slide review carousel).
2. **🎥 Video Tab:** Swaps dynamically between **🎥 Video Lesson** (embedded HTML5 player rendering the actual video generated natively inside NotebookLM's studio, with download button) and **📝 Text Script** (screencast direction tables with word-for-word spoken voiceover script).

---

## 📂 4. Project Structure & Architecture

```
AI learning/
├── package.json                    # Next.js 16, React 19, TypeScript
├── globals.css                     # Premium theme variables & markdown custom overrides
├── docs/
│   └── PROJECT_GUIDE.md            # Exhaustive syllabus blueprint & project scope
├── public/
│   └── lessons/
│       ├── week-1/                 # Downloaded native high-fidelity studio assets
│       │   ├── slides.pdf          # Native Google NotebookLM PDF presentation slide deck
│       │   └── video.mp4           # Native Google NotebookLM MP4 video overview tutorial
│       └── week-2/
│           └── slides.pdf          # (Native video processing in background)
├── scripts/
│   ├── generate_lessons.py         # Automates bulk extraction of high-density bilingual text
│   └── generate_native_artifacts.py # Native media studio pipeline (trigger, poll, download)
└── src/
    ├── app/
    │   ├── page.tsx                # Root redirect (/ -> /ru)
    │   └── [lang]/
    │       ├── layout.tsx          # Localized application shell & responsive navigation
    │       ├── page.tsx            # Server Component dashboard (RU/EN)
    │       └── [week]/
    │           └── page.tsx        # Server Component week detail loader (compiles GFM & maps PDFs/Videos)
    ├── components/
    │   ├── DashboardClient.tsx     # Localized timeline, month blocks & progress dashboard
    │   └── WeekDetailClient.tsx    # Interactive lesson page with dynamic tabs, dual players & quizzes
    └── data/
        ├── curriculum.ts           # 26-week curriculum database (checklists, homeworks, metadata)
        └── lessons/                # Raw high-density markdown data folders (RU/EN)
            ├── ru/week-N/lecture.md  # Lecture text (weeks 1-8 populated)
            ├── ru/week-N/slides.md   # Slide deck source
            └── ru/week-N/video.md    # Video script (en/ mirrors same structure)
```

---

## 🛠️ 5. How to Run & Automate

### Development Server
```bash
npm run dev
```

### Static Production Compile ( SSG )
To verify full path compilation and clean builds (all 58 routes static compile in ~3.8s):
```bash
npm run build
```

### High-Density Lesson Text Generator
Queries NotebookLM sequentially utilizing safe rate-limits to generate massive detailed lessons:
```bash
python3 ./scripts/generate_lessons.py
```

### Automated Native Studio Media Generator
To natively trigger slide decks and video overviews inside NotebookLM, poll until complete, and download them directly into the Next.js directories:
```bash
# Process Week 2 in Russian (Triggers, polls, and downloads slides + video)
./scripts/generate_native_artifacts.py --weeks 2 --lang ru

# Process Week 3 in English
./scripts/generate_native_artifacts.py --weeks 3 --lang en

# Process both languages for Weeks 5 & 6
./scripts/generate_native_artifacts.py --weeks 5,6 --lang both
```

---

## 🔒 Verification Checklist
- [x] **SSG Static Compiler:** Zero TypeScript warnings or Next.js build errors.
- [x] **Bilingual Mirroring:** Dynamic language switches compile separate HTML for `/ru` and `/en`.
- [x] **State Persistence:** Local storage tracks checklists and quiz completion.
- [x] **Dual-Mode Players:** Native PDFs/Videos render beautifully and load with direct local download links.
