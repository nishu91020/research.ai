**Research Agent Pro**

A lightweight research assistant web app that gathers, extracts, and produces concise summaries of information across multiple fields (science, law, engineering, business, healthcare, and more). The agent ingests heterogeneous sources, extracts key facts and arguments, and returns a short, well-cited summary with provenance.

**Project Overview**
- **Purpose:**: Provide researchers and knowledge workers a single interface to collect, condense, and cite information from multiple sources in a clear, readable summary.
- **Target users:**: researchers, analysts, students, product teams, and domain experts who need quick, accurate briefs.
- **Key features:**: multi-domain support, source provenance, concise summaries, configurable extraction pipeline, and an interactive frontend.

**Quick Start**
- **Install dependencies:**: Run the following from the project root to install packages.

```powershell
npm install
```

- **Run (development):**: Start the Vite dev server.

```powershell
npm run dev
```

- **Build/Preview:**

```powershell
npm run build
npm run preview
```

Note: This project uses Vite (`vite`) as shown in `package.json`.

**Usage**
- **Open the app:**: Visit the local dev server URL (usually `http://localhost:3000`) and use the UI.
- **Workflow:**: Enter your query in the sidebar or chat input, then ask the agent to research. The agent will:
  - ingest relevant sources,
  - extract and normalize key information,
  - create a concise summary (3–6 sentences by default), and
  - append source citations and provenance.
- **Output:**: A short, actionable summary with links or references back to original sources.
