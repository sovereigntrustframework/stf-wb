# STF Specification

**The Sovereign Trust Framework (STF) Specification**

---

<a id="STF-WB-CL-000001"></a>
# Sovereign Trust Framework Workbench Specification (STF-WB)

<a id="STF-WB-CL-000002"></a>
**Version:** 0.2.0  
<a id="STF-WB-CL-000003"></a>
**Status:** Draft  
<a id="STF-WB-CL-000004"></a>
**Role in STF:** Tooling/workbench specification that operationalizes STF-M executions and publishes auditable evidence artifacts.  
<a id="STF-WB-CL-000005"></a>
**Normative dependency:** STF-M (methodology workflow) and STF-Spec (framework requirements). See Section 12 (References) for formal citations.  
<a id="STF-WB-CL-000006"></a>
**This document:** Uses RFC 2119 keywords (MUST/SHOULD/MAY).

---

<a id="STF-WB-CL-000007"></a>
## Change log (informative)

- v0.2.0 Draft: MINOR version increment with significant normative changes. Applied 8 critical blockers: formalized deterministic validation semantics (Section 9.1), completed coverage computation algorithm (Section 6.4.1), structured artifact input format (Section 6.5), explicit gate derivation rules (Section 6.6), enumerated immutability mechanisms with snapshot_type field (Section 6.2.1), iteration state transition rules with state_history tracking (Section 6.3.1), added Security and Privacy Considerations sections (Sections 10–11), and relaxed commit-per-artifact to allow action-level batching (Section 7). Implemented 5 strategic enhancements: defined artifact class schemas S0.A through S5.A (Section 6.5.1–6.5.6), added error handling and retry semantics (Section 8.1), created formal References section (Section 12), added Abstract section, and defined scope adequacy guidance (Section 6.4.2). Applied editorial standardization: capitalized defined terms, standardized JSON field formatting, formalized citations, clarified environment namespace semantics, and updated CLI placeholder syntax.

- v0.1.0 Draft: Initial clause-first MVP for projects, iterations, evidence storage layout, and structured scope/coverage metrics.

---

## Abstract (informative)

This specification defines a minimal, auditable workbench data model and storage layout for executing the STF methodology (STF-M) against target specifications and publishing evidence artifacts. The workbench provides operationalization of the STF-M workflow (Steps 0–5) through structured data models (Project, Iteration, Artifact, GateResult, ScopeSpec), repository layout conventions, and formalized deterministic validation requirements. This specification enables third-party verification of formal specification work and supports iterative evidence collection while maintaining audit integrity. Optional profiles allow implementation flexibility across serialization formats and storage backends.

---

<a id="STF-WB-CL-000008"></a>
## 1. Scope and purpose (normative)

<a id="STF-WB-CL-000009"></a>
This specification defines a minimal, auditable workbench data model and storage layout for executing the STF methodology (STF-M) against a target specification and publishing evidence artifacts.  
<a id="STF-WB-CL-000010"></a>
This specification is primarily concerned with (a) Project and Iteration lifecycle, (b) Artifact identity and validation, (c) structured Scope and coverage metrics, and (d) evidence publication to a shared GitHub repository.  
<a id="STF-WB-CL-000011"></a>
This specification does not mandate a specific formal method, prover, programming language, UI technology, or database engine.

---

<a id="STF-WB-CL-000012"></a>
## 2. Normative language (normative)

<a id="STF-WB-CL-000013"></a>
The key words MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are to be interpreted as described in RFC 2119 [RFC2119], consistent with STF drafting guidance.  
<a id="STF-WB-CL-000014"></a>
Implementations claiming conformance to this specification MUST satisfy all requirements labeled as normative in this document.

---

<a id="STF-WB-CL-000015"></a>
## 3. Conformance and profiles (normative)

<a id="STF-WB-CL-000016"></a>
An implementation is STF-WB-conformant iff it implements the required data model objects and produces/publishes the required Artifacts with deterministic validation as specified herein.  
<a id="STF-WB-CL-000017"></a>
This specification defines a core profile and optional profiles to allow evolution without breaking interoperability, following SemVer practices recommended for STF-faithful specifications.

<a id="STF-WB-CL-000018"></a>
### 3.1 Core profile (normative)

<a id="STF-WB-CL-000019"></a>
An implementation conforming to **profile:core** MUST implement: Project, Iteration, Artifact, GateResult, and ScopeSpec objects, plus the evidence repository layout rules in Section 7.  
<a id="STF-WB-CL-000020"></a>
An implementation conforming to **profile:core** MUST be able to publish Artifacts in a machine-readable form with deterministic validation methods whose execution is documented.

<a id="STF-WB-CL-000021"></a>
### 3.2 Serialization profiles (normative)

<a id="STF-WB-CL-000022"></a>
The workbench MUST NOT require JSON as the only serialization format; however, this v0.2.0 draft defines **profile:serialization-json** as the default interoperable profile for the MVP.  
<a id="STF-WB-CL-000023"></a>
An implementation claiming **profile:serialization-json** MUST serialize required objects as JSON and MUST provide deterministic validation for those JSON documents.

