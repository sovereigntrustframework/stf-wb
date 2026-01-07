"""Tests for GitHub publisher."""

from unittest.mock import MagicMock, patch

import pytest

from stfwb.core.iteration import Iteration
from stfwb.publishers.github import GitHubPublisher
from stfwb.steps.runner import run_steps


def test_github_publisher_init() -> None:
    """Test GitHubPublisher initialization."""
    publisher = GitHubPublisher(token="ghp_test", repo="owner/repo")
    assert publisher.token == "ghp_test"
    assert publisher.repo == "owner/repo"
    assert publisher.api_base == "https://api.github.com"
    assert "Authorization" in publisher.headers


def test_github_publisher_dry_run() -> None:
    """Test dry-run mode."""
    publisher = GitHubPublisher(token="ghp_test", repo="owner/repo")
    iteration = Iteration(project_id="p1")

    result = publisher.publish(iteration, dry_run=True)

    assert result["success"] is True
    assert result["issue_url"] is not None
    assert "github.com" in result["issue_url"]
    assert result["error"] is None


def test_github_publisher_build_issue_body_empty() -> None:
    """Test building issue body for iteration with no steps."""
    publisher = GitHubPublisher(token="ghp_test", repo="owner/repo")
    iteration = Iteration(project_id="p1")

    body = publisher._build_issue_body(iteration)

    assert f"# Iteration {iteration.id}" in body
    assert "**Project:** p1" in body
    assert "**State:** created" in body
    assert "No steps completed yet" in body


def test_github_publisher_build_issue_body_with_steps() -> None:
    """Test building issue body for iteration with steps."""
    publisher = GitHubPublisher(token="ghp_test", repo="owner/repo")
    iteration = Iteration(project_id="p1")
    iteration.start()
    run_steps(iteration, 2)

    body = publisher._build_issue_body(iteration)

    assert f"# Iteration {iteration.id}" in body
    assert "### S0 - completed" in body
    assert "### S1 - completed" in body
    assert "```json" in body


@patch("stfwb.publishers.github.requests.post")
def test_github_publisher_create_issue_success(mock_post: MagicMock) -> None:
    """Test successful issue creation."""
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"html_url": "https://github.com/owner/repo/issues/123"}
    mock_post.return_value = mock_response

    publisher = GitHubPublisher(token="ghp_test", repo="owner/repo")
    url = publisher._create_issue("Test Issue", "Test body")

    assert url == "https://github.com/owner/repo/issues/123"
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert call_args.kwargs["json"]["title"] == "Test Issue"
    assert call_args.kwargs["json"]["body"] == "Test body"


@patch("stfwb.publishers.github.requests.post")
def test_github_publisher_create_issue_failure(mock_post: MagicMock) -> None:
    """Test failed issue creation."""
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.text = "Forbidden"
    mock_post.return_value = mock_response

    publisher = GitHubPublisher(token="ghp_test", repo="owner/repo")

    with pytest.raises(RuntimeError, match="GitHub API error"):
        publisher._create_issue("Test Issue", "Test body")


@patch("stfwb.publishers.github.requests.post")
def test_github_publisher_publish_success(mock_post: MagicMock) -> None:
    """Test successful iteration publishing."""
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"html_url": "https://github.com/owner/repo/issues/123"}
    mock_post.return_value = mock_response

    publisher = GitHubPublisher(token="ghp_test", repo="owner/repo")
    iteration = Iteration(project_id="p1")
    iteration.start()

    result = publisher.publish(iteration, dry_run=False)

    assert result["success"] is True
    assert result["issue_url"] == "https://github.com/owner/repo/issues/123"
    assert result["error"] is None


@patch("stfwb.publishers.github.requests.post")
def test_github_publisher_publish_failure(mock_post: MagicMock) -> None:
    """Test failed iteration publishing."""
    mock_post.side_effect = Exception("Network error")

    publisher = GitHubPublisher(token="ghp_test", repo="owner/repo")
    iteration = Iteration(project_id="p1")

    result = publisher.publish(iteration, dry_run=False)

    assert result["success"] is False
    assert result["issue_url"] is None
    assert "Network error" in result["error"]


def test_github_publisher_issue_title_format() -> None:
    """Test issue title format."""
    publisher = GitHubPublisher(token="ghp_test", repo="owner/repo")
    iteration = Iteration(project_id="test-project")

    body = publisher._build_issue_body(iteration)
    # Check that iteration ID is truncated in title (first 8 chars)
    assert iteration.id[:8] in body
