"""CLI smoke tests using Click's CliRunner."""

from pathlib import Path

from click.testing import CliRunner

from stfwb_cli.main import cli


def test_cli_version_and_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0-alpha" in result.output

    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "STF-WB" in result.output


def test_cli_project_create():
    runner = CliRunner()
    result = runner.invoke(
        cli, ["project", "create", "--name", "demo", "--target-uri", "https://example.org/x"]
    )
    assert result.exit_code == 0
    assert "Creating project 'demo' targeting https://example.org/x" in result.output


def test_cli_iteration_commands():
    from pathlib import Path
    from tempfile import TemporaryDirectory

    runner = CliRunner()
    with TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # Create an iteration first
        create_result = runner.invoke(
            cli,
            ["iteration", "create", "--project-id", "p1", "--store-dir", str(tmp_path)],
        )
        assert create_result.exit_code == 0
        assert "Creating iteration for project p1" in create_result.output

        # Extract iteration ID from output
        import re

        match = re.search(r"Created iteration ([0-9a-f\-]+)", create_result.output)
        assert match is not None
        iteration_id = match.group(1)

        # Run the iteration
        run_result = runner.invoke(
            cli,
            ["iteration", "run", "--iteration-id", iteration_id, "--store-dir", str(tmp_path)],
        )
        assert run_result.exit_code == 0
        assert f"Running iteration {iteration_id}" in run_result.output
        assert "Starting iteration..." in run_result.output


def test_cli_publish_command(tmp_path: Path):
    """Test publish command with dry-run."""
    from stfwb.core.iteration import Iteration
    from stfwb.utils.storage import save_iteration
    
    # Create an iteration to publish
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
            "ghp_xxx",
            "--dry-run",
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0
    assert "[DRY RUN]" in result.output