<a id="STF-WB-CL-000024"></a>
### 3.3 Interface profiles (informative)

- **profile:interface-cli**: Recommends CLI commands for managing projects/iterations and publishing evidence.

<a id="STF-WB-CL-000025"></a>
### 3.4 Storage profiles (normative)

<a id="STF-WB-CL-000026"></a>
This v0.2.0 draft defines **profile:storage-github-shared-repo** for publishing evidence into a single shared GitHub repository organized by Project slug.  
<a id="STF-WB-CL-000027"></a>
An implementation claiming **profile:storage-github-shared-repo** MUST conform to the layout and publication rules in Section 7.

---

<a id="STF-WB-CL-000028"></a>
## 4. Terminology (normative)

<a id="STF-WB-CL-000029"></a>
**Workflow (STF-M workflow):** The abstract, methodology-defined process comprising steps, actions, and gates (Step 0–5) as defined by STF-M.  
<a id="STF-WB-CL-000030"></a>
**Project:** A persistent workbench container that groups multiple Iterations against a target specification identity and publication configuration.  
<a id="STF-WB-CL-000031"></a>
**Iteration (Run):** A concrete instantiation of the STF-M workflow applied to a specific target snapshot and a specific Scope declaration, producing auditable evidence Artifacts.  
<a id="STF-WB-CL-000032"></a>
**ScopeSpec:** A structured declaration of what parts of the source snapshot are in scope for an Iteration, designed to enable Scope and coverage metrics.  
<a id="STF-WB-CL-000033"></a>
**Artifact:** A machine-readable object produced or used during STF-M steps, with deterministic validation.  
<a id="STF-WB-CL-000034"></a>
**GateResult:** A machine-readable record of a step gate evaluation outcome derived from action outcomes.

---

<a id="STF-WB-CL-000035"></a>
## 5. Global requirements (normative)

<a id="STF-WB-CL-000036"></a>
A workbench MUST preserve explicit, auditable traceability across Artifacts and source fragments, and MUST publish evidence such that a third party can inspect and re-run documented validation steps on the same inputs.  
<a id="STF-WB-CL-000037"></a>
All workbench Artifacts required by this specification MUST be machine-readable and MUST have a deterministic validation method; any permitted non-determinism MUST be explicitly documented.  
<a id="STF-WB-CL-000038"></a>
The workbench MUST support iterative execution, including revisiting steps and retry transitions, while preserving traceability and recording retries.

---

<a id="STF-WB-CL-000039"></a>
## 6. Data model (normative)

This section defines the minimum required fields for interoperable evidence publication under **profile:serialization-json**.

<a id="STF-WB-CL-000040"></a>
### 6.1 Common fields (normative)

<a id="STF-WB-CL-000041"></a>
Every required JSON object defined in this document MUST include:
- `kind` (string): stable identifier for the object type
- `version` (string): schema version for that object (SemVer)
- `id` (string): stable identifier for the object instance within its namespace
- `created_at` (string): ISO-8601 timestamp

<a id="STF-WB-CL-000042"></a>
### 6.2 Project object (normative)

<a id="STF-WB-CL-000043"></a>
A Project MUST be represented as a JSON object with `kind = "stfwb.project"`.  
<a id="STF-WB-CL-000044"></a>
A Project MUST include:
- `project_id` (string): immutable internal identifier (UUID recommended)
- `project_slug` (string): immutable, URL-safe slug chosen by the operator
- `target` (object): identity of the target specification (see below)
- `storage` (object): evidence repository locator (see below)

<a id="STF-WB-CL-000045"></a>
The `target` object MUST include:
- `source_identity` (string): URI-like identifier for the target spec (repo URL, doc URL, etc.)
- `description` (string, optional)

<a id="STF-WB-CL-000046"></a>
The `storage` object MUST include:
- `provider` = "github"
- `repo` (string): `owner/repo`
- `branch` (string): branch name
- `base_path` (string): base directory path within the repo for this Project, derived from the slug (Section 7)

<a id="STF-WB-CL-000046a"></a>
#### 6.2.1 Immutability mechanisms (normative)

<a id="STF-WB-CL-000046b"></a>
Projects MUST include a `source_snapshot` object within the Project metadata that references the target specification version. The `source_snapshot` object MUST include both a snapshot identity and an immutable reference selected from the following acceptable mechanisms:

(a) **Cryptographic hash:** SHA-256 or stronger hash of the canonical specification content. Implementations MUST record the hash algorithm name (e.g., "sha256") in a `hash_algorithm` field.

(b) **Git commit SHA:** A commit SHA from a stable, version-controlled repository. Implementations MUST record the repository URL and branch/ref in `git_repo` and `git_ref` fields.

(c) **Timestamped DOI:** A Digital Object Identifier assigned to an immutable archive (e.g., Zenodo, IPFS). Implementations MUST record the DOI and archive timestamp.

