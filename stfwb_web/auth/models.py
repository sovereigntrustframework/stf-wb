"""User and authentication models."""

from datetime import datetime
from pydantic import BaseModel


class GitHubUser(BaseModel):
    """GitHub user information."""

    id: int
    login: str
    name: str | None
    avatar_url: str | None
    html_url: str


class UserSession(BaseModel):
    """User session with GitHub token."""

    user: GitHubUser
    access_token: str
    token_type: str = "bearer"
    created_at: datetime
    expires_at: datetime | None = None

    @property
    def is_expired(self) -> bool:
        """Check if session token is expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at


class AuthResponse(BaseModel):
    """Authentication response."""

    user: GitHubUser
    access_token: str
    token_type: str = "bearer"


class AuthError(BaseModel):
    """Authentication error response."""

    error: str
    error_description: str
