"""Additional CLI filter tests covering empty results for text and JSON."""

import json
from pathlib import Path

from click.testing import CliRunner

from stfwb_cli.main import cli


def test_project_list_filter_empty(tmp_path: Path) -> None:
    runner = CliRunner()
    # No projects created; filter should still show empty message
    res = runner.invoke(
        cli,
        ["project", "list", "--name-contains", "zzz", "--store-dir", str(tmp_path)],
    )
    assert res.exit_code == 0
    assert f"No projects found in {tmp_path}" in res.output

    # JSON with filter should be []
    res_json = runner.invoke(
        cli,
        ["project", "list", "--json", "--name-contains", "zzz", "--store-dir", str(tmp_path)],
    )
    assert res_json.exit_code == 0
    data = json.loads(res_json.output)
    assert data == []


def test_iteration_list_filter_empty(tmp_path: Path) -> None:
    runner = CliRunner()
    # No iterations; filter should still show empty message
    res = runner.invoke(
        cli,
        ["iteration", "list", "--state", "created", "--store-dir", str(tmp_path)],
    )
    assert res.exit_code == 0
    assert f"No iterations found in {tmp_path}" in res.output

    # JSON with project-id filter should be []
    res_json = runner.invoke(
        cli,
        ["iteration", "list", "--json", "--project-id", "pX", "--store-dir", str(tmp_path)],
    )
    assert res_json.exit_code == 0
    data = json.loads(res_json.output)
    assert data == []
