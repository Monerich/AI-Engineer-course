# AI Automation & AI Agent Builder Course Platform

This repository contains a bilingual Russian/English web application for a 26-week learning program focused on AI automation and AI agent development.

The app presents the curriculum as an interactive course workspace: learners can browse weekly materials, follow their progress, complete checklists, take quizzes, and review homework and resources.

## What is included

- Localized course pages for Russian and English (`/ru` and `/en`).
- A dashboard with the course timeline, months, weeks, and progress indicators.
- Weekly pages with:
  - lecture text;
  - slide outlines;
  - video lesson scripts;
  - topic navigation;
  - checklists, quizzes, homework, and resources.
- Course data and lesson materials in `src/data/`.
- The detailed curriculum and architecture reference in [`docs/PROJECT_GUIDE.md`](docs/PROJECT_GUIDE.md).
- Optional maintenance and content-generation utilities in `scripts/`.

Binary PDF source files are intentionally not stored in this repository. Slide and video content available in the app is represented by Markdown files and the application can use externally hosted media when configured.

## Project structure

```text
.
├── docs/
│   └── PROJECT_GUIDE.md       # Detailed curriculum and implementation guide
├── scripts/                   # Maintenance and content utilities
├── src/
│   ├── app/                   # Next.js routes for the dashboard and weekly pages
│   ├── components/            # Interactive course UI
│   └── data/
│       ├── curriculum.ts      # Curriculum, quizzes, checklists, and homework
│       └── lessons/           # Russian and English Markdown materials
├── public/                    # Static web assets
├── package.json
└── README.md
```

## Run locally

Install dependencies and start the development server:

```bash
npm install
npm run dev
```

Then open [http://localhost:3000](http://localhost:3000).

Useful checks:

```bash
npm run lint
npm run build
```

The project uses Next.js, React, TypeScript, Tailwind CSS, and `marked` for rendering Markdown lesson materials.
