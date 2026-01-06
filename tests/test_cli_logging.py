"""Tests for CLI logging verbosity flags and file output."""

from pathlib import Path

from click.testing import CliRunner

from stfwb_cli.main import cli


def test_verbose_logging_project_create(tmp_path: Path, caplog) -> None:
    runner = CliRunner()
    res = runner.invoke(
        cli,
        [
            "-vv",
            "project",
            "create",
            "--name",
            "loggy",
            "--target-uri",
            "https://example.org/t",
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert res.exit_code == 0
    # Validate logs via caplog
    joined = "\n".join(record.message for record in caplog.records)
    assert "Saving project" in joined
    assert "Writing JSON" in joined


def test_quiet_logging_iteration_create(tmp_path: Path, caplog) -> None:
    runner = CliRunner()
    res = runner.invoke(
        cli,
        [
            "--quiet",
            "iteration",
            "create",
            "--project-id",
            "p1",
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert res.exit_code == 0
    # In quiet mode, caplog should not capture INFO from our loggers
    assert not any(r.levelname == "INFO" and r.name.startswith("stfwb.") for r in caplog.records)


def test_single_v_info_level(tmp_path: Path, caplog) -> None:
    runner = CliRunner()
    res = runner.invoke(
        cli,
        [
            "-v",
            "project",
            "create",
            "--name",
            "once",
            "--target-uri",
            "https://example.org/t",
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert res.exit_code == 0
    # With -v, info logs should be present
    assert any(r.levelname == "INFO" and r.name == "stfwb.storage" for r in caplog.records)


def test_log_file_output(tmp_path: Path) -> None:
    log_file = tmp_path / "test.log"
    runner = CliRunner()
    res = runner.invoke(
        cli,
        [
            "-vv",
            "--log-file",
            str(log_file),
            "project",
            "create",
            "--name",
            "filetest",
            "--target-uri",
            "https://example.org/t",
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert res.exit_code == 0
    assert log_file.exists()
    content = log_file.read_text()
    assert "INFO stfwb.storage" in content
    assert "DEBUG stfwb.storage" in content


def test_command_override_quiet_with_verbose(tmp_path: Path, caplog) -> None:
    runner = CliRunner()
    res = runner.invoke(
        cli,
        [
            "--quiet",
            "project",
            "create",
            "-vv",
            "--name",
            "override",
            "--target-uri",
            "https://example.org/t",
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert res.exit_code == 0
    # Command-level -vv should override global --quiet
    assert any(r.levelname == "DEBUG" and r.name.startswith("stfwb.") for r in caplog.records)


def test_command_override_verbose_with_quiet(tmp_path: Path, caplog) -> None:
    runner = CliRunner()
    res = runner.invoke(
        cli,
        [
            "-vv",
            "iteration",
            "create",
            "--quiet",
            "--project-id",
            "p1",
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert res.exit_code == 0
    # Command-level --quiet should override global -vv
    assert not any(r.levelname == "INFO" and r.name.startswith("stfwb.") for r in caplog.records)


def test_command_single_v_info(tmp_path: Path, caplog) -> None:
    runner = CliRunner()
    res = runner.invoke(
        cli,
        [
            "--quiet",
            "project",
            "create",
            "-v",
            "--name",
            "info",
            "--target-uri",
            "https://example.org/t",
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert res.exit_code == 0
    # Command-level -v (single) should override global --quiet
    assert any(r.levelname == "INFO" and r.name == "stfwb.storage" for r in caplog.records)
