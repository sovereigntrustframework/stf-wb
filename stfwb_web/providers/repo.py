"""Repository provider abstraction."""

from abc import ABC, abstractmethod
from typing import Optional

from stfwb_web.models_auth import GitHubRepository, GitHubAppToken


class RepoRef:
    """Abstract reference to a repository."""

    pass


class GitHubRepoRef(RepoRef):
    """GitHub repository reference."""

    def __init__(self, owner: str, repo: str, installation_id: int):
        self.owner = owner
        self.repo = repo
        self.installation_id = installation_id

    @property
    def full_name(self) -> str:
        return f"{self.owner}/{self.repo}"


class RepoProvider(ABC):
    """Abstract interface for repository operations."""

    @abstractmethod
    async def list_accessible_repos(self) -> list[GitHubRepository]:
        """List repositories accessible to the authenticated user."""
        pass

    @abstractmethod
    async def get_access_token(self, repo_ref: RepoRef) -> str:
        """Get access token for a specific repository."""
        pass

    @abstractmethod
    async def clone(self, repo_ref: RepoRef, target_path: str) -> None:
        """Clone a repository."""
        pass

    @abstractmethod
    async def create_branch(self, repo_ref: RepoRef, branch_name: str, from_branch: str = "main") -> None:
        """Create a new branch."""
        pass

    @abstractmethod
    async def commit(
        self,
        repo_ref: RepoRef,
        branch: str,
        message: str,
        files: dict[str, str],
    ) -> str:
        """Commit changes (returns commit SHA)."""
        pass

    @abstractmethod
    async def create_pull_request(
        self,
        repo_ref: RepoRef,
        title: str,
        body: str,
        head: str,
        base: str = "main",
    ) -> dict:
        """Create a pull request."""
        pass

    @abstractmethod
    async def merge_pull_request(self, repo_ref: RepoRef, pr_number: int) -> None:
        """Merge a pull request."""
        pass


class GitHubRepoProvider(RepoProvider):
    """GitHub repository provider using GitHub App."""

    def __init__(self, user_id: str, installations: list):
        self.user_id = user_id
        self.installations = {inst.installation_id: inst for inst in installations}

    async def list_accessible_repos(self) -> list[GitHubRepository]:
        """List all GitHub repositories accessible to the user."""
        # TODO: Implement using GitHub App API
        pass

    async def get_access_token(self, repo_ref: RepoRef) -> str:
        """Get access token for a repository."""
        if not isinstance(repo_ref, GitHubRepoRef):
            raise ValueError("Expected GitHubRepoRef")

        # TODO: Mint installation access token
        pass

    async def clone(self, repo_ref: RepoRef, target_path: str) -> None:
        """Clone a repository."""
        # TODO: Implement git clone
        pass

    async def create_branch(self, repo_ref: RepoRef, branch_name: str, from_branch: str = "main") -> None:
        """Create a new branch."""
        # TODO: Implement git branch creation
        pass

    async def commit(
        self,
        repo_ref: RepoRef,
        branch: str,
        message: str,
        files: dict[str, str],
    ) -> str:
        """Commit changes."""
        # TODO: Implement git commit
        pass

    async def create_pull_request(
        self,
        repo_ref: RepoRef,
        title: str,
        body: str,
        head: str,
        base: str = "main",
    ) -> dict:
        """Create a pull request."""
        # TODO: Implement PR creation
        pass

    async def merge_pull_request(self, repo_ref: RepoRef, pr_number: int) -> None:
        """Merge a pull request."""
        # TODO: Implement PR merge
        pass
