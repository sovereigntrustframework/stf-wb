
# Providers (Identity, Repo, Storage)

## Goal
STFWorkbench (stfwb) must ship an MVP that proves the full loop (login → select repo/project → create run → execute steps → publish → stream SSE), while keeping the backend as the **single-writer** and the UI as a REST+SSE client. [file:21][file:22]  
At the same time, the architecture must keep the door open for additional identity providers (email/SSI), other repo providers (GitLab/local), and even non-git storage backends. [file:22]

## MVP decisions (with long-term intent)

### Identity Provider (IdP)
**MVP decision:** GitHub is the only IdP in the MVP, using just-in-time provisioning to create an internal `User` at first login. [file:21][file:22]  
**Recommendation:** implement GitHub login via a **GitHub App** (web flow), because GitHub Apps are generally preferred over OAuth apps (fine‑grained permissions, tighter repository selection control, short‑lived tokens). [web:73]  
**Minimum security:** use OAuth `state` to mitigate CSRF in redirect-based flows. [web:136]

### Repo Provider
**MVP decision:** GitHub is the only repo provider in the MVP and all Git operations (clone/branch/commit/merge/sync) run on the backend; the UI never performs Git operations directly. [file:22][file:21]  
**Recommendation:** use **GitHub App installation access tokens** for repo operations, minted on demand for the selected installation; GitHub states these tokens expire after 1 hour. [web:23]  
**Why now:** it matches the existing direction (“GitHub App for repository access”) and avoids PATs. [file:22]

### Storage Provider
**MVP decision:** git is the only durable store for versioned artifacts (to avoid DB migration burden now), and the workspace lives on the server filesystem (local-server now; Oracle VM disk later). [file:21][file:22]  
**Recommendation:** split “artifact storage” from “application state storage” from day one (even if both are filesystem/memory in the MVP). [file:21][file:22]  
This is the key design move that keeps “non-git databases” viable later without breaking the domain model. [file:22]

---

## Internal provider interfaces

### IdentityProvider
Responsibilities:
- Authenticate a user and return a stable `ExternalIdentity`.
- Optionally expose a server-side “provider token handle” for provider API calls (never sent to the browser).
- Never store provider tokens in the frontend; the browser only has a session cookie. [file:21][file:22]

Data types (example):
```ts
type ProviderId =
  | "github"
  | "gitlab"
  | "email"
  | "ssi";

type ExternalIdentity = {
  provider: ProviderId;
  subject: string;        // stable provider identifier (do NOT use username as primary key)
  display?: string;       // login/email/did (UI-friendly)
  email?: string | null;
  avatar_url?: string | null;
};

type User = {
  user_id: string;        // internal UUID
  created_at: string;
};

type LinkedIdentity = {
  user_id: string;
  provider: ProviderId;
  subject: string;
  created_at: string;
  last_login_at: string | null;
};

type AuthSession = {
  user_id: string;
  identities: ExternalIdentity[];
};
```

**MVP note:** even with only GitHub, persist `User` and `LinkedIdentity` so future providers can be added without refactoring projects/runs/publications. [file:22]

Future IdP examples:
- `EmailMagicLinkIdentityProvider` (`provider="email"`, `subject=email_normalized`)
- `OIDCIdentityProvider` (Google/Microsoft; `subject=iss + ":" + sub`)
- `SSIIdentityProvider` (`provider="ssi"`, `subject=did:<method>:...`)

### RepoProvider
Responsibilities:
- Enumerate repo targets the system can operate on (installations, orgs, repos, etc).
- Create a persistent “project binding” to a repo, including any provider-specific references.
- Provide abstract repo operations (clone/fetch, create branch, commit, open PR/MR, merge, etc). [file:22]

Data types (example):
```ts
type RepoRef =
  | { kind: "github"; owner: string; repo: string; installation_id: number }
  | { kind: "gitlab"; project_id: number }
  | { kind: "local_git"; path: string };

type Project = {
  project_id: string;
  name: string;
  repo: RepoRef;
};
```

Future repo provider examples:
- `GitLabRepoProvider` (projects, merge requests, impersonation tokens)
- `BitbucketRepoProvider`
- `LocalGitRepoProvider` (offline-first; local bare repo + later sync)
- `NoGitRepoProvider` (if storage becomes purely DB/object store and git is optional)

### StorageProvider (two layers)
We strongly recommend two storage interfaces:

1) **ArtifactStore** (durable, domain artifacts)
- Versioned: runs, publications, ledgers, and “audit-worthy” outputs.
- MVP implementation: git repo. [file:21]

2) **AppStateStore** (operational state)
- Sessions, settings, caches/indexes, job state, logs.
- MVP implementation: memory + local filesystem; hosted: Redis/DB. [file:21][file:22]

Data types (example):
```ts
type ArtifactStoreRef =
  | { kind: "git"; repo: RepoRef; base_branch: "main" }
  | { kind: "sql"; dsn: string }
  | { kind: "object_store"; bucket: string; prefix: string };

type AppStateStoreRef =
  | { kind: "memory" }
  | { kind: "filesystem"; root: string }
  | { kind: "redis"; url: string }
  | { kind: "sql"; dsn: string };
```

Future storage examples:
- `SQLArtifactStore`: store runs/publications in PostgreSQL; optionally export snapshots to git on publish.
- `ObjectStoreArtifactStore`: store large outputs in OCI Object Storage (content-addressed), keep hashes/metadata in git or SQL.
- `Hybrid`: artifacts in git, indexes in SQL (fast queries for UI timelines).

