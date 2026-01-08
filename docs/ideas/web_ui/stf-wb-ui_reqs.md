# STF‑Workbench Web UI — Requirements (MVP)

Version: 0.1  
Scope: Functional & non‑functional requirements for the STF‑Workbench web UI MVP, aligned with:
- stf‑methodology‑v0.1.3
- stf‑workbench‑v0.1.2
- Python-first + OpenAPI-first + SSE backend architecture [web:887][web:428]

---

## 1. Global layout and navigation

### 1.1. Layout structure

**REQ‑LAYOUT‑01**  
The UI SHALL use a 3+1 panel layout:
- Top bar (global status)
- Left panel (tree navigation with multiple views)
- Central panel (contextual viewer/editor)
- Bottom panel (optional log console, collapsible) [web:1118][web:1120]

**REQ‑LAYOUT‑02**  
The layout SHALL be responsive enough to work on typical desktop/laptop resolutions (≥ 1280×720), with priority on horizontal layout (no mobile-first requirement for MVP).

**REQ‑LAYOUT‑03**  
The left panel width and bottom console height SHOULD be resizable by the user.

---

## 2. Top bar — Global project & run status

### 2.1. Project and run context

**REQ‑TOP‑01**  
The top bar SHALL always display:
- Selected project name (mapped to a GitHub repo)
- GitHub owner/installation (user/org)
- Selected run identifier (run ID and short label)

**REQ‑TOP‑02**  
The top bar SHALL display the current run state:
- `created`, `running`, `blocked`, `failed`, `published` (as per STF‑WB run model).

**REQ‑TOP‑03**  
The top bar SHALL display the current step/gate when the run is in `running` or `blocked` state (e.g., “S0”, “Gate Sx”). (Aligned with STF‑Methodology v0.1.3.)

### 2.2. Sync & publication status

**REQ‑TOP‑04**  
The top bar SHALL show Git sync status for the project’s workspace:
- `in sync`, `ahead`, `behind`, or `diverged` relative to the remote default branch.

**REQ‑TOP‑05**  
The top bar SHALL expose a `Sync` action that triggers a server-side sync (pull/push) for the project workspace; the UI MUST NOT perform Git operations directly. [web:364]

**REQ‑TOP‑06**  
The top bar SHALL display information about the last successful publication for the current run (timestamp + link to PR/commit if available).

### 2.3. Coverage and quality

**REQ‑TOP‑07**  
The top bar SHALL display at least one coverage metric aligned with STF‑Methodology, e.g.:
- percentage of requirements that have mapped properties/models in the current run.

**REQ‑TOP‑08**  
The top bar SHALL display a summary of validation issues (e.g., counts of errors/warnings) aggregated at run level.

---

## 3. Left panel — Project tree and views

### 3.1. View modes

**REQ‑NAV‑01**  
The left panel SHALL support at least three view modes:

1. Methodology View (Steps / Actions / Gates)  
2. Coverage View (Requirements → Properties → Models)  
3. Artifacts & Dependencies View (Artefact graph flattened into a navigable hierarchy)

**REQ‑NAV‑02**  
The view mode SHALL be switchable via tabs or a dropdown in the left panel header.

### 3.2. Methodology view

**REQ‑NAV‑03**  
Methodology View SHALL reflect STF‑Methodology v0.1.3:

- Root node: current run
- Children: methodology steps (S0, S1, S2, …)
- Optionally nested actions or sub-activities per step (if defined in STF‑M)

**REQ‑NAV‑04**  
Each step node SHALL display:

- Step identifier (e.g. “S0”)
- Short title (from methodology/spec)
- State badge: `not started`, `in progress`, `completed`, `stale`, `failed`.

**REQ‑NAV‑05**  
If gates are defined in the methodology for a step, the UI SHALL represent them as children or siblings of that step (e.g., “Gate Sx”).

### 3.3. Coverage view

**REQ‑NAV‑06**  
Coverage View SHALL represent:  
`Requirement → Property → Model`, as per STF‑WB v0.1.2’s graph structure.

**REQ‑NAV‑07**  
Each node in Coverage View SHALL display:

- ID and label (requirement/property/model)
- Coverage status (covered / partially covered / uncovered)
- Optional link to the latest run/step that updated coverage.

### 3.4. Artifacts & dependencies view

**REQ‑NAV‑08**  
Artifacts & Dependencies View SHALL list logical artefact families and their versions for the current run.

