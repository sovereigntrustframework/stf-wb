# Phase 2A Implementation: GitHub App OAuth + User Model

## Overview

Phase 2A implements proper user authentication using GitHub App OAuth, establishing the foundation for the provider-model architecture. This replaces the MVP's standard OAuth with GitHub App OAuth, enabling:

1. **JIT User Provisioning**: Users are automatically created on first login
2. **Installation Access Tokens**: Short-lived (1 hour) tokens scoped to GitHub App installations
3. **Proper Git Semantics**: Commits and PRs appear under the authenticated user's account
4. **Multi-Provider Foundation**: Architecture ready for GitLab, email, and SSI providers

## Architecture

### Backend Components

#### 1. `stfwb_web/models_auth.py`
Defines the authentication data model:

- **ProviderId**: Enum for provider types (GitHub, GitLab, email, SSI)
- **ExternalIdentity**: Provider-specific identity (provider + subject + profile info)
- **User**: Internal user record (UUID-based, provider-agnostic)
- **LinkedIdentity**: Link between User and ExternalIdentity (tracks last login, profile info)
- **AuthSession**: Server-side session with user + linked identities
- **GitHub-specific models**:
  - GitHubInstallation: User's GitHub App installation
  - GitHubRepository: Accessible GitHub repository
  - GitHubAppToken: Short-lived installation token

#### 2. `stfwb_web/auth/github_app.py`
GitHub App OAuth implementation:

- **GitHubAppOAuthConfig**: Manages GitHub App authentication
  - `get_authorization_url()`: Returns OAuth authorization URL
  - `exchange_code_for_token()`: Exchanges auth code for user access token
  - `fetch_user()`: Gets user info from GitHub API
  - `fetch_installations()`: Lists user's GitHub App installations
  - `mint_installation_token()`: Creates short-lived installation token using JWT
  - `authenticate()`: Full JIT provisioning (returns user + identity + installations)

#### 3. `stfwb_web/providers/` 
Provider abstraction layer:

- **repo.py**: RepoProvider interface for Git operations
  - Abstract methods: list_repos, get_access_token, clone, create_branch, commit, create_pr, merge_pr
  - GitHubRepoProvider: GitHub implementation (stub for future completion)

- **storage.py**: Storage abstraction for user/identity/session persistence
  - UserStore: User CRUD operations
  - IdentityStore: Linked identity management
  - SessionStore: Session storage and retrieval
  - InMemory implementations for MVP

#### 4. Updated `stfwb_web/app.py`
FastAPI endpoints refactored for GitHub App OAuth:

- `/auth/github/start`: Initiates OAuth flow (CSRF state token)
- `/auth/github/callback`: Completes OAuth (JIT user provisioning)
- `/auth/user?user_id=...`: Gets authenticated user info
- `/auth/logout?user_id=...`: Invalidates session

### Frontend Components

#### 1. Updated `AuthContext.tsx`
Manages authentication state:

- Stores: user_id (UUID), AuthUser (with LinkedIdentities), token
- Handles OAuth callback: URL params → fetch user info → localStorage persistence
- Implements login/logout using user_id instead of tokens

#### 2. Updated Components
- **TopBar**: Uses user.identities[0] for avatar/display
- **HomePage**: Shows GitHub login option only if not authenticated

## OAuth Flow

### GitHub App Installation Discovery

```
User clicks "Sign In with GitHub"
    ↓
Frontend redirects to /auth/github/start
    ↓
Backend generates CSRF state, redirects to GitHub OAuth
    ↓
User authorizes app on GitHub (sees list of installations)
    ↓
GitHub redirects to /auth/github/callback with code + state
    ↓
Backend verifies CSRF, exchanges code for user access token
    ↓
Backend fetches user info + list of installations
    ↓
Backend creates User + LinkedIdentity (JIT), stores session
    ↓
Backend redirects to frontend with user_id
    ↓
Frontend stores user_id in localStorage, loads app
```

### Installation Token Minting (Future)

When user selects a repository for a project:

