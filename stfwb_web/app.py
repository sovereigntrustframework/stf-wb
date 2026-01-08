"""FastAPI application for STF-Workbench Web UI."""

import asyncio
import json
import logging
import os
import secrets
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, RedirectResponse
from pydantic import BaseModel

from stfwb_web.models import RunInfo, RunStatus, StepName
from stfwb_web.models_auth import AuthSession
from stfwb_web.auth.github_app import initialize_github_app_oauth, get_github_app_oauth
from stfwb_web.providers.storage import initialize_stores, get_user_store, get_identity_store, get_session_store

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# In-memory storage for MVP (will be replaced with proper state management)
active_runs: dict[str, RunInfo] = {}
event_queues: list[asyncio.Queue] = []
oauth_states: dict[str, dict] = {}  # CSRF states for OAuth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting STF-Workbench Web UI")

    # Initialize storage
    initialize_stores()
    logger.info("Storage providers initialized")

    # Initialize GitHub App OAuth if credentials are available
    github_app_id = os.getenv("GITHUB_APP_ID")
    github_app_private_key = os.getenv("GITHUB_APP_PRIVATE_KEY")
    github_client_id = os.getenv("GITHUB_CLIENT_ID")
    github_client_secret = os.getenv("GITHUB_CLIENT_SECRET")
    github_redirect_uri = os.getenv("GITHUB_REDIRECT_URI", "http://localhost:8000/auth/github/callback")

    if github_app_id and github_app_private_key and github_client_id and github_client_secret:
        initialize_github_app_oauth(
            github_app_id,
            github_app_private_key,
            github_client_id,
            github_client_secret,
            github_redirect_uri,
        )
        logger.info("GitHub App OAuth configured")
    else:
        logger.warning(
            "GitHub App OAuth credentials not fully configured. Set GITHUB_APP_ID, GITHUB_APP_PRIVATE_KEY, "
            "GITHUB_CLIENT_ID, and GITHUB_CLIENT_SECRET"
        )

    yield
    logger.info("Shutting down STF-Workbench Web UI")


app = FastAPI(
    title="STF-Workbench Web UI",
    description="Web interface for STF-Workbench CI/CD pipeline",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    timestamp: datetime
    version: str


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy", timestamp=datetime.now(), version="0.1.0"
    )


# ============================================================================
# Authentication Endpoints (GitHub App OAuth)
# ============================================================================


@app.get("/auth/github/start")
async def auth_start():
    """
    Start GitHub OAuth flow for app installation discovery.

    Returns a redirect to GitHub authorization URL.
    """
    try:
        oauth = get_github_app_oauth()
    except RuntimeError:
        raise HTTPException(status_code=503, detail="GitHub App OAuth not configured")

    # Generate CSRF state token
    state = secrets.token_urlsafe(32)
    oauth_states[state] = {"created_at": datetime.now().isoformat()}

    auth_url = oauth.get_authorization_url(state)
    logger.info(f"GitHub App OAuth flow started (state={state})")
    return RedirectResponse(url=auth_url)


@app.get("/auth/github/callback")
async def auth_callback(code: str = Query(...), state: str = Query(...)):
    """
    GitHub OAuth callback - exchanges code for user token and installations.

    This implements JIT (Just-In-Time) user provisioning:
    1. Exchange code for GitHub user access token
    2. Fetch user info (establishes identity)
    3. Fetch GitHub App installations accessible to user
    4. Create internal User + LinkedIdentity (first login)
    5. Store session with installations
    """
    try:
        oauth = get_github_app_oauth()
    except RuntimeError:
        raise HTTPException(status_code=503, detail="GitHub App OAuth not configured")

    # Verify CSRF state
    if state not in oauth_states:
        logger.warning(f"Invalid CSRF state: {state}")
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    try:
        # Authenticate with GitHub (JIT provisioning)
        user, linked_identity, installations = await oauth.authenticate(code)

        # Store user and identity
        user_store = get_user_store()
        identity_store = get_identity_store()
        session_store = get_session_store()

        await user_store.create_user(user)
        await identity_store.link_identity(linked_identity)

        # Create session
        auth_session = AuthSession(
            user_id=user.user_id,
            identities=[linked_identity],
            created_at=datetime.utcnow(),
        )
        await session_store.create_session(auth_session)

        # Clean up CSRF state
        del oauth_states[state]

        logger.info(f"User authenticated (JIT): {user.user_id} - {linked_identity.display}")

        # Return auth token to frontend
        # TODO: Use secure httpOnly cookies in production
        return RedirectResponse(
            url=f"http://localhost:5173/auth/success?user_id={user.user_id}&login={linked_identity.display}&installations={len(installations)}"
        )

    except Exception as e:
        logger.error(f"GitHub App OAuth callback error: {e}")
        return RedirectResponse(
            url=f"http://localhost:5173/auth/error?message={str(e)}"
        )


