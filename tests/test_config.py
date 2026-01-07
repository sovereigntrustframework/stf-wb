"""Tests for config file and environment variable support."""

from pathlib import Path

from click.testing import CliRunner

from stfwb.utils.config import Config
from stfwb_cli.main import cli


def test_config_defaults() -> None:
    """Test that config has sensible defaults."""
    cfg = Config()
    assert cfg.store_dir is None
    assert cfg.log_file is None
    assert cfg.github_token is None
    assert cfg.github_repo is None
    assert cfg.verbose == 0
    assert cfg.quiet is False


def test_env_var_store_dir(monkeypatch) -> None:
    """Test STFWB_STORE_DIR env var override."""
    monkeypatch.setenv("STFWB_STORE_DIR", "/tmp/custom")
    cfg = Config()
    assert cfg.store_dir == "/tmp/custom"


def test_env_var_log_file(monkeypatch) -> None:
    """Test STFWB_LOG_FILE env var override."""
    monkeypatch.setenv("STFWB_LOG_FILE", "/tmp/app.log")
    cfg = Config()
    assert cfg.log_file == "/tmp/app.log"


def test_env_var_verbose(monkeypatch) -> None:
    """Test STFWB_VERBOSE env var override."""
    monkeypatch.setenv("STFWB_VERBOSE", "2")
    cfg = Config()
    assert cfg.verbose == 2


def test_env_var_quiet_true(monkeypatch) -> None:
    """Test STFWB_QUIET=true env var override."""
    monkeypatch.setenv("STFWB_QUIET", "true")
    cfg = Config()
    assert cfg.quiet is True


def test_env_var_quiet_false(monkeypatch) -> None:
    """Test STFWB_QUIET=false env var is not set."""
    monkeypatch.delenv("STFWB_QUIET", raising=False)
    cfg = Config()
    assert cfg.quiet is False


def test_env_var_github_token(monkeypatch) -> None:
    """Test STFWB_GITHUB_TOKEN env var override."""
    monkeypatch.setenv("STFWB_GITHUB_TOKEN", "ghp_token")
    cfg = Config()
    assert cfg.github_token == "ghp_token"


def test_env_var_github_repo(monkeypatch) -> None:
    """Test STFWB_GITHUB_REPO env var override."""
    monkeypatch.setenv("STFWB_GITHUB_REPO", "owner/repo")
    cfg = Config()
    assert cfg.github_repo == "owner/repo"


def test_cli_uses_config_defaults(tmp_path: Path, monkeypatch) -> None:
    """Test that CLI uses config store-dir when not provided."""
    custom_store = tmp_path / "custom_store"
    # Reset the singleton to force reload from env
    import stfwb.utils.config as cfg_module

    monkeypatch.setenv("STFWB_STORE_DIR", str(custom_store))
    cfg_module._instance = None  # Force reload

    runner = CliRunner()
    res = runner.invoke(
        cli,
        [
            "project",
            "create",
            "--name",
            "cfg",
            "--target-uri",
            "https://example.org/t",
        ],
    )
    assert res.exit_code == 0
    # Project should be saved to env-configured store
    assert custom_store.exists()
    assert any(f.suffix == ".json" for f in custom_store.glob("projects/*"))


def test_cli_flag_overrides_env(tmp_path: Path, monkeypatch) -> None:
    """Test that CLI --store-dir overrides env var."""
    import stfwb.utils.config as cfg_module

    env_store = tmp_path / "env_store"
    cli_store = tmp_path / "cli_store"
    monkeypatch.setenv("STFWB_STORE_DIR", str(env_store))
    cfg_module._instance = None  # Force reload

    runner = CliRunner()
    res = runner.invoke(
        cli,
        [
            "project",
            "create",
            "--name",
            "override",
            "--target-uri",
            "https://example.org/t",
            "--store-dir",
            str(cli_store),
        ],
    )
    assert res.exit_code == 0
    # Project should be saved to CLI-provided store, not env-configured
    assert cli_store.exists()
    assert any(f.suffix == ".json" for f in cli_store.glob("projects/*"))


