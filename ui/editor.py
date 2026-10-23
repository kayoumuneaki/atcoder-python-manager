
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.config import Config
from core.runner import PythonRunner


class EditorWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.config = Config()
        self.runner = PythonRunner()

        self.create_ui()
        self.load_settings()

    def create_ui(self):
        title_label = QLabel("Python Editor")
        title_label.setStyleSheet(
            "font-size: 24px; font-weight: bold;"
        )

        code_label = QLabel("Code")

        self.code_editor = QTextEdit()
        self.code_editor.setFont(QFont("Consolas", 11))
        self.code_editor.setPlaceholderText(
            "Write your Python code here."
        )

        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.run_code)

        output_label = QLabel("Output")

        self.output_view = QTextEdit()
        self.output_view.setReadOnly(True)
        self.output_view.setFont(QFont("Consolas", 11))

        layout = QVBoxLayout(self)
        layout.addWidget(title_label)
        layout.addWidget(code_label)
        layout.addWidget(self.code_editor, 3)
        layout.addWidget(self.run_button)
        layout.addWidget(output_label)
        layout.addWidget(self.output_view, 2)

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

        if not code.strip():
            self.output_view.setPlainText(
                "Please enter Python code."
            )
            return

        self.run_button.setEnabled(False)
        self.run_button.setText("Running...")

        try:
            result = self.runner.run(code)

            output = result["stdout"]

            if result["stderr"]:
                if output and not output.endswith("\n"):
                    output += "\n"
                output += result["stderr"]

            if result["timed_out"]:
                output += (
                    "\nExecution timed out "
                    "(limit: 5 seconds)."
                )
            elif (
                result["returncode"] not in (0, None)
                and not result["stderr"]
            ):
                output += (
                    f"\nPython exited with code "
                    f"{result['returncode']}."
                )

            self.output_view.setPlainText(output)

        except Exception as error:
            self.output_view.setPlainText(
                f"Execution error:\n{error}"
            )

        finally:
            self.run_button.setEnabled(True)
            self.run_button.setText("Run")