```
Frontend requests /repos/installations
    ↓
Backend returns user's accessible installations
    ↓
Frontend shows installation/repo selector
    ↓
User selects repo
    ↓
Frontend requests access token for repo
    ↓
Backend mints JWT from app private key
    ↓
Backend exchanges JWT for installation access token
    ↓
Backend returns token to frontend (1 hour expiry)
    ↓
Frontend uses token for Git operations
```

## Environment Setup

### GitHub App Creation

1. Go to https://github.com/settings/apps/new
2. Create app with:
   - Name: STF-Workbench-Dev
   - Homepage URL: http://localhost:5173
   - Callback URL: http://localhost:8000/auth/github/callback
   - Permissions:
     - Contents: Read & Write
     - Pull Requests: Read & Write
     - Workflows: Read & Write
3. Copy App ID and Client ID
4. Generate private key and client secret
5. Create `.env` file in project root (see `.env.example`)

### Local Development

```bash
# Install dependencies
pip install -e ".[web]"

# Set environment variables
export GITHUB_APP_ID=your_app_id
export GITHUB_APP_PRIVATE_KEY="$(cat /path/to/private-key.pem)"
export GITHUB_CLIENT_ID=your_client_id
export GITHUB_CLIENT_SECRET=your_client_secret

# Run backend
cd stfwb_web
uvicorn app:app --reload --port 8000

# In another terminal, run frontend
cd stfwb_web_ui
npm run dev
```

## Data Flows

### User Creation (JIT)

```python
# On first GitHub OAuth:
1. Frontend redirects to /auth/github/start
2. User authorizes app
3. Backend:
   - Exchanges code for user token
   - Fetches user info (GitHub ID as subject)
   - Creates internal User (UUID)
   - Creates LinkedIdentity (user_id + GitHub provider/subject)
   - Stores AuthSession
   - Returns user_id to frontend
```

### Multi-Provider Support (Future)

Same user can have multiple linked identities:

```python
user_id = UUID("...")
identities = [
    LinkedIdentity(
        user_id=user_id,
        provider=ProviderId.GITHUB,
        subject="12345",  # GitHub user ID
        display="alice",
        ...
    ),
    LinkedIdentity(
        user_id=user_id,
        provider=ProviderId.GITLAB,
        subject="alice@example.com",
        display="alice",
        ...
    ),
]
```

## Testing

### Backend Auth Endpoints

```bash
# Test /auth/github/start (should redirect to GitHub)
curl http://localhost:8000/auth/github/start -v

# Test /auth/user (should return 401 without valid user_id)
curl "http://localhost:8000/auth/user?user_id=invalid" 
# Should return 401

# Test /auth/logout
curl -X POST "http://localhost:8000/auth/logout?user_id=valid_id"
```

### Frontend OAuth Flow

1. Go to http://localhost:5173
2. Click "Sign In with GitHub"
3. Authorize the app
4. Should redirect back with user_id in URL
5. Check localStorage for user_id and auth_user
6. Avatar should appear in TopBar

## Next Steps (Phase 2B)

1. **Installation/Repo Selection UI**: Add modal for selecting which installation/repo to work with
2. **Installation Token Endpoints**: `/repos/installations` and `/repos/list`
3. **GitHubRepoProvider Implementation**: Complete clone, commit, create_pr, merge_pr
4. **Database Persistence**: Replace in-memory stores with SQLAlchemy
5. **Token Refresh**: Handle expired installation tokens
6. **Error Handling**: Proper error messages for auth failures

## Key Decisions

1. **JIT Over Pre-Registration**: Users are created on first login (simpler UX)
2. **Installation Tokens Over User Token**: Short-lived installation tokens (better security)
3. **Internal UUID Over GitHub ID**: Provider-agnostic user model (multi-provider ready)
4. **localStorage For Session**: Good for MVP (cookies in production)
5. **No API Key Auth**: OAuth only for Phase 1 (API keys may be added later)

## Known Limitations

- In-memory storage (MVP only)
- No token refresh (1-hour limit, user re-authenticates)
- No rate limiting on auth endpoints
- Private key in environment variable (should use secret management in production)
- Limited error messages in OAuth callback