**REQ‑NAV‑09**  
Each artefact node SHALL display:

- Logical artefact identifier (e.g., path or ID)
- Version (hash or version number)
- State badge: `fresh` or `stale` based on dependencies.

**REQ‑NAV‑10**  
The UI SHOULD visually indicate if an artefact has downstream dependents (e.g., small icon or count).

### 3.5. Node interaction

**REQ‑NAV‑11**  
Clicking any node in the left panel SHALL update the central panel with a context-specific view:

- Step node → Step view
- Gate node → Gate/Publication view
- Requirement/Property/Model node → Coverage detail view
- Artefact node → Artefact view

**REQ‑NAV‑12**  
Nodes SHALL provide a context menu (or equivalent) with actions such as:

- For Steps:
  - Run step
  - View logs
  - Open related artefacts
- For Artefacts:
  - View details
  - View dependencies & dependents
  - Mark for recomputation
- For Requirements/Properties/Models:
  - View linked artefacts
  - View last run that affected this node

---

## 4. Central panel — Viewer/Editor

### 4.1. Step view

**REQ‑STEP‑01**  
When a step is selected, the central panel SHALL show:

- Step header:
  - Step ID (e.g., “S0”) and STF‑M title
  - Associated run
  - Current state
- Inputs section:
  - List of artefacts/inputs used by this step
  - Step parameters (if any)
- Outputs section:
  - List of artefacts produced by this step (with fresh/stale status)
- History:
  - Previous executions of this step in the run (timestamp, user, status)

**REQ‑STEP‑02**  
The Step view SHALL provide controls to:

- Trigger execution of the step (Run step)
- Re-run the step with updated inputs (recompute).

### 4.2. Artefact view

**REQ‑ART‑01**  
When an artefact is selected, the central panel SHALL show:

- Header:
  - Logical artefact ID and version
  - Producing step/run
- Content tab:
  - JSON representation (viewer; editor if editing is allowed in MVP)
- Dependencies tab:
  - List of direct dependencies (inputs) with identifying data and digests
  - List of direct or transitive dependents (if available)
- Versions tab:
  - List of versions of this artefact in the current run (and optionally across runs)
- Validation tab:
  - Schema and consistency validation results

### 4.3. Gate / Publication view

**REQ‑GATE‑01**  
When a gate or publication is selected, the central panel SHALL show:

- Gate description and conditions (from STF‑M)
- Inputs considered in the decision
- Outputs/decisions (accepted/rejected, rationale)
- Linked GitHub PR(s) / commits for the publication:
  - PR number
  - Status (open/merged/closed)
  - Required checks status [web:364]

**REQ‑GATE‑02**  
From this view, the user SHALL be able to:

- Open the corresponding PR in GitHub (if created)
- Trigger re-evaluation of the gate (if artefacts changed and backend exposes such action).

---

## 5. Bottom panel — Log console

### 5.1. Displayed content

**REQ‑CONSOLE‑01**  
The console SHALL display log events received from the backend via SSE:

- Run events (run started/finished)
- Step events (step started/completed/failed)
- Publication events (publish started/progress/completed/failed)
- Validation messages (errors/warnings/info)
- System events (sync, auth issues, workspace errors) [web:428][web:709]

**REQ‑CONSOLE‑02**  
Each log entry SHALL include at least:

- Timestamp
- Severity: `error | warning | info | debug`
- Context IDs: `project_id`, `run_id`, optionally `step_id`, `artifact_id`
- Message text

### 5.2. Filtering and navigation

**REQ‑CONSOLE‑03**  
The console SHALL provide filtering options:

- By severity (checkboxes)
- By run (dropdown or filter)
- Optionally by step or artefact

**REQ‑CONSOLE‑04**  
Clicking a log entry SHOULD focus the relevant node in the left panel and update the central panel to the corresponding context (if resolvable).

**REQ‑CONSOLE‑05**  
The console SHALL be collapsible; collapsed state SHOULD be persisted per session.

---

## 6. SSE-driven live updates

### 6.1. Event handling

**REQ‑SSE‑01**  
The UI SHALL establish an SSE connection to `/events` after authentication and project/run selection. [web:428][web:709]

**REQ‑SSE‑02**  
The UI SHALL handle at least the following logical event types:

