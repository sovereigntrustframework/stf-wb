"""GitHub publisher for STF-WB artifacts.

Publishes iteration artifacts to GitHub as issues, comments, and pull requests.
"""

from __future__ import annotations

import json
from typing import Any, TypedDict

import requests

from stfwb.core.iteration import Iteration
from stfwb.utils.logging import get_logger

_log = get_logger("stfwb.publishers.github")


class PublishResult(TypedDict):
    """Result of publishing an iteration to GitHub."""

    success: bool
    issue_url: str | None
    error: str | None


class GitHubPublisher:
    """Publisher for GitHub integration."""

    def __init__(self, token: str, repo: str) -> None:
        """Initialize GitHub publisher.

        Args:
            token: GitHub personal access token
            repo: Repository in format "owner/repo"
        """
        self.token = token
        self.repo = repo
        self.api_base = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def publish(self, iteration: Iteration, dry_run: bool = False) -> PublishResult:
        """Publish an iteration to GitHub.

        Creates a GitHub issue with iteration details and artifacts.

        Args:
            iteration: Iteration to publish
            dry_run: If True, simulate publishing without making API calls

        Returns:
            PublishResult with success status and issue URL
        """
        if dry_run:
            _log.info(f"[DRY RUN] Would publish iteration {iteration.id} to {self.repo}")
            return {
                "success": True,
                "issue_url": f"https://github.com/{self.repo}/issues/1",
                "error": None,
            }

        try:
            # Create issue with iteration summary
            issue_title = f"Iteration {iteration.id[:8]} - Project {iteration.project_id}"
            issue_body = self._build_issue_body(iteration)

            _log.info(f"Creating GitHub issue for iteration {iteration.id}")
            issue_url = self._create_issue(issue_title, issue_body)

            _log.info(f"Published iteration to {issue_url}")
            return {"success": True, "issue_url": issue_url, "error": None}

        except Exception as e:
            _log.error(f"Failed to publish iteration: {e}")
            return {"success": False, "issue_url": None, "error": str(e)}

    def _build_issue_body(self, iteration: Iteration) -> str:
        """Build markdown body for GitHub issue."""
        lines = [
            f"# Iteration {iteration.id}",
            "",
            f"**Project:** {iteration.project_id}",
            f"**State:** {iteration.state.value}",
            f"**Created:** {iteration.created_at}",
            "",
            "## Steps",
            "",
        ]

        if not iteration.steps:
            lines.append("No steps completed yet.")
        else:
            for step in iteration.steps:
                lines.append(f"### {step.step_id.upper()} - {step.status}")
                lines.append(f"- Started: {step.started_at}")
                lines.append(f"- Completed: {step.completed_at}")
                if step.result:
                    lines.append("")
                    lines.append("```json")
                    lines.append(json.dumps(step.result, indent=2))
                    lines.append("```")
                lines.append("")

        return "\n".join(lines)

    def _create_issue(self, title: str, body: str) -> str:
        """Create a GitHub issue.

        Args:
            title: Issue title
            body: Issue body (markdown)

        Returns:
            URL of created issue

        Raises:
            RuntimeError: If API call fails
        """
        url = f"{self.api_base}/repos/{self.repo}/issues"
        payload = {"title": title, "body": body}

        response = requests.post(url, headers=self.headers, json=payload, timeout=30)

        if response.status_code == 201:
            data = response.json()
            return str(data["html_url"])

        raise RuntimeError(f"GitHub API error: {response.status_code} - {response.text}")