def test_config_load_yaml_not_found() -> None:
    """Test config with nonexistent yaml file."""
    cfg = Config()
    result = cfg._load_yaml(Path("/nonexistent/stfwb.yaml"))
    assert result == {}


def test_config_load_yaml_invalid(tmp_path: Path) -> None:
    """Test config with invalid yaml file."""
    bad_yaml = tmp_path / "bad.yaml"
    bad_yaml.write_text("{bad yaml content:")
    cfg = Config()
    result = cfg._load_yaml(bad_yaml)
    assert result == {}


def test_config_load_yaml_non_dict(tmp_path: Path) -> None:
    """Test config with yaml that doesn't parse to dict."""
    list_yaml = tmp_path / "list.yaml"
    list_yaml.write_text("- item1\n- item2")
    cfg = Config()
    result = cfg._load_yaml(list_yaml)
    assert result == {}


def test_config_from_yaml_home(tmp_path: Path, monkeypatch) -> None:
    """Test loading config from ~/.stfwb/stfwb.yaml."""
    home_stfwb_dir = tmp_path / ".stfwb"
    home_stfwb_dir.mkdir()
    yaml_file = home_stfwb_dir / "stfwb.yaml"
    yaml_file.write_text(
        "store_dir: /tmp/custom\nverbose: 1\nquiet: false\ngithub_token: ghp_yml\ngithub_repo: owner/repo\n"
    )

    # Patch home() to use tmp_path
    import stfwb.utils.config as cfg_module

    original_home = cfg_module.Path.home

    def mock_home():
        return tmp_path

    cfg_module.Path.home = mock_home  # type: ignore[method-assign]
    try:
        cfg_module._instance = None
        cfg = cfg_module.get_config()
        assert cfg.store_dir == "/tmp/custom"
        assert cfg.github_token == "ghp_yml"
        assert cfg.github_repo == "owner/repo"
        assert cfg.verbose == 1
        assert cfg.quiet is False
    finally:
        cfg_module.Path.home = original_home  # type: ignore[method-assign]


def test_config_from_current_dir(tmp_path: Path, monkeypatch) -> None:
    """Test loading config from ./stfwb.yaml in current directory."""
    yaml_file = tmp_path / "stfwb.yaml"
    yaml_file.write_text("store_dir: /tmp/local\nlog_file: /tmp/app.log\nquiet: true\n")

    monkeypatch.chdir(tmp_path)
    import stfwb.utils.config as cfg_module

    cfg_module._instance = None
    cfg = cfg_module.get_config()
    assert cfg.store_dir == "/tmp/local"
    assert cfg.log_file == "/tmp/app.log"
    assert cfg.quiet is True


def test_project_create_without_config_in_ctx(tmp_path: Path) -> None:
    """Test project create when ctx.obj is not set (edge case)."""
    runner = CliRunner()
    # This tests the fallback when ctx.obj is None or missing "config"
    res = runner.invoke(
        cli,
        [
            "project",
            "create",
            "--name",
            "noconfig",
            "--target-uri",
            "https://example.org/t",
            "--store-dir",
            str(tmp_path),
        ],
    )
    assert res.exit_code == 0
    assert tmp_path.exists()


def test_iteration_create_without_store_dir(tmp_path: Path, monkeypatch) -> None:
    """Test iteration create without --store-dir uses DEFAULT."""
    runner = CliRunner()
    # No --store-dir provided; should use DEFAULT_STORE_DIR
    res = runner.invoke(
        cli,
        [
            "iteration",
            "create",
            "--project-id",
            "p1",
        ],
    )
    assert res.exit_code == 0
    # Verify it went to default location
    from pathlib import Path as P

    from stfwb.utils.storage import DEFAULT_STORE_DIR

    default_path = P(DEFAULT_STORE_DIR) / "iterations"
    assert any(f.suffix == ".json" for f in default_path.glob("*") if default_path.exists())
