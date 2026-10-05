# Liquid fuels documentation viewer

Read-only replacement for the Streamlit viewer, aligned with the reference frontend in
`tender_scraper`: Next.js 16.2.10, React 19.2.7, TypeScript, Tailwind 4 and Radix UI.
Dependency versions are pinned and the lockfile is tracked. This frontend is a local
project choice; **project-canon was not changed for this migration**.

## Run locally

Node 22 or newer is required. From the repository root on Windows:

```powershell
cd frontend
npm.cmd ci
npm.cmd run dev
```

Open http://127.0.0.1:3100. On other platforms use `npm` instead of `npm.cmd`.
Port 3100 avoids colliding with the tender application's normal development port.

## Pages and content

| Page | Source |
|---|---|
| Overview | Repository README.md and the hypothesis-tree summary |
| Hypothesis tree | docs/methodology/demand_hypothesis_tree.md |
| Architecture | CLAUDE.md |

Next.js reads these files on the server for each request. Edit Markdown and refresh the
page; there is no duplicate content store, database, FastAPI service or model-execution endpoint.
Expandable sections use Radix Accordion. Markdown tables and code blocks use react-markdown
with remark-gfm; embedded HTML is skipped. Sources can be read through the three allowlisted
`/source/<document>` routes. Unknown keys return 404; arbitrary paths cannot be requested.

Set `LFM_DOCS_ROOT` to the absolute repository root if the source files live elsewhere.
The default assumes the process starts inside `frontend/`. `.env.example` documents this.
Missing source files produce an error page and `/health` returns 503.

## Verify and build

```powershell
npm.cmd test
npm.cmd run typecheck
npm.cmd run build
npm.cmd start
```

`npm start` serves the production build on 127.0.0.1:3100. Tests cover document refresh,
allowlisted source access, heading parsing, and Markdown rendering without raw HTML.

## Docker

From the repository root:

```powershell
docker compose up -d --build
```

Local Compose exposes port 3100. The base service listens on internal port 3000 for a
reverse proxy. Read-only documentation mounts keep Markdown edits visible on refresh.
The container contains only the frontend and the allowlisted documentation files.

This is an internal viewer without authentication, like its predecessor. Keep access
internal or use the existing hosting gateway. No hosting service or public deployment
was created by this migration.
