"""Cover the module entry point by invoking CLI directly."""

from click.testing import CliRunner

from stfwb_cli.main import cli


def test_cli_module_entrypoint_help():
    """Test CLI --help output."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "STF-WB" in result.output


def test_cli_main_invocation():
    """Test __main__.py by importing and executing it."""
    # Import the __main__ module to ensure it's covered
    import stfwb_cli.__main__  # noqa: F401
