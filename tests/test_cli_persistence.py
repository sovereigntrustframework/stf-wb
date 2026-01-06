"""CLI persistence tests with Click's isolated filesystem."""

from pathlib import Path

from click.testing import CliRunner

from stfwb_cli.main import cli


def test_cli_project_and_iteration_persist() -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        store = Path(".stfwb")

        res = runner.invoke(
            cli,
            [
                "project",
                "create",
                "--name",
                "demo",
                "--target-uri",
                "https://example.org/spec",
                "--store-dir",
                str(store),
            ],
        )
        assert res.exit_code == 0, res.output
        assert store.exists()
        # Extract id from output
        assert "id=" in res.output

        res2 = runner.invoke(
            cli,
            [
                "iteration",
                "create",
                "--project-id",
                "demo-proj",
                "--store-dir",
                str(store),
            ],
        )
        assert res2.exit_code == 0, res2.output
        assert (store / "iterations").exists()