<a id="STF-WB-CL-000046c"></a>
A `snapshot_type` field MUST be included to indicate which mechanism is used: `"hash" | "git_commit" | "doi"`. Implementations MUST NOT use mutable URLs (e.g., unversioned HTTP endpoints) for immutability references. The immutability reference MUST enable third-party auditors to obtain the identical specification content for re-validation purposes.

---

<a id="STF-WB-CL-000047"></a>
### 6.3 Iteration object (normative)

<a id="STF-WB-CL-000048"></a>
An Iteration MUST be represented as a JSON object with `kind = "stfwb.iteration"`.  
<a id="STF-WB-CL-000049"></a>
An Iteration MUST include:
- `iteration_id` (string): immutable identifier
- `project_id` (string): parent Project internal identifier
- `scope` (ScopeSpec object or reference)
- `source_snapshot` (object): snapshot identity and immutability reference
- `status` (string): `created | in_progress | frozen | archived` (minimum set)
- `created_at` (string): timestamp

<a id="STF-WB-CL-000050"></a>
The `source_snapshot` object MUST include a snapshot identity and an immutable reference (hash, git SHA, or DOI) consistent with STF-M Step 0 input requirements. The snapshot MUST be immutable and identifiable such that third-party auditors can verify they are inspecting identical source material.  
<a id="STF-WB-CL-000051"></a>
The `scope` MUST be structured and MUST enable Scope and coverage metrics, consistent with STF-M's requirement that a Scope statement be declared for each Iteration.

<a id="STF-WB-CL-000051a"></a>
#### 6.3.1 Iteration state transitions (normative)

<a id="STF-WB-CL-000051b"></a>
Iteration state transitions are constrained to preserve audit integrity. The following transitions are allowed:

- `created` → `in_progress` when the first action is executed
- `in_progress` → `frozen` when the final gate result is accepted (all gates passed)
- `frozen` → `archived` when transitioning to long-term storage (read-only, no further modifications allowed)

All other transitions are prohibited. Attempts to transition in prohibited directions MUST be rejected by the workbench.

<a id="STF-WB-CL-000051c"></a>
A `state_history` array MUST be included in the Iteration object. Each entry in `state_history` MUST record:
- `from_state` (string): the previous state
- `to_state` (string): the new state
- `timestamp` (string): ISO-8601 timestamp of the transition
- `reason` (string, optional): explanation or action that triggered the transition

Archived Iterations MUST NOT be modified or unfrozen under any circumstances. Unfreezing a frozen Iteration is strictly prohibited and indicates audit compromise if observed.

---

<a id="STF-WB-CL-000052"></a>
### 6.4 ScopeSpec object (normative)

<a id="STF-WB-CL-000053"></a>
A ScopeSpec MUST be represented as a JSON object with `kind = "stfwb.scope"`.  
<a id="STF-WB-CL-000054"></a>
A ScopeSpec MUST include:
- `scope_id` (string): stable identifier
- `mode` (string): `include` (v0.2.0 defines include-only mode)
- `selectors` (array): structured selectors (see below)
- `metrics` (object): Scope metrics and coverage metrics fields (see below)
- `assumptions` (array of strings, optional)

<a id="STF-WB-CL-000055"></a>
Each selector in `selectors` MUST be one of:
- `{ "type": "source_fragment_id", "ids": ["SRC-...", "..."] }`
- `{ "type": "source_path_range", "path": "…", "start": "...", "end": "..." }`
- `{ "type": "source_section", "section_id": "..." }`

<a id="STF-WB-CL-000056"></a>
The `metrics` object MUST include:
- `scope_size` (object): `{ "unit": "fragments|sections|lines|tokens", "value": number }`
- `coverage` (object): `{ "unit": "fragments|sections", "covered": number, "total": number, "gaps": ["SRC-XXX", "..."] }`

<a id="STF-WB-CL-000057"></a>
Coverage metrics MUST be computed against the declared Scope and MUST allow reporting gaps, aligning with STF-M Gate S1 requirements that coverage relative to Scope is stated.

<a id="STF-WB-CL-000057a"></a>
#### 6.4.1 Coverage computation algorithm (normative)

<a id="STF-WB-CL-000057b"></a>
Coverage metrics MUST be computed using the following algorithm:

**covered:** Count of unique source fragment IDs that appear in the `inputs` arrays of all published Artifacts for this Iteration. A fragment is counted as covered if at least one Artifact traces it directly or derives results from it.

**total:** Count of all source fragment IDs that match the expanded selector set. For `source_fragment_id` selectors, total includes all explicitly listed fragments. For `source_path_range` and `source_section` selectors, total is the count of source fragments within those ranges/sections.

**gaps:** Array of source fragment IDs that appear in the total set but do not appear in the covered set. All gaps MUST be explicitly listed.