- `run.status` (updates top bar run state and Step view)
- `step.status` (updates Step node badges and central Step view)
- `artifact.status` (updates Artefact node badges and central Artefact view)
- `publish.status` (updates Gate/Publication view and top bar)
- `log.line` (append to console)

**REQ‑SSE‑03**  
On SSE disconnect, the UI SHALL attempt reconnection with backoff; the UI SHOULD indicate temporary disconnection.

### 6.2. Consistency

**REQ‑SSE‑04**  
Whenever an SSE event updates the UI state, subsequent REST reads for the same entity (run, step, artefact, gate) SHALL return a state consistent with the event (modulo eventual latency).

---

## 7. Runs, collaboration and Git model (UI assumptions)

### 7.1. Run selection and context

**REQ‑RUN‑01**  
The UI SHALL provide a way to select:

- a project (GitHub repo where the STF artefacts live)
- a run within that project.

**REQ‑RUN‑02**  
Once selected, project and run context SHALL remain visible (in the top bar) until changed by the user.

### 7.2. Collaboration on runs

**REQ‑RUN‑03**  
The UI MUST support the concept that multiple users can work on the same run simultaneously, assuming backend uses a “branch-per-user” strategy under the hood. [web:1072]

**REQ‑RUN‑04**  
The top bar (or a suitable place) SHOULD display which users are currently active contributors to the run (e.g., “Contributors: userA, userB”).

**REQ‑RUN‑05**  
The UI SHALL not expose raw Git branch names directly to users in the MVP; these are an implementation detail of the backend.

### 7.3. Publication model (PR per publication)

**REQ‑RUN‑06**  
The UI SHALL assume a **PR per publication** model:

- Each publication from a run corresponds to a distinct PR from the run branch to `main`.
- The Publication/Gate view SHALL show links to these PRs and their status. [web:1073]

---

## 8. Authentication and session UX

### 8.1. Entry and login

**REQ‑AUTH‑01**  
If the user is not authenticated, the UI SHALL show a login entry screen with a button to initiate GitHub/App authorization.

**REQ‑AUTH‑02**  
After successful login, the UI SHALL show a project/run selection screen before loading the main 3+1 layout.

### 8.2. Session state

**REQ‑AUTH‑03**  
The UI SHALL rely on a session cookie for auth; it SHALL NOT store GitHub tokens in the browser (these remain server-side).

**REQ‑AUTH‑04**  
On session expiry or 401 responses from the API, the UI SHALL redirect to the login screen or show a clear “session expired” message with a button to re-login.

---

## 9. Non-functional requirements (UI-focused)

**REQ‑NF‑01**  
The UI SHALL be implemented as a static SPA (e.g., React + Vite build to `dist/`) and assume a separate API origin is possible (CORS-friendly). [web:150]

**REQ‑NF‑02**  
The UI SHOULD avoid heavy client-side state duplication of server models; it SHOULD treat the server as the source of truth and rely on SSE + REST for synchronization.

**REQ‑NF‑03**  
Errors and validation messages SHOULD be user-readable and clearly differentiate between:
- Backend/system errors
- Validation/schema errors
- Methodology/gate violations

**REQ‑NF‑04**  
The UI SHOULD be usable primarily with keyboard + mouse, but detailed accessibility optimizations are not required for MVP (can be added later).

---

## 10. Alignment with STF‑Methodology and STF‑Workbench

**REQ‑ALIGN‑01**  
All references to steps, actions, gates, and artefact types in the UI MUST be consistent with the definitions in stf‑methodology‑v0.1.3 and stf‑workbench‑v0.1.2.

**REQ‑ALIGN‑02**  
Coverage View MUST reflect the requirement/property/model structure defined by STF‑Workbench, and coverage metrics displayed in the top bar MUST be derivable from this model.

**REQ‑ALIGN‑03**  
The Run and Publication concepts in the UI MUST match the STF‑Workbench definitions:
- A Run as an execution container over a baseline/spec
- One Run MAY have multiple publications (PR per publication model).

---

## 11. Open questions (to be resolved in design/implementation)

- **UI editing rights**: which artefacts are editable in the MVP (all vs subset vs read-only).
- **Granularity of Artefact nodes**: large monolithic JSON vs smaller files per logical artefact.
- **Gate re-evaluation UX**: automatic on artefact changes vs explicit user-triggered re-evaluation.

These points SHOULD be resolved before implementing the first production-ready version of the UI, but the above requirements remain valid regardless of the chosen answers.
