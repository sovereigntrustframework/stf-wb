# Phase 2A Complete ✓ - Next Steps Guide

## What's Been Done

**Phase 2A Implementation** is now complete with:

### Backend Architecture
- ✅ User model (internal UUID-based)
- ✅ LinkedIdentity model (provider-specific bindings)
- ✅ AuthSession for server-side sessions
- ✅ GitHub App OAuth integration
  - OAuth authorization flow
  - Installation discovery
  - JIT user provisioning
- ✅ RepoProvider interface (abstraction for future multi-provider)
- ✅ Storage abstraction (UserStore, IdentityStore, SessionStore)
- ✅ Updated FastAPI endpoints for GitHub App OAuth
- ✅ Environment configuration (.env.example)

### Frontend Updates
- ✅ AuthContext refactored for new user model
- ✅ TopBar component updated for LinkedIdentity
- ✅ HomePage component updated for GitHub App flow
- ✅ OAuth callback handling

### Documentation
- ✅ PHASE_2A_GITHUB_APP_OAUTH.md (comprehensive guide)
- ✅ .env.example (setup instructions)

## To Test Phase 2A

### 1. Create a GitHub App

```bash
# Visit: https://github.com/settings/apps/new
# Fill in:
Name: STF-Workbench-Dev
Homepage URL: http://localhost:5173
Callback URL: http://localhost:8000/auth/github/callback

# Permissions needed:
- Contents: Read & Write
- Pull Requests: Read & Write
- Workflows: Read & Write

# Installation location: Only on this account
```

### 2. Configure Environment

```bash
# Create .env file in project root
GITHUB_APP_ID=<your_app_id>
GITHUB_APP_PRIVATE_KEY=<contents_of_pem_file>
GITHUB_CLIENT_ID=<your_client_id>
GITHUB_CLIENT_SECRET=<your_client_secret>
GITHUB_REDIRECT_URI=http://localhost:8000/auth/github/callback
```

### 3. Run Backend & Frontend

```bash
# Terminal 1: Backend
cd /home/alex/github/stf-wb
source .venv/bin/activate
cd stfwb_web
uvicorn app:app --reload --port 8000

# Terminal 2: Frontend
cd /home/alex/github/stf-wb/stfwb_web_ui
npm run dev  # Runs on http://localhost:5173
```

### 4. Test the Flow

1. Visit http://localhost:5173
2. Click "Sign In with GitHub"
3. Authorize the app
4. Should redirect back with user info
5. Check browser console for any errors
6. Avatar should appear in TopBar

## Phase 2B: Installation & Repo Selection

After Phase 2A is tested, Phase 2B will add:

### What Phase 2B Will Include

1. **Installation Selector UI**
   - Show user's GitHub App installations
   - Let user select which org/repo to work with
   
2. **Repo Selection**
   - List repos accessible via selected installation
   - Show repo metadata (owner, description, visibility)
   
3. **Backend Endpoints**
   - `GET /repos/installations` - List user's installations
   - `GET /repos/installations/{id}/repositories` - List repos in installation
   - `POST /repos/select` - Record selected repo for project
   
4. **Token Minting**
   - `POST /repos/{installation_id}/token` - Get installation access token
   - JWT signing with app private key
   - 1-hour token expiry

5. **Frontend Integration**
   - Installation selector modal on project creation
   - Repo picker UI
   - Token caching with expiry tracking

## Architecture Diagram

```
User                       Frontend                  Backend
  |                          |                          |
  |--"Sign In"----->         |                          |
  |                    /auth/github/start              |
  |                          |---OAuth Start----->      |
  |                          |     (CSRF state)         |
  |<---Redirect to GitHub----|                          |
  |                                                     |
  | [User authorizes app, sees installations]          |
  |                                                     |
  |--Redirect with code---->                           |
  |                    /auth/github/callback            |
  |                          |--Exchange code---------> 
  |                          |<--User token (from GitHub)
  |                          |--Fetch user+installs-->
  |                          |<--User+installs--------
  |                          |--Create User+Identity-->
  |<--Redirect w/ user_id----|                          |
  |                    (stores in localStorage)        |
  |                          |                          |
  | [Home page with avatar]  |                          |
  |--Click "New Project"---> |                          |
  |                    [Show installations]             |
  |                          |--List installations----->
  |                          |<--Installations---------
  | [Select installation]    |                          |
  |                    [Show available repos]           |
  |                          |--List repos in inst------>
  |                          |<--Repos---------
  | [Select repo]            |                          |
  |                    [Create project]                 |
  |<--Project started--------|                          |
```

## Key Code Locations

- **Auth Models**: [stfwb_web/models_auth.py](../stfwb_web/models_auth.py)
- **GitHub App OAuth**: [stfwb_web/auth/github_app.py](../stfwb_web/auth/github_app.py)
- **Auth Endpoints**: [stfwb_web/app.py](../stfwb_web/app.py#L78-L170)
- **Frontend Auth**: [stfwb_web_ui/src/context/AuthContext.tsx](../stfwb_web_ui/src/context/AuthContext.tsx)
- **Storage Layer**: [stfwb_web/providers/storage.py](../stfwb_web/providers/storage.py)
- **Provider Interface**: [stfwb_web/providers/repo.py](../stfwb_web/providers/repo.py)

## Debugging Tips

### Backend
```bash
# Check OAuth flow logs
curl -v http://localhost:8000/auth/github/start

# Test auth endpoints
curl "http://localhost:8000/auth/user?user_id=test-id"  # Should return 401

# Check imports
python -c "from stfwb_web.auth.github_app import *; print('OK')"
```

### Frontend
```bash
# Check browser console for errors
# Check localStorage
localStorage.getItem('user_id')
localStorage.getItem('auth_user')

# Network tab for auth requests
# Check OAuth callback URL params
```

## Known Issues & TODOs

1. **In-Memory Storage**: Will need database for production
   - Plan: SQLAlchemy models for User, LinkedIdentity, AuthSession
   
2. **Token Expiry**: Installation tokens expire after 1 hour
   - Plan: Add token refresh logic in GitHubRepoProvider
   
3. **Error Messages**: Could be more descriptive
   - Plan: Add structured error codes and messages
   
4. **Private Key Management**: Currently in .env
   - Plan: Use secret manager (HashiCorp Vault, AWS Secrets Manager, etc.)
   
5. **Rate Limiting**: No rate limits on auth endpoints
   - Plan: Add Redis-based rate limiting
   
6. **CORS**: Localhost only for MVP
   - Plan: Refine for production domains

## Success Criteria for Phase 2A Testing

- [ ] GitHub App created and credentials in .env
- [ ] Backend starts without errors
- [ ] Frontend starts without errors  
- [ ] Can login with GitHub
- [ ] User ID stored in localStorage
- [ ] Avatar displays in TopBar
- [ ] Can logout
- [ ] Session persists on page refresh
- [ ] Proper error handling for failed auth

## Questions?

Refer to [PHASE_2A_GITHUB_APP_OAUTH.md](./PHASE_2A_GITHUB_APP_OAUTH.md) for detailed documentation.
