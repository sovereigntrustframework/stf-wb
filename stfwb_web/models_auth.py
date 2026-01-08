"""User and identity models for provider abstraction."""

from datetime import datetime
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel


class ProviderId(str, Enum):
    """Identity provider types."""

    GITHUB = "github"
    GITLAB = "gitlab"
    EMAIL = "email"
    SSI = "ssi"


class ExternalIdentity(BaseModel):
    """External identity from a provider (GitHub, GitLab, etc.)."""

    provider: ProviderId
    subject: str  # Stable provider identifier (not username)
    display: str | None = None  # login/email/did for UI
    email: str | None = None
    avatar_url: str | None = None


class User(BaseModel):
    """Internal user record (provider-agnostic)."""

    user_id: str  # UUID
    created_at: datetime
    updated_at: datetime

    @classmethod
    def new(cls) -> "User":
        """Create a new user."""
        now = datetime.utcnow()
        return cls(
            user_id=str(uuid4()),
            created_at=now,
            updated_at=now,
        )


class LinkedIdentity(BaseModel):
    """Link between a User and an external identity provider."""

    user_id: str
    provider: ProviderId
    subject: str  # Stable provider identifier
    display: str | None = None
    email: str | None = None
    avatar_url: str | None = None
    created_at: datetime
    last_login_at: datetime | None = None

    @classmethod
    def new(
        cls,
        user_id: str,
        provider: ProviderId,
        external_identity: ExternalIdentity,
    ) -> "LinkedIdentity":
        """Create a new linked identity."""
        now = datetime.utcnow()
        return cls(
            user_id=user_id,
            provider=provider,
            subject=external_identity.subject,
            display=external_identity.display,
            email=external_identity.email,
            avatar_url=external_identity.avatar_url,
            created_at=now,
            last_login_at=now,
        )


class AuthSession(BaseModel):
    """Server-side session with authenticated user."""

    user_id: str
    identities: list[LinkedIdentity]
    created_at: datetime


class GitHubInstallation(BaseModel):
    """GitHub App installation for a user."""

    installation_id: int
    account_type: str  # "User" or "Organization"
    account_login: str
    account_id: int
    avatar_url: str | None = None
    repositories_url: str


class GitHubRepository(BaseModel):
    """GitHub repository accessible to user."""

    repo_id: int
    owner: str
    name: str
    full_name: str
    description: str | None = None
    html_url: str
    is_private: bool
    installation_id: int  # Which installation can access this


class GitHubAppToken(BaseModel):
    """GitHub App installation access token."""

    token: str
    expires_at: datetime
    installation_id: int

    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.utcnow() > self.expires_at
