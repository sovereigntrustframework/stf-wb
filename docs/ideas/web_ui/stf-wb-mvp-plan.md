# STF‑WB MVP — Pragmatic Plan (Python-first, OpenAPI-first, Oracle-ready)

Date: 2026-01-07

Goal: ship an MVP that proves the full loop:
**Login (GitHub App, on behalf of user) → Select repo (personal/org) → Create Run → Execute Step(s) → Stream status (SSE) → Publish to Git**. [web:756][web:709]

Key constraint: do not waste time now, but keep a clean path to Rust and Oracle later. (Project context)

---

## 0) Guiding decisions (MVP)

### Must-have
- GitHub App integration with user attribution (“on behalf of user”). [web:756]
- Git as the only durable store for now (no DB migration burden).
- Server is the workspace and single-writer; UI never edits Git directly. (Project decision)
- Status updates via SSE (EventSource). [web:428]

### Explicitly defer
- Full-blown workflow engine / durable job queue.
- Rich editor/diff UI.
- Complex governance levels and strict monotonicity rules.

---

## 1) OpenAPI-first (important addition)

Contract-first development means defining the interface contract (e.g., OpenAPI for REST) before implementing it, so UI/backend can move in parallel and so later rewrites are less risky. [web:887]

### Deliverable: `openapi.yaml` early (Day 0–1)
Create a minimal OpenAPI spec that covers only:
- Auth endpoints (start/callback/logout)
- Project selection endpoints
- Run endpoints
- SSE endpoint (documented as `text/event-stream`)

Even if you don’t generate code, treat this file as the “single source of truth” for:
- request/response JSON shapes
- error format
- versioning rules (e.g., `/api/v1`)

### Why it matters for Python→Rust
If the OpenAPI contract is stable, Rust migration becomes “re-implement the same contract”, not “reverse-engineer behavior”. [web:887]

---

## 2) MVP architecture (Python now, Rust later)

### Backend (Python for MVP)
- Use Python for speed (auth flows + glue + iteration).
- Structure code into replaceable modules:
  - `auth/` (GitHub App user tokens, sessions)
  - `git_adapter/` (clone/branch/commit/pr/merge)
  - `jobs/` (step execution and scheduling)
  - `events/` (SSE broadcaster + event schema)
  - `domain/` (project/run/publication models + serialization)

### Realtime (SSE)
- Use SSE to push status updates; client uses `EventSource`. [web:428][web:709]

### Frontend (Vite SPA)
- Build as static assets into `dist/`. [web:150]

---

## 3) Oracle-ready deployment track (important addition)

Even though MVP runs locally, plan for Oracle by keeping these constraints:
- Configuration via environment variables (GitHub App keys, callback URLs, workspace path).
- Stateless API layer (except session store), so scaling later is feasible.
- Workspace storage: initially local disk; later can be Oracle VM disk / block volume.

### Concrete Oracle plan (later milestone)
- Run backend in a container (or systemd service on a VM).
- Serve the Vite `dist/` either:
  - by the backend (same origin, simplest cookies/SSE), or
  - by a static web server / CDN with API on subdomain (requires careful CORS+cookies for SSE). [web:428]
- Add a real session store (e.g., Redis) when moving beyond single-instance.

---

## 4) Milestones (updated)

### Milestone A — Contract + Walking Skeleton (Day 1–2)
Deliverables:
- `openapi.yaml` committed early. [web:887]
- Backend:
  - `GET /health`
  - `GET /events` (SSE): emit a `ping` every 1s. [web:428]
- Frontend: one page connects to `/events` and prints messages.

Acceptance:
- SSE works reliably in browser. [web:709]

---

### Milestone B — GitHub App user attribution auth (Day 2–3)
Deliverables:
- `/auth/start` and `/auth/callback` implementing GitHub App user token generation. [web:756]
- Server-side session cookie storing user identity (token stays server-side).

Acceptance:
- `GET /me` returns GitHub login/id fetched using the user token. [web:756]

---

### Milestone C — Repo selection (personal + org) (Day 3–4)
Deliverables:
- List available installations and repos; select one to become a Project.
- Record `(owner, repo, installation_id)` as project metadata.

Acceptance:
- Can select personal or org repo where app is installed.

---

### Milestone D — Git workspace + Run baseline (Day 4–5)
Deliverables:
- Clone repo into server workspace.
- Create `runs/<run-id>` branch, commit `run.json`.

Acceptance:
- Repo contains run branch with a commit attributable to the user.

---

### Milestone E — Step 0 stub + Publish (Day 5–7)
Deliverables:
- Run Step 0 (generate placeholder outputs) → commit.
- Publish:
  - MVP choice: PR + merge OR direct merge (pick simplest).
- SSE streams publish progress.

Acceptance:
- User can execute Step 0 and see results on `main`.

---

## 5) First tasks (next 2 hours)

1) Draft `openapi.yaml` (minimal) and commit it first. [web:887]
2) Implement `/health` + `/events` SSE endpoint (dummy events). [web:428]
3) Create minimal Vite page that connects using `EventSource`. [web:428][web:150]
4) Implement GitHub App user token flow (`/auth/start`, `/auth/callback`). [web:756]

---

## 6) MVP exit criteria

- GitHub App user attribution works (actions on behalf of user). [web:756]
- Works for both org and personal repos (where installed).
- Create run, execute step, stream status via SSE, publish to main. [web:709]
- Contract (`openapi.yaml`) matches behavior and is updated before interface changes. [web:887]