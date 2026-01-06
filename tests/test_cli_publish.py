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


def test_publish_missing_repo(tmp_path: Path) -> None:
    """Publish should fail when repo is not provided and no config/env fallback exists."""
    it = Iteration(project_id="p1")
    save_iteration(it, tmp_path)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "publish",
            "--iteration-id",
            it.id,
            "--token",
            "ghp_test",
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 1
    assert "GitHub repo not provided" in result.output


def test_publish_missing_token(tmp_path: Path) -> None:
    """Publish should fail when token is not provided and no config/env fallback exists."""
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
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 1
    assert "GitHub token not provided" in result.output


@patch("stfwb.publishers.github.GitHubPublisher")
def test_publish_uses_env_store_and_credentials(
    mock_publisher_class: MagicMock, tmp_path: Path, monkeypatch
) -> None:
    """Publish should use env-configured store and credentials when flags are omitted."""
    mock_publisher = MagicMock()
    mock_publisher.publish.return_value = {
        "success": True,
        "issue_url": "https://github.com/owner/repo/issues/99",
        "error": None,
    }
    mock_publisher_class.return_value = mock_publisher

    store_dir = tmp_path / "env_store"
    store_dir.mkdir()

    it = Iteration(project_id="p1")
    save_iteration(it, store_dir)

    import stfwb.utils.config as cfg_module

    cfg_module._instance = None
    monkeypatch.setenv("STFWB_STORE_DIR", str(store_dir))
    monkeypatch.setenv("STFWB_GITHUB_TOKEN", "ghp_env")
    monkeypatch.setenv("STFWB_GITHUB_REPO", "owner/repo")

    runner = CliRunner()
    result = runner.invoke(cli, ["publish", "--iteration-id", it.id])

    assert result.exit_code == 0
    assert "Published successfully" in result.output
    assert "https://github.com/owner/repo/issues/99" in result.output
