"""Provider storage abstraction."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from stfwb_web.models_auth import User, LinkedIdentity, AuthSession


class UserStore(ABC):
    """Abstract interface for user storage."""

    @abstractmethod
    async def create_user(self, user: User) -> None:
        """Create a new user."""
        pass

    @abstractmethod
    async def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        pass

    @abstractmethod
    async def get_user_by_identity(self, provider: str, subject: str) -> Optional[User]:
        """Get a user by external identity (provider + subject)."""
        pass


class IdentityStore(ABC):
    """Abstract interface for linked identity storage."""

    @abstractmethod
    async def link_identity(self, identity: LinkedIdentity) -> None:
        """Link an external identity to a user."""
        pass

    @abstractmethod
    async def get_identities(self, user_id: str) -> list[LinkedIdentity]:
        """Get all linked identities for a user."""
        pass

    @abstractmethod
    async def update_last_login(self, user_id: str, provider: str) -> None:
        """Update last login timestamp for an identity."""
        pass


class SessionStore(ABC):
    """Abstract interface for session storage."""

    @abstractmethod
    async def create_session(self, session: AuthSession) -> None:
        """Create a session."""
        pass

    @abstractmethod
    async def get_session(self, user_id: str) -> Optional[AuthSession]:
        """Get a session by user ID."""
        pass

    @abstractmethod
    async def delete_session(self, user_id: str) -> None:
        """Delete a session."""
        pass


class InMemoryUserStore(UserStore):
    """In-memory user store for MVP."""

    def __init__(self):
        self.users: dict[str, User] = {}
        self.by_identity: dict[tuple[str, str], str] = {}  # (provider, subject) -> user_id

    async def create_user(self, user: User) -> None:
        self.users[user.user_id] = user

    async def get_user(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)

    async def get_user_by_identity(self, provider: str, subject: str) -> Optional[User]:
        user_id = self.by_identity.get((provider, subject))
        if user_id:
            return await self.get_user(user_id)
        return None

    def _register_identity(self, user_id: str, provider: str, subject: str):
        """Internal: register identity mapping."""
        self.by_identity[(provider, subject)] = user_id


class InMemoryIdentityStore(IdentityStore):
    """In-memory identity store for MVP."""

    def __init__(self):
        self.identities: dict[str, list[LinkedIdentity]] = {}  # user_id -> [identities]

    async def link_identity(self, identity: LinkedIdentity) -> None:
        if identity.user_id not in self.identities:
            self.identities[identity.user_id] = []
        self.identities[identity.user_id].append(identity)

    async def get_identities(self, user_id: str) -> list[LinkedIdentity]:
        return self.identities.get(user_id, [])

    async def update_last_login(self, user_id: str, provider: str) -> None:
        if user_id in self.identities:
            for identity in self.identities[user_id]:
                if identity.provider.value == provider:
                    identity.last_login_at = datetime.utcnow()


class InMemorySessionStore(SessionStore):
    """In-memory session store for MVP."""

    def __init__(self):
        self.sessions: dict[str, AuthSession] = {}

    async def create_session(self, session: AuthSession) -> None:
        self.sessions[session.user_id] = session

    async def get_session(self, user_id: str) -> Optional[AuthSession]:
        return self.sessions.get(user_id)

    async def delete_session(self, user_id: str) -> None:
        if user_id in self.sessions:
            del self.sessions[user_id]


# Global store instances
_user_store: Optional[UserStore] = None
_identity_store: Optional[IdentityStore] = None
_session_store: Optional[SessionStore] = None


def initialize_stores():
    """Initialize default stores for MVP."""
    global _user_store, _identity_store, _session_store
    _user_store = InMemoryUserStore()
    _identity_store = InMemoryIdentityStore()
    _session_store = InMemorySessionStore()


def get_user_store() -> UserStore:
    if _user_store is None:
        raise RuntimeError("Stores not initialized")
    return _user_store


def get_identity_store() -> IdentityStore:
    if _identity_store is None:
        raise RuntimeError("Stores not initialized")
    return _identity_store


def get_session_store() -> SessionStore:
    if _session_store is None:
        raise RuntimeError("Stores not initialized")
    return _session_store