<a id="STF-WB-CL-000057c"></a>
The GateResult for each Iteration MUST include the computed `gaps` array. If `gaps` is non-empty, the gate MUST NOT accept unless the Iteration's assumptions array includes an explicit justification for each gap (e.g., "SRC-042: excluded due to ambiguous specification language"). Operators MUST document exclusion rationale for all uncovered fragments.

<a id="STF-WB-CL-000057d"></a>
#### 6.4.2 Scope adequacy guidance (normative)

<a id="STF-WB-CL-000057e"></a>
To prevent scope gaming and ensure meaningful verification, implementers SHOULD achieve minimum coverage targets: at least 80% of normative clauses in the target specification should be included in Scope. If Scope covers fewer than 80% of normative clauses, the operator MUST document explicit justification in the assumptions field (e.g., "Scope limited to Section 3–4 due to resource constraints").

<a id="STF-WB-CL-000057f"></a>
Gate acceptance criteria SHOULD check that `coverage.covered / coverage.total >= 0.80` or higher to promote comprehensive verification. Implementers MAY use tighter thresholds (e.g., 90% or 100%) for high-assurance applications.

---

<a id="STF-WB-CL-000058"></a>
### 6.5 Artifact object (normative)

<a id="STF-WB-CL-000059"></a>
Every published Artifact MUST be represented as a JSON object with `kind = "stfwb.artifact"` or as a domain Artifact class object that includes the required Artifact metadata defined in this clause.  
<a id="STF-WB-CL-000060"></a>
Every Artifact MUST include:
- `artifact_id` (string): stable identifier
- `artifact_class` (string): e.g., `S0.A`, `S1.A`, etc.
- `produced_by` (object): `{ "step": "S0|S1|S2|S3|S4|S5", "action": "A0.1|...|A5.7|manual" }`
- `inputs` (array): structured references to upstream Artifacts and source fragments (see Section 6.5.0)
- `validation` (object): deterministic validation method reference and last result

<a id="STF-WB-CL-000060a"></a>
#### 6.5.0 Artifact input reference format (normative)

<a id="STF-WB-CL-000060b"></a>
The `inputs` array MUST contain structured reference objects, not bare strings. Each input reference MUST be a JSON object with the following fields:

```json
{
  "type": "artifact" | "source_fragment",
  "id": "<artifact_id or source_fragment_id>",
  "trace_kind": "direct" | "derived"
}
```

- `type`: Indicates whether the input is an upstream Artifact or a source specification fragment
- `id`: The identifier of the referenced Artifact or source fragment
- `trace_kind`: Specifies the nature of the reference:
  - `"direct"`: The Artifact includes or verbatim incorporates the referenced input
  - `"derived"`: The Artifact is the result of analysis, transformation, or synthesis based on the referenced input (e.g., formalization of a requirement, proof of a property)

This structured format enables automated dependency graph reconstruction and precise provenance tracking for third-party auditors.

---

<a id="STF-WB-CL-000060c"></a>
#### 6.5.1 Artifact class S0.A: Source snapshot metadata (normative)

<a id="STF-WB-CL-000060d"></a>
S0.A Artifacts capture snapshot metadata and immutability proof for Step 0 (source understanding). S0.A Artifacts MUST include:
- `snapshot_identity` (string): canonical identifier (hash, URI, or DOI)
- `snapshot_type` (string): `"hash" | "git_commit" | "doi"`
- `hash_algorithm` (string, conditional): algorithm name if `snapshot_type = "hash"` (e.g., "sha256")
- `content_hash` (string, conditional): computed hash of canonical content
- `git_repo` (string, conditional): repository URL if `snapshot_type = "git_commit"`
- `git_ref` (string, conditional): commit SHA or branch/tag if `snapshot_type = "git_commit"`
- `doi` (string, conditional): DOI value if `snapshot_type = "doi"`
- `archived_at` (string, conditional): timestamp of immutable archive if `snapshot_type = "doi"`

S0.A Artifacts establish the baseline for reproducibility and enable auditors to verify they are analyzing identical specifications.

<a id="STF-WB-CL-000060e"></a>
#### 6.5.2 Artifact class S1.A: Normalized requirements (normative)

<a id="STF-WB-CL-000060f"></a>
S1.A Artifacts are produced in Step 1 (requirements normalization) and represent the specification requirements in a structured form. S1.A Artifacts MUST include:
- `requirements` (array): array of normalized requirement objects
- Each requirement object MUST include:
  - `req_id` (string): stable identifier for the requirement (from source)
  - `text` (string): normalized requirement statement
  - `source_location` (string): reference to source fragment or section
  - `category` (string, optional): e.g., "functional", "performance", "security"

S1.A Artifacts serve as the basis for formal specification and verification in subsequent steps.

<a id="STF-WB-CL-000060g"></a>
#### 6.5.3 Artifact class S2.A: Formal specification (normative)