@app.get("/auth/user")
async def get_current_user(user_id: str = Query(...)):
    """
    Get current authenticated user.

    Args:
        user_id: User ID from session

    Returns:
        User information and linked identities
    """
    user_store = get_user_store()
    identity_store = get_identity_store()

    user = await user_store.get_user(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    identities = await identity_store.get_identities(user_id)

    return {
        "user_id": user.user_id,
        "created_at": user.created_at,
        "identities": [
            {
                "provider": identity.provider.value,
                "display": identity.display,
                "avatar_url": identity.avatar_url,
                "last_login_at": identity.last_login_at,
            }
            for identity in identities
        ],
    }


@app.post("/auth/logout")
async def logout(user_id: str = Query(...)):
    """
    Logout user and invalidate session.

    Args:
        user_id: User ID to log out
    """
    session_store = get_session_store()
    await session_store.delete_session(user_id)
    logger.info(f"User logged out: {user_id}")
    return {"status": "logged_out"}


async def event_generator() -> AsyncIterator[str]:
    """
    Generate SSE events for active runs.

    Event format:
    data: {"type": "event_type", "payload": {...}}

    Event types:
    - run.created: New run started
    - run.started: Run execution began
    - step.started: Step execution started
    - step.completed: Step execution finished
    - step.failed: Step execution failed
    - publish.progress: Publication progress update
    - run.completed: Run finished successfully
    - run.failed: Run failed
    """
    queue: asyncio.Queue = asyncio.Queue()
    event_queues.append(queue)

    try:
        # Send initial connection event
        yield f"data: {json.dumps({'type': 'connection.established', 'payload': {'timestamp': datetime.now().isoformat()}})}\n\n"

        # Send periodic heartbeat and events
        while True:
            try:
                # Wait for events with timeout for heartbeat
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield f"data: {json.dumps(event)}\n\n"
            except asyncio.TimeoutError:
                # Send heartbeat
                yield f"data: {json.dumps({'type': 'heartbeat', 'payload': {'timestamp': datetime.now().isoformat()}})}\n\n"
    except asyncio.CancelledError:
        logger.info("Client disconnected from event stream")
    finally:
        event_queues.remove(queue)


@app.get("/events")
async def events():
    """
    Server-Sent Events endpoint for real-time updates.

    Subscribe to this endpoint to receive real-time updates about:
    - Run creation and status changes
    - Step execution progress
    - Publication progress
    - Errors and failures

    Returns:
        StreamingResponse: SSE stream with JSON-encoded events
    """
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable buffering in nginx
        },
    )


async def broadcast_event(event_type: str, payload: dict):
    """
    Broadcast an event to all connected clients.

    Args:
        event_type: Type of event (e.g., "run.started", "step.completed")
        payload: Event payload data
    """
    event = {"type": event_type, "payload": payload}
    logger.info(f"Broadcasting event: {event_type}")

    for queue in event_queues:
        try:
            await queue.put(event)
        except Exception as e:
            logger.error(f"Error broadcasting to queue: {e}")


# Test endpoint to simulate events (will be removed)
@app.post("/test/emit")
async def emit_test_event(event_type: str, payload: dict):
    """Emit a test event (development only)."""
    await broadcast_event(event_type, payload)
    return {"status": "emitted", "type": event_type}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
