
import subprocess
import tempfile
import threading
from pathlib import Path


class PythonRunner:
    def __init__(self, python_path="python", timeout=5):
        self.python_path = python_path
        self.timeout = timeout

        # 実行中の子プロセス（stop() で強制終了するために保持する）
        self._process = None
        self._stopped = False
        self._lock = threading.Lock()

    def run(self, code, stdin=""):
        """Pythonコードを実行し、標準出力・標準エラーなどを返す。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            script_path = Path(temp_dir) / "main.py"
            script_path.write_text(code, encoding="utf-8")

            try:
                process = subprocess.Popen(
                    [self.python_path, "-X", "utf8", str(script_path)],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    cwd=temp_dir,
                )
            except OSError as error:
                return {
                    "stdout": "",
                    "stderr": str(error),
                    "returncode": None,
                    "timed_out": False,
                }

            with self._lock:
                self._process = process
                self._stopped = False

            try:
                stdout, stderr = process.communicate(
                    input=stdin,
                    timeout=self.timeout,
                )
                timed_out = False

            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                timed_out = True

            finally:
                with self._lock:
                    self._process = None
                    stopped = self._stopped

            return {
                "stdout": stdout or "",
                "stderr": stderr or "",
                "returncode": None if timed_out else process.returncode,
                "timed_out": timed_out,
                # stop() で止められた場合は True
                "stopped": stopped,
            }

    def stop(self):
        """実行中の子プロセスがあれば強制終了する（停止ボタン・アプリ終了時）。"""
        with self._lock:
            process = self._process
            if process is not None and process.poll() is None:
                self._stopped = True

        if process is not None and process.poll() is None:
            process.kill()