<a id="STF-WB-CL-000060h"></a>
S2.A Artifacts are produced in Step 2 (formalization) and represent requirements as formal models. S2.A Artifacts MUST include:
- `formal_method` (string): identifier of the formal method used (e.g., "tlaplus", "alloy", "coq", "isabelle")
- `formal_language_version` (string): version of the formal language tool (e.g., TLC version for TLA+)
- `specification_content` (string): the formal specification source code or reference to external file
- `entry_point` (string, optional): identifier of the main module or spec (e.g., "HelloWorldProtocol")

S2.A Artifacts enable automated verification and reproducible counterexample discovery in Step 3.

<a id="STF-WB-CL-000060i"></a>
#### 6.5.4 Artifact class S3.A: Verification results (normative)

<a id="STF-WB-CL-000060j"></a>
S3.A Artifacts are produced in Step 3 (verification) and record outcomes of automated verification on S2.A formal specifications. S3.A Artifacts MUST include:
- `verification_method` (string): identifier of the verifier used (e.g., "tlc", "alloy", "coq", "isabelle")
- `verification_version` (string): version of the verification tool
- `status` (string): `"passed" | "failed" | "error"`
- `result_summary` (string): brief description of verification outcome
- If status is `"failed"`:
  - `counterexample` (object): representation of the failing behavior (traces, variable values, etc.)
- If status is `"error"`:
  - `error_message` (string): description of verification tool error
  - `error_location` (string, optional): reference to problematic specification region

S3.A Artifacts provide evidence of automated analysis and enable reproducibility of verification.

<a id="STF-WB-CL-000060k"></a>
#### 6.5.5 Artifact class S4.A: Interface contracts (normative)

<a id="STF-WB-CL-000060l"></a>
S4.A Artifacts are produced in Step 4 (interface specification) and define contracts and API specifications. S4.A Artifacts MUST include:
- `interface_type` (string): kind of interface (e.g., "rest-api", "rpc", "messaging", "protocol")
- `contracts` (array): array of contract definitions
- Each contract MUST include:
  - `contract_id` (string): stable identifier
  - `description` (string): human-readable description of the contract
  - `inputs` (object, optional): expected input structure or schema
  - `outputs` (object, optional): expected output structure or schema
  - `preconditions` (array, optional): required conditions before invocation
  - `postconditions` (array, optional): guaranteed conditions after invocation
  - `side_effects` (array, optional): observable side effects

S4.A Artifacts enable conformance testing in Step 5 and provide implementation guidance.

<a id="STF-WB-CL-000060m"></a>
#### 6.5.6 Artifact class S5.A: Conformance tests (normative)

<a id="STF-WB-CL-000060n"></a>
S5.A Artifacts are produced in Step 5 (conformance testing) and contain executable tests and evidence of test execution. S5.A Artifacts MUST include:
- `test_suite_id` (string): stable identifier for the test suite
- `test_framework` (string): name/version of testing framework used
- `tests` (array): array of test case records
- Each test case MUST include:
  - `test_id` (string): unique identifier within the suite
  - `test_description` (string): human-readable description
  - `inputs` (object): test inputs
  - `expected_outputs` (object): expected outputs
  - `actual_outputs` (object, conditional): actual outputs if test has been executed
  - `status` (string, conditional): `"passed" | "failed" | "skipped"` if executed
  - `trace_to_contract` (string): reference to S4.A contract ID being tested
- `execution_summary` (object): aggregate test results (total, passed, failed, skipped)

S5.A Artifacts provide evidence of conformance and implementation correctness.

---

<a id="STF-WB-CL-000061"></a>
### 6.6 GateResult object (normative)

<a id="STF-WB-CL-000062"></a>
Each STF-M step gate evaluation published by the workbench MUST be represented as `kind = "stfwb.gate_result"`.  
<a id="STF-WB-CL-000063"></a>
A GateResult MUST include:
- `gate_id` (string): `S0|S1|S2|S3|S4|S5`
- `status` (string): `accepted | rejected | needs_review`
- `derived_from_actions` (array): `{ "action_id": "A0.1", "status": "accepted|rejected|needs_review" }`
- `evidence` (array): references to Artifact IDs supporting the gate result

<a id="STF-WB-CL-000064"></a>
GateResult status MUST be derived from action outcomes using the following explicit algorithm:

- `status = "accepted"` iff ALL actions in `derived_from_actions` have `status = "accepted"`
- `status = "rejected"` iff ANY action in `derived_from_actions` has `status = "rejected"`
- `status = "needs_review"` for all other cases (some actions pending or mixed outcomes)

When status is `"rejected"`, the GateResult MUST include a `rejection_reason` field identifying the first failing action and an optional `remediation_guidance` field suggesting corrective actions.

---

<a id="STF-WB-CL-000065"></a>
## 7. Evidence publication to a shared GitHub repository (normative)

<a id="STF-WB-CL-000066"></a>
Under **profile:storage-github-shared-repo**, all published evidence MUST reside under a single shared repository and MUST be partitioned by immutable `project_slug` namespaces.  
<a id="STF-WB-CL-000067"></a>
The canonical base path for a Project MUST be:
- `env/dev/projects/<project_slug>/` for development/test evidence, or
- `env/prod/projects/<project_slug>/` for published/stable evidence.

