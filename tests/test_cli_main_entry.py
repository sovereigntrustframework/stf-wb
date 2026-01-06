"""Cover the module entry point by invoking `python -m stfwb_cli.main`."""

import subprocess
import sys


def test_cli_module_entrypoint_help():
    # Run the module as a script with --help to avoid interactive prompts
    res = subprocess.run(
        [sys.executable, "-m", "stfwb_cli.main", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0
    assert "STF-WB" in res.stdout
