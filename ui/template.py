
from pathlib import Path

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class TemplateWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.template_dir = (
            Path(__file__).resolve().parent.parent / "templates"
        )
        self.current_file = None

        self.create_ui()
        self.load_template_list()

    def create_ui(self):
        title_label = QLabel("Python Templates")
        title_label.setStyleSheet(
            "font-size: 24px; font-weight: bold;"
        )

        self.template_list = QListWidget()
        self.template_list.currentItemChanged.connect(
            self.on_template_selected
        )

        self.editor = QTextEdit()
        self.editor.setPlaceholderText(
            "Select a template to edit."
        )
        self.editor.setFontFamily("Consolas")
        self.editor.setFontPointSize(11)

        self.save_button = QPushButton("Save")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_template)

        self.reload_button = QPushButton("Reload List")
        self.reload_button.clicked.connect(
            self.load_template_list
        )

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.reload_button)
        button_layout.addWidget(self.save_button)

        splitter = QSplitter()
        splitter.addWidget(self.template_list)
        splitter.addWidget(self.editor)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        layout = QVBoxLayout(self)
        layout.addWidget(title_label)
        layout.addWidget(splitter, 1)
        layout.addLayout(button_layout)

    def load_template_list(self):
        self.template_list.blockSignals(True)
        self.template_list.clear()

        self.template_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        files = sorted(
            self.template_dir.glob("*.py"),
            key=lambda path: path.name.lower(),
        )

        for file_path in files:
            self.template_list.addItem(file_path.name)

        self.template_list.blockSignals(False)

        self.current_file = None
        self.editor.clear()
        self.save_button.setEnabled(False)

    def on_template_selected(self, current, previous):
        if current is None:
            return

        file_path = self.template_dir / current.text()

        try:
            content = file_path.read_text(encoding="utf-8")
        except OSError as error:
            QMessageBox.warning(
                self,
                "Load Error",
                f"Failed to load template:\n{error}",
            )
            return

        self.current_file = file_path
        self.editor.setPlainText(content)
        self.save_button.setEnabled(True)

    def save_template(self):
        if self.current_file is None:
            return

        answer = QMessageBox.question(
            self,
            "Confirm Save",
            f"Overwrite {self.current_file.name}?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            self.current_file.write_text(
                self.editor.toPlainText(),
                encoding="utf-8",
            )
        except OSError as error:
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save template:\n{error}",
            )
            return

        QMessageBox.information(
            self,
            "Saved",
            f"{self.current_file.name} was saved successfully.",
        )
