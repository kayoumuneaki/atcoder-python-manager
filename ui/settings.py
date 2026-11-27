from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.config import Config


class SettingsWidget(QWidget):
    # 設定保存後に発行。各画面はこれを受けて設定を読み直す
    settings_saved = Signal()

    def __init__(self):
        super().__init__()

        self.config = Config()

        self.username_input = QLineEdit()
        self.python_path_input = QLineEdit()
        self.working_folder_input = QLineEdit()

        self.create_ui()
        self.load_settings()

    def create_ui(self):
        form_layout = QFormLayout()

        form_layout.addRow(
            "AtCoder ユーザー名",
            self.username_input
        )

        form_layout.addRow(
            "Python のパス",
            self.python_path_input
        )

        folder_layout = QHBoxLayout()

        folder_layout.addWidget(
            self.working_folder_input
        )

        browse_button = QPushButton("参照")
        browse_button.clicked.connect(
            self.select_working_folder
        )

        folder_layout.addWidget(browse_button)

        form_layout.addRow(
            "作業フォルダ",
            folder_layout
        )

        save_button = QPushButton("保存")
        save_button.clicked.connect(
            self.save_settings
        )

        layout = QVBoxLayout(self)

        layout.addLayout(form_layout)
        layout.addWidget(save_button)
        layout.addStretch()

    def select_working_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "作業フォルダを選択"
        )

        if folder:
            self.working_folder_input.setText(folder)

    def save_settings(self):
        settings = {
            "atcoder_username": self.username_input.text(),
            "python_path": self.python_path_input.text(),
            "working_folder": self.working_folder_input.text(),
        }

        self.config.save(settings)
        self.settings_saved.emit()

        QMessageBox.information(
            self,
            "設定",
            "設定を保存しました。"
        )

    def load_settings(self):
        settings = self.config.load()

        self.username_input.setText(
            settings.get("atcoder_username", "")
        )

        self.python_path_input.setText(
            settings.get("python_path", "")
        )

        self.working_folder_input.setText(
            settings.get("working_folder", "")
        )