---

## Security and deployment notes (MVP-ready, Oracle-ready)

### Cookies & sessions
Use a server-side session model and set cookie attributes defensively (`HttpOnly`, `Secure` in HTTPS, and appropriate `SameSite`). [web:130]  
This is especially important when you later move from same-host (backend serving SPA) to split-host (CDN + API subdomain). [file:21][file:22]

### GitHub tokens
GitHub App installation tokens should be minted on demand and rotated frequently; GitHub notes installation access tokens expire after 1 hour. [web:23]  
GitHub Apps are generally preferred to OAuth apps due to fine-grained permissions and tighter repo access control, reducing blast radius if credentials leak. [web:73]

---

## Open questions (tracked, not blocking the MVP)
These items influence provider boundaries and should remain explicit in the design docs:

- **Credential flow end-to-end:** how the backend receives, stores (or avoids storing), and refreshes GitHub access securely across local and Oracle deployments. [file:22]  
- **Settings storage:** server-side profile area vs in-repo settings vs separate DB/object storage (cache/index). [file:22]  
- **Offline story:** pure local-server with later sync vs always-online with caching/resilience. [file:22]  
- **Tenancy/isolation:** whether a server instance serves multiple users/orgs and what isolation is required. [file:22]  
- **Publication ledger and PR strategy:** ledger file vs derive from Git history; one PR per run vs per publication (impacts RepoProvider semantics and UI state model). [file:22]

---

## Recommended next steps (to unblock MVP)
1) Commit `openapi.yaml` early (OpenAPI-first) covering: auth start/callback/logout, `GET /me`, repo selection endpoints, runs endpoints, and SSE (`text/event-stream`). [file:21]  
2) Implement `GitHubIdentityProvider` + server-side session (memory store) + JIT provisioning (`User` + `LinkedIdentity`). [file:21][file:22]  
3) Implement `GitHubRepoProvider` for listing installations/repos and minting installation tokens, then layer Git operations on top. [file:21][web:23]

Citações:
[1] stf-wb-mvp-plan.md https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/41684381/f8e10063-ea0d-4321-adac-eb0e69d2c478/stf-wb-mvp-plan.md
[2] stf-wb-decisions.md https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/41684381/bb1f0fcf-ba65-4d4d-9d54-c3da18b3e19c/stf-wb-decisions.md
[3] Differences between GitHub Apps and OAuth apps - GitHub Docs https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/differences-between-github-apps-and-oauth-apps
[4] Deciding when to build a GitHub App https://docs.github.com/en/apps/creating-github-apps/about-creating-github-apps/deciding-when-to-build-a-github-app
[5] Differences between GitHub Apps and OAuth apps https://docs.github.com/en/enterprise-cloud@latest/apps/oauth-apps/building-oauth-apps/differences-between-github-apps-and-oauth-apps
[6] Diferenças entre os aplicativos GitHub e os aplicativos OAuth - GitHub Enterprise Server 3.16 Docs https://docs.github.com/pt/enterprise-server@3.16/apps/oauth-apps/building-oauth-apps/differences-between-github-apps-and-oauth-apps
[7] Differences between GitHub Apps and OAuth apps - GitHub Enterprise Server 3.5 Docs https://docs.github.com/en/enterprise-server@3.5/apps/oauth-apps/building-oauth-apps/differences-between-github-apps-and-oauth-apps
[8] Generating an installation access token for a GitHub App https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-an-installation-access-token-for-a-github-app
[9] Authentication and Session Management | OWASP/CheatSheetSeries | DeepWiki https://deepwiki.com/OWASP/CheatSheetSeries/3-authentication-and-session-management
[10] Differences between GitHub Apps and OAuth apps - GitHub Enterprise Server 3.8 Docs https://docs.github.com/en/enterprise-server@3.8/apps/oauth-apps/building-oauth-apps/differences-between-github-apps-and-oauth-apps
[11] Generating an installation access token for a GitHub App - GitHub Enterprise Server 3.9 Docs https://docs.github.com/en/enterprise-server@3.9/apps/creating-github-apps/authenticating-with-a-github-app/generating-an-installation-access-token-for-a-github-app
[12] Session Management - OWASP Cheat Sheet Series https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
[13] Differences between GitHub Apps and OAuth apps - GitHub Enterprise Server 3.6 Docs https://docs.github.com/en/enterprise-server@3.6/apps/oauth-apps/building-oauth-apps/differences-between-github-apps-and-oauth-apps
[14] Generating an installation access token for a GitHub App - GitHub Enterprise Server 3.12 Docs https://docs.github.com/en/enterprise-server@3.12/apps/creating-github-apps/authenticating-with-a-github-app/generating-an-installation-access-token-for-a-github-app
[15] CheatSheetSeries/cheatsheets/Session_Management_Cheat_Sheet.md at master · OWASP/CheatSheetSeries https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Session_Management_Cheat_Sheet.md
[16] Differences between GitHub Apps and OAuth apps - GitHub Enterprise Server 3.4 Docs https://docs.github.com/en/enterprise-server@3.4/apps/oauth-apps/building-oauth-apps/differences-between-github-apps-and-oauth-apps
[17] Using The Octokit. Js Sdk To... https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-as-a-github-app-installation
