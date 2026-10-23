
import subprocess
import tempfile
from pathlib import Path


class PythonRunner:
    def __init__(self, python_path="python", timeout=5):
        self.python_path = python_path
        self.timeout = timeout

    def run(self, code, stdin=""):
        """Pythonコードを実行し、標準出力・標準エラーなどを返す。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            script_path = Path(temp_dir) / "main.py"
            script_path.write_text(code, encoding="utf-8")

            try:
                result = subprocess.run(
                    [self.python_path, "-X", "utf8", str(script_path)],
                    input=stdin,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=self.timeout,
                    cwd=temp_dir,
                    check=False,
                )

                return {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode,
                    "timed_out": False,
                }

            except subprocess.TimeoutExpired as error:
                stdout = error.stdout or ""
                stderr = error.stderr or ""

                if isinstance(stdout, bytes):
                    stdout = stdout.decode("utf-8", errors="replace")
                if isinstance(stderr, bytes):
                    stderr = stderr.decode("utf-8", errors="replace")

                return {
                    "stdout": stdout,
                    "stderr": stderr,
                    "returncode": None,
                    "timed_out": True,
                }

            except OSError as error:
                return {
                    "stdout": "",
                    "stderr": str(error),
                    "returncode": None,
                    "timed_out": False,
                }