The `env/dev` and `env/prod` are conventional namespace separators for development and production evidence respectively. Implementers MAY use different environment prefixes (e.g., `staging`, `test`, `qa`) but MUST document their semantics in project metadata. All environment prefixes are optional; implementations MAY omit the `env/` prefix entirely if documented in storage configuration.

<a id="STF-WB-CL-000068"></a>
Within a Project base path, the workbench MUST create:
- `project.json` (Project object)
- `runs/<iteration_id>/iteration.json` (Iteration object)
- `runs/<iteration_id>/scope.json` (ScopeSpec object)
- `runs/<iteration_id>/steps/<Sx>/gate.json` (GateResult per step)
- `runs/<iteration_id>/steps/<Sx>/artifacts/<artifact_id>.json` (Artifacts)

<a id="STF-WB-CL-000069"></a>
Artifacts MAY be committed in batches by action rather than one artifact per commit. When batching is used, the commit message MUST list all artifact IDs: `[project_slug/iteration_id/action_id] artifact_id_1, artifact_id_2, ...`. Artifacts produced by different actions MUST be committed in separate commits to preserve action-level traceability. The workbench MUST NOT batch artifacts from different actions into a single commit.

<a id="STF-WB-CL-000070"></a>
The workbench MUST ensure that published Artifacts are machine-readable and include deterministic validation references to enable third-party auditing.

<a id="STF-WB-CL-000071"></a>
Project slugs MUST be immutable in v0.2.0 and MUST remain stable across the lifetime of published evidence for that Project namespace.

---

<a id="STF-WB-CL-000072"></a>
## 8. Minimum workflow integration (normative)

<a id="STF-WB-CL-000073"></a>
An Iteration MUST record `source_snapshot` identity and immutability reference, and MUST record a structured ScopeSpec, before Step 0 Artifacts are considered valid for publication.  
<a id="STF-WB-CL-000074"></a>
A workbench MAY publish partial results (e.g., only Step 0 and Step 1) as long as published Artifacts remain internally consistent, traceable, and deterministically validatable.  
<a id="STF-WB-CL-000075"></a>
The workbench MUST support iterative revision: steps MAY be revisited and actions retried, provided each retry is recorded and published evidence remains auditable.

<a id="STF-WB-CL-000075a"></a>
### 8.1 Retry semantics and error handling (normative)

<a id="STF-WB-CL-000075b"></a>
Retries are allowed only for Iterations in the `in_progress` state. Each retry of an action MUST result in a new Artifact version or separate Artifact record.

<a id="STF-WB-CL-000075c"></a>
When an action is retried:
- A new Artifact MUST be created with a distinct `artifact_id`
- The new Artifact MUST include a `retry_of` field referencing the previous attempt's `artifact_id`
- The previous Artifact MUST remain published (not deleted or overwritten) to preserve audit trail
- A new attempt number or version suffix SHOULD be appended to the artifact ID (e.g., `artifact-id-attempt-2`)

<a id="STF-WB-CL-000075d"></a>
When a gate is rejected, the GateResult MUST include:
- `rejection_reason` (string): explanation of why the gate was rejected
- `suggested_remediation` (string, optional): recommended corrective actions
- `retry_allowed` (boolean): indication of whether the Iteration can be retried

<a id="STF-WB-CL-000075e"></a>
Frozen Iterations MUST NOT be retried without explicit unfreezing. Unfreezing a frozen Iteration requires formal justification recorded in a `unfreeze_justification` audit log entry that documents why the frozen evidence is being reopened (e.g., "Critical bug discovered in verification tool"). Archived Iterations MUST NEVER be unfrozen or retried; doing so would violate audit integrity.

---

<a id="STF-WB-CL-000076"></a>
## 9. Deterministic validation (normative)

<a id="STF-WB-CL-000077"></a>
For each required object and Artifact, the workbench MUST publish (a) a validation method description and (b) the latest validation result, such that re-running validation on the same inputs yields the same result.  
<a id="STF-WB-CL-000078"></a>
Validation methods SHOULD be machine-executable and versioned, and the validation environment SHOULD be recorded when practical.

<a id="STF-WB-CL-000078a"></a>
### 9.1 Outcome equivalence definition (normative)

<a id="STF-WB-CL-000078b"></a>
"Deterministic validation" means that re-running a validation method on identical inputs in the same environment yields equivalent outcomes. Outcome equivalence is defined as follows:

- **Method identity:** Same `method_id`, `method_version`, and tool version
- **Input identity:** Identical `inputs` (bytes-identical for files, structurally identical for objects)
- **Environment identity:** Same validation environment (OS, tool dependencies, configuration)
- **Outcome equivalence:** Same pass/fail/error status AND substantively identical diagnostics and results

Substantive identity means:
- For pass/fail outcomes: identical boolean status
- For proofs/counterexamples: semantically equivalent traces (same state transitions, not necessarily byte-identical logging)
- For numeric results: identical values (or within declared tolerance if tool-specific precision is documented)

