import subprocess
import sys
from pathlib import Path


def test_hello_example_runs():
    repo = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "-m", "src.cli.vela_main", "run", "examples/basic/hello.vela"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Hello Vela" in result.stdout
