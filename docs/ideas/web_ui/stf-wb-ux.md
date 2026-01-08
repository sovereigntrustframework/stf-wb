# STF‑Workbench Web UI — Concept & UX (MVP‑oriented)

Version: 0.1 (aligned with stf‑methodology‑v0.1.3 and stf‑workbench‑v0.1.2)
Scope: MVP web UI for STF‑Workbench, focusing on runs, steps, artefacts, coverage, and publications.

## 1. Overall layout

The UI follows a 3+1 panel layout, similar to IDEs and tooling workbenches:

1) **Top bar** — Global project/run status
2) **Left panel** — Project tree with switchable views
3) **Central panel** — Main viewer/editor (contextual)
4) **Bottom panel (optional)** — Log console with streaming events

This layout supports complex workflows while keeping context visible and is consistent with master/detail patterns commonly used in professional tools. [web:1118]

---

## 2. Top bar — Global status

The top bar acts as a **Global Status Bar** for the current project and selected Run. [web:1116]

### 2.1. Content

- **Project context**
  - Project name (mapped to GitHub repo)
  - Installation (GitHub account/org)
  - Current branch for the run (e.g., `runs/<run-id>`)

- **Run context**
  - Run label (e.g., “S0+S1 iteration 3”)
  - Run state: `created | running | blocked | failed | published`
  - Current step/gate (aligned with STF‑Methodology steps 0..N)

- **Health & synchronization**
  - Git sync status: `in sync with remote / ahead / behind / diverged`
  - Last sync time
  - Indicator if there are pending publications

- **Coverage & quality**
  - Coverage summary (as defined in STF‑M): e.g., % requirements with mapped properties/models
  - Number of open issues/warnings (validation results)

- **Primary actions**
  - `Sync` (pull/push via server, not from browser)
  - `Run step` (context-aware)
  - `Publish` (trigger publication workflow for the current run)

### 2.2. Behaviour

- The top bar updates via SSE events:
  - `run.status` (state transitions)
  - `git.sync` (sync progress)
  - `publish.progress` (publication stages) [web:428][web:709]
- Clicking on elements (e.g., coverage badge) can focus the left tree into the relevant view (e.g., Coverage View).

---

## 3. Left panel — Project tree and views

The left panel provides a **structured tree navigation** with multiple view modes. It is the primary way to explore a project, run, and artefact structure.

### 3.1. View modes

The UI offers at least three main view modes (tabs or dropdown):

1. **Methodology view** (Steps / Actions / Gates)
   - Root: current Run
   - Children:
     - Steps (S0, S1, …) as defined in stf‑methodology‑v0.1.3
     - Within each Step: actions, tasks, or sub‑activities aligned with STF‑M
   - Node badges:
     - State: `not started / in progress / completed / stale / failed`
     - Validation status (e.g., schema OK, consistency OK)

2. **Coverage view**
   - Root: top-level requirements set (from STF‑M)
   - Hierarchy: requirement → property → model, as per workbench spec v0.1.2
   - Node badges:
     - Coverage status (covered / partially covered / uncovered)
     - Links to runs/steps/artifacts that realize or validate each element

3. **Artifacts & dependencies view**
   - Root: artefact families (logical artefact IDs)
   - Children: versions of each artefact for this run
   - Each artefact node displays:
     - Fresh/stale state (based on dependency digests)
     - Step that produced it
     - A small indicator if there are downstream dependents

These views reflect the STF‑M focus on traceability (from methodology steps to artefacts and publications) and STF‑WB’s requirement for explicit artefact dependency graphs.

### 3.2. Interaction

- Clicking a node changes the **central panel** content to the appropriate viewer/editor.
- Context menu per node (right-click or “…”):
  - For Steps:
    - Run step
    - View logs
    - Open related artefacts
  - For Artefacts:
    - View details
    - View dependencies / dependents
    - Mark for recomputation (if stale)
  - For Requirements/Properties:
    - View linked artefacts and validations
    - Jump to latest run that touched this element

---

## 4. Central panel — Viewer/Editor

The central panel is the main **detail view**, driven by the selected node and the current run context.

### 4.1. Step view

When a Step (e.g., Step 0) is selected:

- **Header**
  - Step name + STF‑M reference (e.g., “S0 — Problem framing”)
  - Run and step state
- **Content sections**
  - Inputs:
    - Which artefacts / JSONs are consumed (with links)
    - Parameters for the step (config)
  - Outputs:
    - Artefacts produced (with states: fresh/stale)
    - Versions per publication
  - Execution controls:
    - `Run step`
    - `Re-run with changed inputs` (if upstream changed)
  - History:
    - Past executions within this run (timestamps, user, result)

### 4.2. Artefact view

When an artefact is selected:

- **Header**
  - Logical ID / path
  - Version identifier (hash, version number)
  - Producing step and run
- **Tabs**
  - **Content**: embedded viewer/editor for the JSON artefact
  - **Dependencies**:
    - List of dependencies (inputs) with digests and references
    - List of dependents (reverse graph), computed via scan or index
  - **Versions**:
    - All versions of this artefact in this run (and possibly across runs)
  - **Validation**:
    - Validation status (schema, consistency, coverage)

### 4.3. Gate / Publication view

When a gate or publication node is selected:

- Summary of:
  - Conditions for the gate (aligned with STF‑M gate definitions)
  - Inputs considered
  - Outputs and decisions made
- Publication metadata:
  - Linked PR(s) on GitHub
  - Commit SHAs
  - Status of required checks
- Action buttons:
  - Open PR
  - Re-evaluate gate with updated artefacts

---

## 5. Bottom panel — Log console

The bottom panel behaves like a **log console**, displaying streamed events and messages from the backend. [web:1110][web:1120]

### 5.1. Content types

- Step execution logs:
  - `run.started`, `step.started`, `step.completed`, `step.failed`
- Publish logs:
  - `publish.started`, `publish.progress`, `publish.completed`, `publish.failed`
- Validation messages:
  - Errors, warnings, info (e.g., schema violations, coverage gaps)
- System events:
  - Git sync, authentication, workspace events

All of these are fed by SSE events, and each event includes contextual IDs (project, run, step, artefact) so the console can link back to other panels. [web:428][web:709]

### 5.2. Features

- Filter controls:
  - `[x] Errors  [x] Warnings  [ ] Info  [ ] Debug`
  - Filter by run/step/artefact
- Click-to-navigate:
  - Clicking a log line focuses the relevant node in the left tree and opens the corresponding view in the centre.

---

## 6. SSE integration and live updates

The UI uses Server‑Sent Events for **one-way streaming** of state changes, consistent with earlier backend design. [web:428][web:709]

### 6.1. Event types (examples)

- `run.status` — updates top bar and central Step view
- `step.status` — updates Step node badges and console
- `artifact.status` — updates Artefacts view (fresh/stale)
- `publish.status` — updates top bar, central Gate/Publication view
- `log.line` — populates console

The SSE event schema is already reflected in the OpenAPI 3.2 `SseEvent` definition and should be kept aligned with these UI expectations.

---

## 7. User journeys (examples)

### Journey 1 — Investigate a gate failure

**Goal:** A reviewer wants to understand why a publication gate failed and what needs to change.

1. **Select project & run**
   - From a projects list, user selects a project, then a specific run.
   - Top bar shows run state `failed` and gate indicator “Gate Sx failed”.

2. **Navigate to gate**
   - In the left panel, switch to Methodology view.
   - Expand Steps → Gates and click the relevant gate node.

3. **Central panel — Gate view**
   - Central panel shows:
     - Gate conditions (as per STF‑M)
     - Summary of failing checks (e.g., missing coverage, validation errors)
     - Linked artefacts.

4. **See logs**
   - Bottom console is filtered automatically to show logs with `run_id` and gate-related events.
   - User can click a specific log line to jump to the problematic artefact or step.

5. **Drill down to artefact**
   - Left tree highlights the relevant artefact; user clicks it.
   - Central Artefact view shows content, dependencies, and validation errors.

6. **Plan remediation**
   - From Artefact view, user can:
     - Edit or schedule a new Step execution to regenerate the artefact.
     - Observe dependency impact (which other artefacts will become stale).

This journey demonstrates how the Methodology view, Artefact view, and console converge to tell a coherent story of failure and remediation.

