import subprocess


def test_cli_runs():
    # Run CLI with fake branch, ensure that exit code is 0
    result = subprocess.run(
        ["python", "src/cli.py", "--branch=feature/test-branch"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Review Summary" in result.stdout
