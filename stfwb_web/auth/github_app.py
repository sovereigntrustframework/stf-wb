"""GitHub App authentication handler."""

import json
import logging
from datetime import datetime, timedelta
from typing import Optional

import httpx
import jwt

from stfwb_web.models_auth import (
    ExternalIdentity,
    LinkedIdentity,
    ProviderId,
    User,
    GitHubInstallation,
    GitHubRepository,
    GitHubAppToken,
)

logger = logging.getLogger(__name__)


class GitHubAppOAuthConfig:
    """GitHub App OAuth configuration."""

    def __init__(
        self,
        app_id: str,
        private_key: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str = "http://localhost:8000/auth/github/callback",
    ):
        self.app_id = app_id
        self.private_key = private_key
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.auth_url = "https://github.com/login/oauth/authorize"
        self.token_url = "https://github.com/login/oauth/access_token"
        self.user_url = "https://api.github.com/user"
        self.installations_url = "https://api.github.com/user/installations"
        self.installation_repos_url = "https://api.github.com/user/installations/{installation_id}/repositories"

    def get_authorization_url(self, state: str) -> str:
        """Get GitHub OAuth authorization URL for GitHub App."""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "read:user,read:org",  # Read-only for app installation discovery
            "state": state,
        }
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.auth_url}?{query_string}"

    async def exchange_code_for_token(self, code: str) -> dict:
        """Exchange authorization code for user access token."""
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

    async def fetch_user(self, access_token: str) -> ExternalIdentity:
        """Fetch authenticated user info from GitHub."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.user_url,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            data = response.json()

            # Use stable GitHub user ID as subject, not username
            return ExternalIdentity(
                provider=ProviderId.GITHUB,
                subject=str(data["id"]),  # GitHub user ID
                display=data.get("login"),
                email=data.get("email"),
                avatar_url=data.get("avatar_url"),
            )

    async def fetch_installations(self, access_token: str) -> list[GitHubInstallation]:
        """Fetch GitHub App installations for the authenticated user."""
        installations = []
        page = 1

        async with httpx.AsyncClient() as client:
            while True:
                response = await client.get(
                    self.installations_url,
                    headers={"Authorization": f"Bearer {access_token}"},
                    params={"page": page, "per_page": 100},
                )
                response.raise_for_status()
                data = response.json()

                for inst_data in data.get("installations", []):
                    installations.append(
                        GitHubInstallation(
                            installation_id=inst_data["id"],
                            account_type=inst_data["account"]["type"],
                            account_login=inst_data["account"]["login"],
                            account_id=inst_data["account"]["id"],
                            avatar_url=inst_data["account"].get("avatar_url"),
                            repositories_url=inst_data["repositories_url"],
                        )
                    )

                if len(data.get("installations", [])) < 100:
                    break

                page += 1

        logger.info(f"Fetched {len(installations)} GitHub App installations for user")
        return installations

    async def mint_installation_token(self, installation_id: int) -> GitHubAppToken:
        """
        Mint a short-lived installation access token for a GitHub App.

        Uses the app's private key to create a JWT, then exchanges it for
        an installation token (valid for 1 hour).
        """
        # Create JWT signed with app private key
        now = datetime.utcnow()
        jwt_payload = {
            "iss": int(self.app_id),
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=10)).timestamp()),
        }

        try:
            token_jwt = jwt.encode(
                jwt_payload,
                self.private_key,
                algorithm="RS256",
            )
        except Exception as e:
            logger.error(f"Failed to create JWT: {e}")
            raise

        # Exchange JWT for installation token
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.github.com/app/installations/{installation_id}/access_tokens",
                headers={
                    "Authorization": f"Bearer {token_jwt}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )
            response.raise_for_status()
            data = response.json()

            expires_at = datetime.fromisoformat(data["expires_at"].replace("Z", "+00:00"))

            logger.info(f"Minted installation token for installation {installation_id} (expires {expires_at})")

            return GitHubAppToken(
                token=data["token"],
                expires_at=expires_at,
                installation_id=installation_id,
            )

    async def authenticate(self, code: str) -> tuple[User, LinkedIdentity, list[GitHubInstallation]]:
        """
        Authenticate user with GitHub App via OAuth.

        Returns (user, linked_identity, installations) for JIT provisioning.
        """
        try:
            # Exchange code for user access token
            token_data = await self.exchange_code_for_token(code)

            if "error" in token_data:
                raise ValueError(f"GitHub error: {token_data.get('error_description', 'Unknown error')}")

            access_token = token_data["access_token"]

            # Fetch user info
            external_identity = await self.fetch_user(access_token)

            # Fetch GitHub App installations
            installations = await self.fetch_installations(access_token)

            # Create internal user (JIT provisioning)
            user = User.new()

            # Create linked identity
            linked_identity = LinkedIdentity.new(user.user_id, ProviderId.GITHUB, external_identity)

            logger.info(f"GitHub App authentication successful: {external_identity.display} (user_id={user.user_id})")

            return user, linked_identity, installations

        except Exception as e:
            logger.error(f"GitHub App authentication failed: {e}")
            raise


# Global OAuth config instance
_oauth_config: Optional[GitHubAppOAuthConfig] = None


def initialize_github_app_oauth(
    app_id: str,
    private_key: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str = "http://localhost:8000/auth/github/callback",
):
    """Initialize GitHub App OAuth configuration."""
    global _oauth_config
    _oauth_config = GitHubAppOAuthConfig(app_id, private_key, client_id, client_secret, redirect_uri)
    logger.info(f"GitHub App OAuth initialized (app_id={app_id})")


def get_github_app_oauth() -> GitHubAppOAuthConfig:
    """Get GitHub App OAuth config."""
    if _oauth_config is None:
        raise RuntimeError("GitHub App OAuth not initialized. Call initialize_github_app_oauth() first.")
    return _oauth_config