<a id="STF-WB-CL-000078c"></a>
Implementations MUST document acceptable sources of non-determinism in the `reproducibility_notes` field:
- Timestamp fields (validation_time, tool_invocation_time) are not considered part of outcome
- UUID generation in tool output is not considered part of outcome if documented
- Log message formatting differences are acceptable if status and diagnostics are identical
- Floating-point rounding differences are acceptable if declared tolerance is met

Implementations MUST NOT accept non-determinism from:
- Different specification versions or Artifact versions
- Different formal methods or theorem provers
- Different platform architectures (unless explicitly documented as irrelevant)
- Randomized tool behavior (e.g., randomized search in SAT solvers) without deterministic seeding

---

<a id="STF-WB-CL-000079"></a>
## 10. Security Considerations (normative)

<a id="STF-WB-CL-000080"></a>
This section addresses security properties and risks relevant to workbench implementations and evidence repositories.

<a id="STF-WB-CL-000080a"></a>
### 10.1 Evidence integrity and tampering

<a id="STF-WB-CL-000080b"></a>
Published evidence Artifacts are intended to be permanent, auditable records. Implementations MUST implement access controls to prevent unauthorized modification of published Artifacts:

- Repository write access MUST be restricted to authorized workbench operators
- Once an Artifact is published and a gate is `frozen`, no modifications to that Artifact SHOULD be permitted
- If modifications are necessary (e.g., bug fixes to formal specifications), the modified Artifact MUST be published with a new `artifact_id` and a clear `superseded_by` reference, preserving the original as evidence of the prior state

<a id="STF-WB-CL-000080c"></a>
Repositories SHOULD use signed commits (e.g., GPG-signed Git commits) to establish chain-of-custody for published evidence. Commit signatures enable third-party auditors to verify that published evidence has not been retroactively altered.

<a id="STF-WB-CL-000080d"></a>
### 10.2 Supply-chain trust

<a id="STF-WB-CL-000080e"></a>
Validation tools (formal method provers, theorem provers, test harnesses) are part of the trusted computing base for evidence generation. Implementations SHOULD:

- Document the provenance and version of all validation tools (source repositories, release tags, checksums)
- Verify tool binary integrity (e.g., through package manager signatures or build reproducibility)
- Use sealed, immutable tool environments (containers, virtual machines) to prevent configuration drift
- Record tool invocation parameters and environment variables in Artifacts to enable reproducibility

Implementers SHOULD consider using cryptographically sealed containers (signed Docker images, reproducible builds) to establish trust in validation tool versions.

<a id="STF-WB-CL-000080f"></a>
### 10.3 Source specification authenticity

<a id="STF-WB-CL-000080g"></a>
The `source_snapshot` immutability mechanism (hash, git commit, DOI) is critical for preventing specification tampering. Implementations MUST ensure that source snapshots reference authentic specifications:

- For hash-based mechanisms: implementers MUST obtain specification content through secure channels (e.g., https, signed downloads) and independently verify hashes
- For git-based mechanisms: implementers MUST verify that the git repository is under organizational control or is a trusted upstream source
- For DOI-based mechanisms: implementers MUST verify DOI resolution through official archives (Zenodo, etc.) and check timestamps to detect retroactive modifications

<a id="STF-WB-CL-000080h"></a>
## 11. Privacy Considerations (normative)

<a id="STF-WB-CL-000080i"></a>
This section addresses privacy risks and requirements for workbench implementations.

<a id="STF-WB-CL-000080j"></a>
### 11.1 Personally identifiable information in evidence

<a id="STF-WB-CL-000080k"></a>
Artifacts MAY contain sensitive data: source code from specifications, test cases, formal models, or trace logs that reveal system behavior. Before publishing evidence to shared repositories, operators MUST:

- Scan Artifacts for embedded PII (passwords, API keys, email addresses, internal identifiers)
- Remove or redact proprietary or confidential information that is not essential for evidence
- Apply consistent redaction to specification excerpts and trace logs (e.g., replace usernames with `<REDACTED>`)

Organizations publishing to multi-tenant or public repositories SHOULD use separate private repositories for evidence containing confidential specifications or test results.

<a id="STF-WB-CL-000080l"></a>
### 11.2 Scope declarations and system disclosure

<a id="STF-WB-CL-000080m"></a>
ScopeSpec declarations publicly state which parts of a specification are under test. This information can reveal:

- System architecture and design decisions (if Scope focuses on specific modules)
- Undisclosed features (if Scope includes unstable or pre-release clauses)
- Security-sensitive regions (if Scope includes cryptographic or authentication modules)

Operators of high-assurance systems SHOULD:

- Use private evidence repositories for pre-release specifications
- Apply access control to Iteration and ScopeSpec metadata in shared repositories
- Publish evidence only after public specification release
- Redact Scope section descriptions if they reveal security-sensitive details

