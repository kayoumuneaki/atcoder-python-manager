
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QLabel,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.runner import PythonRunner
from core.config import Config


class RunnerWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.config = Config()
        self.runner = PythonRunner()

        self.create_ui()
        self.load_settings()

    def create_ui(self):
        title_label = QLabel("Python Runner")
        title_label.setStyleSheet(
            "font-size: 24px; font-weight: bold;"
        )

        code_label = QLabel("Python Code")
        self.code_editor = QTextEdit()
        self.code_editor.setFont(QFont("Consolas", 11))
        self.code_editor.setPlaceholderText(
            "Write your Python code here."
        )

        stdin_label = QLabel("Standard Input")
        self.stdin_editor = QTextEdit()
        self.stdin_editor.setFont(QFont("Consolas", 11))
        self.stdin_editor.setPlaceholderText(
            "Enter standard input here."
        )

        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        input_layout.addWidget(code_label)
        input_layout.addWidget(self.code_editor, 3)
        input_layout.addWidget(stdin_label)
        input_layout.addWidget(self.stdin_editor, 1)

        self.run_button = QPushButton("Run Python")
        self.run_button.clicked.connect(self.run_code)

        stdout_label = QLabel("Standard Output")
        self.stdout_view = QTextEdit()
        self.stdout_view.setReadOnly(True)
        self.stdout_view.setFont(QFont("Consolas", 11))

        stderr_label = QLabel("Error / Standard Error")
        self.stderr_view = QTextEdit()
        self.stderr_view.setReadOnly(True)
        self.stderr_view.setFont(QFont("Consolas", 10))

        output_widget = QWidget()
        output_layout = QVBoxLayout(output_widget)
        output_layout.addWidget(stdout_label)
        output_layout.addWidget(self.stdout_view, 2)
        output_layout.addWidget(stderr_label)
        output_layout.addWidget(self.stderr_view, 1)

        splitter = QSplitter()
        splitter.addWidget(input_widget)
        splitter.addWidget(output_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        layout = QVBoxLayout(self)
        layout.addWidget(title_label)
        layout.addWidget(splitter, 1)
        layout.addWidget(self.run_button)

    def load_settings(self):
        settings = self.config.load()
        python_path = settings.get("python_path", "python")

        if not isinstance(python_path, str) or not python_path.strip():
            python_path = "python"

        self.runner = PythonRunner(
            python_path=python_path,
            timeout=5,
        )

    def run_code(self):
        code = self.code_editor.toPlainText()
        stdin = self.stdin_editor.toPlainText()

        if not code.strip():
            QMessageBox.warning(
                self,
                "Input Error",
                "Please enter Python code.",
            )
            return

        self.run_button.setEnabled(False)
        self.run_button.setText("Running...")

        try:
            result = self.runner.run(code, stdin)
        except Exception as error:
            QMessageBox.critical(
                self,
                "Execution Error",
                str(error),
            )
            return
        finally:
            self.run_button.setEnabled(True)
            self.run_button.setText("Run Python")

        self.stdout_view.setPlainText(result["stdout"])

        stderr = result["stderr"]

        if result["timed_out"]:
            stderr = (
                "Execution timed out (limit: 5 seconds).\n"
                + stderr
            )
        elif result["returncode"] != 0 and not stderr:
            stderr = (
                f"Python exited with code "
                f"{result['returncode']}."
            )

        self.stderr_view.setPlainText(stderr)
