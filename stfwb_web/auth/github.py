"""GitHub OAuth authentication handler."""

import logging
from datetime import datetime, timedelta
from typing import Optional

import httpx

from stfwb_web.auth.models import GitHubUser, UserSession

logger = logging.getLogger(__name__)


class GitHubOAuthConfig:
    """GitHub OAuth configuration."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str = "http://localhost:8000/auth/callback",
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.auth_url = "https://github.com/login/oauth/authorize"
        self.token_url = "https://github.com/login/oauth/access_token"
        self.user_url = "https://api.github.com/user"

    def get_authorization_url(self, state: str) -> str:
        """Get GitHub authorization URL."""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "repo,read:user",
            "state": state,
        }
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.auth_url}?{query_string}"

    async def exchange_code_for_token(self, code: str) -> dict:
        """Exchange authorization code for access token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                },
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            return response.json()

    async def fetch_user(self, access_token: str) -> GitHubUser:
        """Fetch authenticated user info from GitHub."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.user_url,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            data = response.json()

            return GitHubUser(
                id=data["id"],
                login=data["login"],
                name=data.get("name"),
                avatar_url=data.get("avatar_url"),
                html_url=data["html_url"],
            )

    async def authenticate(self, code: str) -> UserSession:
        """Authenticate user with GitHub code."""
        try:
            # Exchange code for token
            token_data = await self.exchange_code_for_token(code)

            if "error" in token_data:
                raise ValueError(f"GitHub error: {token_data.get('error_description', 'Unknown error')}")

            access_token = token_data["access_token"]

            # Fetch user info
            user = await self.fetch_user(access_token)

            # Create session
            now = datetime.utcnow()
            expires_in = token_data.get("expires_in")
            expires_at = now + timedelta(seconds=expires_in) if expires_in else None

            session = UserSession(
                user=user,
                access_token=access_token,
                created_at=now,
                expires_at=expires_at,
            )

            logger.info(f"User authenticated: {user.login}")
            return session

        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise


# Global OAuth config instance
_oauth_config: Optional[GitHubOAuthConfig] = None


def initialize_oauth(client_id: str, client_secret: str, redirect_uri: str = "http://localhost:8000/auth/callback"):
    """Initialize GitHub OAuth configuration."""
    global _oauth_config
    _oauth_config = GitHubOAuthConfig(client_id, client_secret, redirect_uri)
    logger.info(f"GitHub OAuth initialized with client_id={client_id}")


def get_oauth_config() -> GitHubOAuthConfig:
    """Get OAuth config."""
    if _oauth_config is None:
        raise RuntimeError("OAuth not initialized. Call initialize_oauth() first.")
    return _oauth_config
