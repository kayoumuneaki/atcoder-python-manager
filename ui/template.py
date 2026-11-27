
from pathlib import Path

from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QInputDialog,
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
        title_label = QLabel("Python テンプレート")
        title_label.setStyleSheet(
            "font-size: 24px; font-weight: bold;"
        )

        self.template_list = QListWidget()
        self.template_list.currentItemChanged.connect(
            self.on_template_selected
        )

        self.editor = QTextEdit()
        self.editor.setPlaceholderText(
            "編集するテンプレートを選んでください。"
        )
        self.editor.setFontFamily("Consolas")
        self.editor.setFontPointSize(11)

        self.save_button = QPushButton("保存")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_template)

        self.reload_button = QPushButton("一覧を再読み込み")
        self.reload_button.clicked.connect(
            self.load_template_list
        )

        self.new_button = QPushButton("新規")
        self.new_button.clicked.connect(self.new_template)

        self.copy_button = QPushButton("コードをコピー")
        self.copy_button.clicked.connect(self.copy_template)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.copy_button)
        button_layout.addWidget(self.reload_button)

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
                "読み込みエラー",
                f"テンプレートを読み込めませんでした：\n{error}",
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
            "保存の確認",
            f"{self.current_file.name} を上書きしますか？",
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
                "保存エラー",
                f"テンプレートを保存できませんでした：\n{error}",
            )
            return

        QMessageBox.information(
            self,
            "保存完了",
            f"{self.current_file.name} を保存しました。",
        )

    def new_template(self):
        name, accepted = QInputDialog.getText(
            self,
            "新しいテンプレート",
            "ファイル名（例：dijkstra.py）：",
        )

        if not accepted:
            return

        name = name.strip()
        if not name:
            return

        if not name.endswith(".py"):
            name += ".py"

        # フォルダ区切りや Windows で使えない文字を含む名前は受け付けない
        invalid_chars = set('\\/:*?"<>|')
        if (
            any(char in invalid_chars or ord(char) < 32 for char in name)
            or name == ".py"
        ):
            QMessageBox.warning(
                self,
                "使えない名前",
                'ファイル名に \\ / : * ? " < > | は使えません。',
            )
            return

        file_path = self.template_dir / name

        if file_path.exists():
            QMessageBox.warning(
                self,
                "作成できません",
                f"{name} は既に存在します。",
            )
            return

        try:
            self.template_dir.mkdir(parents=True, exist_ok=True)
            file_path.write_text("", encoding="utf-8")
        except OSError as error:
            QMessageBox.critical(
                self,
                "作成エラー",
                f"テンプレートを作成できませんでした：\n{error}",
            )
            return

        self.load_template_list()

        # 作成したテンプレートを選択して、すぐ編集できるようにする
        matches = self.template_list.findItems(
            name,
            Qt.MatchFlag.MatchExactly,
        )
        if matches:
            self.template_list.setCurrentItem(matches[0])
        self.editor.setFocus()

    def copy_template(self):
        code = self.editor.toPlainText()

        if not code.strip():
            QMessageBox.warning(
                self,
                "コピーエラー",
                "コピーするコードがありません。",
            )
            return

        QApplication.clipboard().setText(code)

        QMessageBox.information(
            self,
            "コピー完了",
            "コードをクリップボードにコピーしました。",
        )
