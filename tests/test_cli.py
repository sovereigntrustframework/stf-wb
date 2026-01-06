"""CLI smoke tests using Click's CliRunner."""

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
    runner = CliRunner()
    result = runner.invoke(cli, ["iteration", "create", "--project-id", "p1"])
    assert result.exit_code == 0
    assert "Creating iteration for project p1" in result.output

    result = runner.invoke(cli, ["iteration", "run", "--iteration-id", "i1"])
    assert result.exit_code == 0
    assert "Running iteration i1" in result.output


def test_cli_publish_command():
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "publish",
            "--iteration-id",
            "i1",
            "--repo",
            "owner/repo",
            "--token",
            "ghp_xxx",
        ],
    )
    assert result.exit_code == 0
    assert "Publishing iteration i1 to owner/repo" in result.output
