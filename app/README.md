# SACU Liquid Fuels Model — documentation app

A Streamlit app that serves the model's documentation (hypothesis tree,
architecture, scope, status) at a URL your team can hit instead of cloning
the repo. The app is **read-only**: it doesn't run the model, doesn't
write outputs, and doesn't carry any state.

## Pages

- **Home** (`streamlit_app.py`) — "Why this exists", scope, segment status table.
- **Hypothesis Tree** (`pages/1_Hypothesis_Tree.py`) — per-segment driver
  decomposition, expandable. Source: `docs/demand_hypothesis_tree.md`.
- **Architecture** (`pages/2_Architecture.py`) — load-bearing decisions,
  scenario mapping, v1 build-out priorities. Source: `CLAUDE.md`.

Every page reads its content from the repo's markdown files at request
time, so editing `docs/*.md`, `README.md`, or `CLAUDE.md` flows through to
the running app on next reload. No duplicate docs to maintain.

## Run locally

From the repo root:

```powershell
pip install -e ".[app]"
streamlit run app/streamlit_app.py
```

The app opens at `http://localhost:8501`.

## Run via Docker Compose (primary path)

A `docker-compose.yml` is committed at the repo root. From the repo root:

```powershell
docker compose up -d            # build (first run) + start detached
docker compose logs -f          # tail logs
docker compose down             # stop and remove
```

Browse to `http://localhost:8501`. The compose file:

- Builds the image from `app/Dockerfile` (only on first run, or when code/deps change)
- Mounts `README.md`, `CLAUDE.md`, and `docs/` **read-only** into the container —
  edits to those files show up on the next browser refresh, no rebuild needed
- Sets `restart: unless-stopped` so the container survives host reboots
- Includes a healthcheck on `/_stcore/health` (30s intervals)
- Conservative resource caps (1 CPU, 512MB RAM) — adjust for your host

When to rebuild:
- `docker compose up -d --build` after any change under `src/lfm/`, `app/`,
  `assumptions/`, or `pyproject.toml`. Documentation edits do NOT need a rebuild.

## Run via plain Docker (no compose)

```powershell
docker build -f app/Dockerfile -t lfm-docs:latest .
docker run --rm -p 8501:8501 lfm-docs:latest
```

Equivalent to `docker compose up` but without the volume mounts (docs are
baked into the image) and without restart policy / healthcheck wiring.

## Deploy internally

The compose file works on any host with Docker installed — a VM, a
bastion, or as part of a larger Compose stack. For Kubernetes / ECS /
Cloud Run / Posit Connect, the image (`lfm-docs:latest`) is the unit;
push it to your registry and reference it from your platform's manifests.

Minimum requirements:

- Port `8501` exposed
- No external secrets; the app needs no API keys or database access
- Health endpoint: `GET /_stcore/health` returns 200 when alive

For Posit Connect specifically: push as a Streamlit content bundle
pointing at `app/streamlit_app.py`. The manifest needs streamlit + the
package's runtime dependencies (`pandas`, `pyyaml`, `openpyxl`); a
`requirements.txt` generated via `pip-compile pyproject.toml` is the
cleanest path.

For Posit Connect: push as a Streamlit content bundle pointing at
`app/streamlit_app.py`. The manifest needs streamlit + the package's
runtime dependencies (`pandas`, `pyyaml`, `openpyxl`). `requirements.txt`
generated from `pip-compile pyproject.toml` is the cleanest path.

## What's intentionally not in v1

- **Run outputs page** — current model CSVs (`runs/<tag>/`) are analyst-grade,
  not stakeholder-grade. Will be added when the output xlsx template is designed.
- **Sourcing log page** — `docs/params_sourcing.md` is currently maintained
  manually by the analyst team; surfacing it in the app would imply more
  rigorous status-tracking than v1 supports.
- **Authentication** — the app carries no sensitive data, so no auth in
  the image. If your hosting needs SSO, add it at the reverse-proxy layer.