---

### Journey 2 — Understand impact of changing an artefact (dependency cascade)

**Goal:** User modifies a foundational artefact (A) and wants to see what else becomes out-of-date.

1. **Select artefact A**
   - In Artifacts & dependencies view (left panel), user selects artefact A.

2. **Central panel — Artefact view**
   - Shows:
     - Content of A
     - `Dependencies` tab listing its inputs
     - `Dependents` tab listing artefacts that depend on A (reverse graph).

3. **Change A**
   - User edits A (or triggers a step that regenerates A) and saves.
   - Backend creates a new version (e.g., `A:v2`), updates digests.

4. **Cascade invalidation**
   - Backend recomputes stale status for dependents of A.
   - SSE emits `artifact.status` events for each affected artefact.

5. **UI updates**
   - Artefact nodes in the left tree show a “stale” badge.
   - Central panel for those artefacts shows `state: stale`.
   - Console logs an informational line summarizing “N artefacts became stale due to A update”.

6. **Rebuild downstream**
   - From Artefact view or Step view, user triggers recomputation for affected steps.
   - Progress is observed in the console and via status badges.

This journey shows explicit dependency management aligned with the graph-based thinking of STF‑Workbench, without requiring a separate graph DB at MVP.

---

### Journey 3 — Collaborative work on a shared Run (simultaneous users)

**Goal:** Multiple users contribute simultaneously to the same Run, each on different parts, without clashing.

1. **Run selection**
   - User A creates a run; User B and C later select the same run from the Project dashboard.

2. **Branches per user**
   - Under the hood, the backend assigns per-user branches (e.g., `runs/<run-id>/wip/<user>`).
   - UI does not expose raw branch names, but top bar shows “Run contributors: A, B, C”.

3. **User A edits Step 0 artefacts**
   - In Methodology view, A selects Step 0, edits relevant artefacts in the central panel.
   - Backend commits to A’s wip-branch; console logs “A updated artefacts in Step 0”.

4. **User B works on Step 1 models**
   - B selects Step 1, works on model artefacts.
   - Backend commits to B’s wip-branch.

5. **Run integration**
   - At certain points, backend integrates user branches into `runs/<run-id>` via merges once validations pass.
   - SSE events update:
     - Top bar (Run status)
     - Left tree (merged artefacts, stale flags)
     - Console (merge logs).

6. **Publication**
   - When Run is ready, someone triggers `Publish` from the top bar or Gate view.
   - A PR per publication is opened from `runs/<run-id>` to `main`, respecting the PR-per-publication strategy for clear audit trail.

This journey respects the single-writer server model, GitHub-based branch/PR workflows, and gives users a coherent UI for simultaneous contributions.

---

## 8. Alignment with STF‑M and STF‑WB specs

- **STF‑Methodology (v0.1.3)**:
  - Steps and gates appear explicitly in the Methodology view.
  - Coverage view maps back to STF‑M’s scoped coverage model (requirements → properties → models).
  - Gate evaluations and publication decisions are first-class entities in the UI, not just logs.

- **STF‑Workbench (v0.1.2)**:
  - Artefact graph (inputs/outputs per step) is surfaced in Artefacts & dependencies view.
  - Runs encapsulate executions over a given baseline/spec, with multiple publications per run.
  - Versioned artefacts with explicit dependency manifests support STF‑WB’s requirement for traceable, reproducible runs.

- **Previous web UI decisions**:
  - Backend as single writer, Git as source of truth.
  - SSE for live status updates, REST for commands. [web:428][web:709]
  - GitHub App auth and project selection are assumed as already established flows behind the UI.

---

## 9. Next UI steps

- Wireframe this 3+1 layout with:
  - Two or three real examples from existing STF specs (e.g., a concrete S0+S1 run).
- Validate journeys with:
  - “Investigate failed gate”
  - “Change artefact and see impact”
  - “Two users editing different steps”
- Use the OpenAPI contract to drive the exact data shapes used by:
  - Top bar
  - Left tree items
  - Central panel view models
  - SSE event handlers

This document should remain consistent with STF‑M and STF‑WB revisions; any change in methodology steps, artefact types, or coverage metrics must be reflected both in backend and UI models.
