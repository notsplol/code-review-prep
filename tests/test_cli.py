import subprocess

def test_cli_runs():
    # Run CLI with fake branch, ensure exit code 0
    result = subprocess.run(
        ["python", "src/cli.py", "--branch=feature/test-branch"],
        capture_output=True,
        text=True
    )
    # CLI should not crash
    assert result.returncode == 0
    assert "Review Summary" in result.stdout
