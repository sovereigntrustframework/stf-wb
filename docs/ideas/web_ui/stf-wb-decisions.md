# STF‑WB — Decisions & Open Questions (Frontend, Backend, Git)

Last updated: 2026-01-07. [memory:719]

This document consolidates the current architecture decisions and the remaining open questions for the STF‑Workbench (stf‑wb) system across frontend, backend, and Git/GitHub workflows. [memory:719]

## Scope and guiding principles

### Decided
- GitHub is the source of truth for versioned artifacts, with `main` as the canonical branch. [memory:723]
- The system follows a single-writer model: users do not edit the repo directly; all repo mutations go through the stf‑wb backend (even in “local” mode). [memory:723]
- The server is the workplace (local-server or Oracle): the working copy lives on the server, while the UI acts as a client. [memory:723]

### Open questions
- What is the exact “offline story”: purely local-server with later sync, or always-online server with caching/resilience? [memory:724][memory:727]
- Should the system explicitly formalize “tenancy” (one server instance serving multiple users/orgs), and what isolation model is required? [memory:723]

---

## Frontend

### Decided
- The frontend is a static SPA (React + Vite) that can be deployed as static files. [web:150][web:167]
- The UI uses REST/JSON for commands, and Server‑Sent Events (EventSource) for continuous state updates. [web:428][web:709]
- The UI does not access the filesystem or Git directly; it treats the backend as the authority for workspace state and Git state (single-writer). [memory:723]
- The UI must expose: Projects, Runs per Project, and Publications per Run (timeline). [memory:719]

### Open questions
- MVP navigation: “Project dashboard with tabs (Runs/Baselines/Activity/Settings)” vs “Run-first global list with filters”. [memory:719]
- MVP interaction depth: thin UI (forms + state) vs richer UI (editor, diff viewer, previews). [memory:720]
- Publication visualization: display only snapshots (from `main` + ledger) vs also first-class PR links and PR metadata (checks, reviews). [memory:719]
- Realtime semantics: SSE as event stream + periodic/triggered `GET /state` reconciliation vs SSE carrying sufficiently rich deltas to avoid polling. [web:428][memory:719]
- Minimum MVP pages: which exact 3 pages define the first shippable UI (login/repo selection, project dashboard, run detail, etc.). [memory:719]

---

## Backend

### Decided
- Backend is responsible for all mutations of the workspace and for all Git operations (clone, branch management, commits, merges, sync). [memory:723]
- Two execution modes are targeted with the same API semantics:
  - Local-server mode for development/offline-friendly workflows.
  - Oracle-deployed mode for hosted usage. [memory:723][memory:727]
- Authentication/authorization direction:
  - GitHub OAuth for user login.
  - GitHub App for repository access (fine-grained permissions, installation-based access, short-lived tokens). [web:447][memory:728]
- Domain model conventions:
  - Project aggregates Runs and Baselines.
  - Baseline = provider raw spec + digest/hash.
  - Step 0 belongs to the Run (not the Baseline), since normalization/parameters may vary. [memory:719]
- Commit policy constraint: only commit/push when the versioned paragraph→requirement→property→model graph is intact, unique, and consistently versioned. [memory:725]
- **Validation execution**: Hybrid model
  - MVP: Server-side pre-commit validation (fast, synchronous feedback)
  - Post-MVP: GitHub Actions for authoritative CI validation (branch protection)
- **Session storage**: In-memory for MVP, Redis/similar for Oracle multi-instance deployment
- **Workspace strategy**: One isolated workspace per project; runs queued FIFO per project (no parallel execution in MVP)

### Open questions
- Git credential flow end-to-end: how the backend receives, stores (or avoids storing), and refreshes GitHub access in a way that does not require PATs and remains secure across local and Oracle deployments. [memory:722][memory:723]
- State model contract: exact shape of the “authoritative state” the UI consumes (project/run/publication status), and how it maps to GitHub primitives (commits/branches/PRs/check runs). [memory:719]
- Long-running jobs: how runs/steps are scheduled, retried, and surfaced to the UI (job IDs, progress, logs, resumability). [memory:719]

---

## Git / GitHub workflow

### Decided
- `main` is canonical and receives changes via merges; do not edit `main` directly. [memory:723]
- Each Run works on its own branch (e.g., `runs/<run-id>`). [memory:719]
- A Run can be published multiple times: multiple merges to `main` are allowed as “milestones” when outputs are audit-worthy and reusable. [memory:719]
- Branch protection is expected, with required status checks gating merges. [web:364]
- **PR strategy: One PR per publication/milestone** (clearer audit trail, supports out-of-order publications, better CI integration).

### Open questions
- “Level / milestone” definition:
  - Level as a derived property computed by validators vs
  - Level as an explicit action/intent (e.g., `publish?level=S4`)—deferred until MVP stabilizes. [memory:719]
- Publication ledger:
  - Store an explicit ledger in-repo (e.g., `runs/<run-id>/publications/<pub-id>.json`) vs
  - Derive publication history from Git commits/PR metadata alone. [memory:719]
- Monotonicity rules:
  - Allow out-of-order publications (e.g., S4 before S0) vs
  - Enforce sequencing / monotonic policy per methodology constraints. [memory:719]
- Required status checks design:
  - Which checks are mandatory,
  - How to handle checks that are not always executed,
  - Whether to require branches to be up-to-date before merging. [web:364][web:730]

---

## Next actions (to close open questions)

### Decided/Ready to implement
- ✅ MVP's 3 pages: Login/repo selection, Project dashboard (with runs list), Run detail (with step execution + publish)
- ✅ PR strategy: One PR per publication (not per run)
- ✅ Backend structure: FastAPI layer reusing existing `stfwb` CLI domain logic
- ✅ Validation: Server-side for MVP, GitHub Actions post-MVP
- ✅ Workspace: One workspace per project, FIFO run queue

### Still open (can defer to implementation)
- Publication ledger file (simplifies UI queries) — can add when needed
- Level/milestone formalization — defer until methodology stabilizes
- GitHub auth token refresh mechanism — implement as part of Milestone B
- Required status checks design — defer to post-MVP branch protection setup