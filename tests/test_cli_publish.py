"""Tests for the publish command."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from stfwb.core.iteration import Iteration
from stfwb.utils.storage import save_iteration
from stfwb_cli.main import cli


def test_publish_dry_run(tmp_path: Path) -> None:
    """Test dry-run mode."""
    # Create and save an iteration
    it = Iteration(project_id="p1")
    it.start()
    save_iteration(it, tmp_path)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "publish",
            "--iteration-id",
            it.id,
            "--repo",
            "owner/repo",
            "--token",
            "ghp_test",
            "--dry-run",
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0
    assert "[DRY RUN]" in result.output
    assert "Would publish" in result.output


def test_publish_not_found(tmp_path: Path) -> None:
    """Test publishing non-existent iteration."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "publish",
            "--iteration-id",
            "nonexistent",
            "--repo",
            "owner/repo",
            "--token",
            "ghp_test",
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 1
    assert "not found" in result.output


@patch("stfwb.publishers.github.GitHubPublisher")
def test_publish_success(mock_publisher_class: MagicMock, tmp_path: Path) -> None:
    """Test successful publishing."""
    # Setup mock
    mock_publisher = MagicMock()
    mock_publisher.publish.return_value = {
        "success": True,
        "issue_url": "https://github.com/owner/repo/issues/123",
        "error": None,
    }
    mock_publisher_class.return_value = mock_publisher

    # Create and save an iteration
    it = Iteration(project_id="p1")
    it.start()
    save_iteration(it, tmp_path)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "publish",
            "--iteration-id",
            it.id,
            "--repo",
            "owner/repo",
            "--token",
            "ghp_test",
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0
    assert "Published successfully" in result.output
    assert "https://github.com/owner/repo/issues/123" in result.output


@patch("stfwb.publishers.github.GitHubPublisher")
def test_publish_failure(mock_publisher_class: MagicMock, tmp_path: Path) -> None:
    """Test failed publishing."""
    # Setup mock
    mock_publisher = MagicMock()
    mock_publisher.publish.return_value = {
        "success": False,
        "issue_url": None,
        "error": "API rate limit exceeded",
    }
    mock_publisher_class.return_value = mock_publisher

    # Create and save an iteration
    it = Iteration(project_id="p1")
    save_iteration(it, tmp_path)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "publish",
            "--iteration-id",
            it.id,
            "--repo",
            "owner/repo",
            "--token",
            "ghp_test",
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 1
    assert "Failed to publish" in result.output
    assert "API rate limit exceeded" in result.output