<a id="STF-WB-CL-000080n"></a>
### 11.3 Third-party validation and auditor privacy

<a id="STF-WB-CL-000080o"></a>
Third-party auditors who re-run validation on published Artifacts generate their own validation logs and intermediate results. These logs MAY contain sensitive information (tool execution traces, performance metrics, intermediate states). Auditors SHOULD:

- Store validation logs in restricted-access locations
- Apply data retention policies to validation artifacts (delete after audit completion)
- Use sandboxed environments to prevent accidental information leakage during validation

---

<a id="STF-WB-CL-000081"></a>
## 12. References (normative and informative)

<a id="STF-WB-CL-000082"></a>
### 12.1 Normative References

<a id="STF-WB-CL-000082a"></a>
[RFC2119] Bradner, S., "Key words for use in RFCs to Indicate Requirement Levels," BCP 14, RFC 2119, DOI 10.17487/RFC2119, March 1997, https://www.rfc-editor.org/rfc/rfc2119.html.

<a id="STF-WB-CL-000082b"></a>
[ISO8601] International Organization for Standardization, "Date and Time—Representations for Information Interchange—Part 1: Basic Rules," ISO 8601-1:2019, 2019. Specifies timestamp and date-time formats used throughout this specification.

<a id="STF-WB-CL-000082c"></a>
[STF-M] Sovereign Trust Framework Methodology. Specifies the abstract STF-M workflow (Steps 0–5, Actions, Gates) that this specification operationalizes. [Full reference to be completed with version and publication details.]

<a id="STF-WB-CL-000082d"></a>
[STF-Spec] Sovereign Trust Framework Framework Specification. Specifies framework requirements and conformance criteria referenced in this specification's scope. [Full reference to be completed with version and publication details.]

<a id="STF-WB-CL-000083"></a>
### 12.2 Informative References

<a id="STF-WB-CL-000083a"></a>
[SemVer] Preston-Werner, T., "Semantic Versioning 2.0.0," https://semver.org/, 2023. Semantic versioning practices recommended for artifact and schema versioning throughout this specification.

<a id="STF-WB-CL-000083b"></a>
[JSON] Bray, T., "The JavaScript Object Notation (JSON) Data Interchange Format," RFC 8259, DOI 10.17487/RFC8259, December 2017, https://www.rfc-editor.org/rfc/rfc8259.html. Serialization format for workbench data models under profile:serialization-json.

<a id="STF-WB-CL-000083c"></a>
[Git] Chacon, S. and Straub, B., "Pro Git," 2nd ed., Apress, 2014. Git version control system and commit semantics referenced in Section 7 (Evidence Publication) and Section 10.1 (signed commits).

<a id="STF-WB-CL-000083d"></a>
[TLA+] Lamport, L., "Specifying Systems: The TLA+ Language and Tools for Hardware and Software Engineers," Addison-Wesley, 2002. Example formal method referenced in artifact class schema definitions (S2.A, S3.A).

<a id="STF-WB-CL-000083e"></a>
[Alloy] Jackson, D., "Software Abstractions: Logic, Language, and Analysis," MIT Press, 2nd ed., 2012. Example formal method for system specification and verification.

<a id="STF-WB-CL-000083f"></a>
[DoD-SSP] U.S. Department of Defense, "Software Security Program," MIL-STD-8888D, 2022. Reference for security assurance practices and supply-chain trust in Section 10.

---

<a id="STF-WB-CL-000084"></a>
## Appendix A: Example objects (informative)

### A.1 Example `project.json`

```json
{
  "kind": "stfwb.project",
  "version": "0.2.0",
  "id": "project:didcomm-v2-test",
  "project_id": "c7f1b3d6-7a14-4fd8-9a8d-3a3c2f91a2e1",
  "project_slug": "didcomm-v2-test",
  "target": {
    "source_identity": "https://github.com/example/didcomm-spec",
    "description": "Dev project for STF workbench testing"
  },
  "storage": {
    "provider": "github",
    "repo": "your-org/stf-evidence",
    "branch": "main",
    "base_path": "env/dev/projects/didcomm-v2-test"
  },
  "source_snapshot": {
    "snapshot_identity": "sha256:abc123def456",
    "snapshot_type": "hash",
    "hash_algorithm": "sha256",
    "content_hash": "abc123def456"
  },
  "created_at": "2026-01-04T01:00:00Z"
}
```

---

<a id="STF-WB-CL-000085"></a>
## Appendix B: CLI sketch (informative)

Updated for v0.2.0 with standardized placeholder syntax (SLUG instead of <slug>):

- stfwb project create --slug SLUG --target URI --repo OWNER/REPO --branch BRANCH --env ENV
- stfwb iteration create --project SLUG --snapshot SNAPSHOT-URI --hash SHA256 --scope SCOPE-FILE
- stfwb step run --project SLUG --iteration ID --step STEP
- stfwb artifact publish --project SLUG --iteration ID --artifact PATH
- stfwb gate evaluate --project SLUG --iteration ID --step STEP

---

---
