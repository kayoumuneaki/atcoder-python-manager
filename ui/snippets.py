
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.database import Database


class SnippetsWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.db = Database()
        self.current_snippet_id = None

        self.create_ui()
        self.load_snippets()

    def create_ui(self):
        title_label = QLabel("辞書登録")
        title_label.setStyleSheet(
            "font-size: 24px; font-weight: bold;"
        )

        self.snippet_list = QListWidget()
        self.snippet_list.currentItemChanged.connect(
            self.on_snippet_selected
        )

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText(
            "辞書名"
        )

        self.category_input = QComboBox()
        self.category_input.setEditable(True)
        self.category_input.addItems([
            "Graph",
            "DP",
            "Data Structure",
            "Math",
            "Search",
            "Other",
        ])
        self.category_input.setCurrentText("Other")

        self.code_editor = QTextEdit()
        self.code_editor.setFont(QFont("Consolas", 11))
        self.code_editor.setPlaceholderText(
            "ここに Python コードを書きます。"
        )

        form_layout = QFormLayout()
        form_layout.addRow("名前", self.title_input)
        form_layout.addRow("カテゴリ", self.category_input)

        self.new_button = QPushButton("新規")
        self.new_button.clicked.connect(self.new_snippet)

        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.save_snippet)

        self.delete_button = QPushButton("削除")
        self.delete_button.clicked.connect(self.delete_snippet)

        self.copy_button = QPushButton("コードをコピー")
        self.copy_button.clicked.connect(self.copy_code)

        self.reload_button = QPushButton("再読み込み")
        self.reload_button.clicked.connect(self.load_snippets)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.copy_button)
        button_layout.addWidget(self.reload_button)

        editor_layout = QVBoxLayout()
        editor_layout.addLayout(form_layout)
        editor_layout.addWidget(self.code_editor, 1)
        editor_layout.addLayout(button_layout)

        editor_widget = QWidget()
        editor_widget.setLayout(editor_layout)

        splitter = QSplitter()
        splitter.addWidget(self.snippet_list)
        splitter.addWidget(editor_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        layout = QVBoxLayout(self)
        layout.addWidget(title_label)
        layout.addWidget(splitter, 1)

    def load_snippets(self):
        self.snippet_list.blockSignals(True)
        self.snippet_list.clear()

        try:
            snippets = self.db.get_snippets()
        except Exception as error:
            self.snippet_list.blockSignals(False)
            QMessageBox.critical(
                self,
                "データベースエラー",
                f"辞書を読み込めませんでした：\n{error}",
            )
            return

        for snippet_id, title, category, code in snippets:
            item_text = f"{title} [{category or 'Other'}]"
            from PySide6.QtWidgets import QListWidgetItem

            item = QListWidgetItem(item_text)
            item.setData(256, snippet_id)
            self.snippet_list.addItem(item)

        self.snippet_list.blockSignals(False)
        self.clear_editor()

    def clear_editor(self):
        self.current_snippet_id = None
        self.title_input.clear()
        self.category_input.setCurrentText("Other")
        self.code_editor.clear()

    def new_snippet(self):
        self.snippet_list.blockSignals(True)
        self.snippet_list.clearSelection()
        self.snippet_list.setCurrentRow(-1)
        self.snippet_list.blockSignals(False)

        self.clear_editor()
        self.title_input.setFocus()

    def on_snippet_selected(self, current, previous):
        if current is None:
            return

        snippet_id = current.data(256)

        try:
            snippets = self.db.get_snippets()
        except Exception as error:
            QMessageBox.critical(
                self,
                "データベースエラー",
                f"辞書を読み込めませんでした：\n{error}",
            )
            return

        for row in snippets:
            if row[0] == snippet_id:
                self.current_snippet_id = row[0]
                self.title_input.setText(row[1])
                self.category_input.setCurrentText(
                    row[2] or "Other"
                )
                self.code_editor.setPlainText(row[3])
                return

    def save_snippet(self):
        title = self.title_input.text().strip()
        category = self.category_input.currentText().strip() or "Other"
        code = self.code_editor.toPlainText()

        if not title:
            QMessageBox.warning(
                self,
                "入力エラー",
                "辞書名を入力してください。",
            )
            return

        if not code.strip():
            QMessageBox.warning(
                self,
                "入力エラー",
                "コードを入力してください。",
            )
            return

        try:
            if self.current_snippet_id is None:
                self.current_snippet_id = self.db.add_snippet(
                    title, category, code
                )
            else:
                self.db.update_snippet(
                    self.current_snippet_id,
                    title,
                    category,
                    code,
                )
        except Exception as error:
            QMessageBox.critical(
                self,
                "データベースエラー",
                f"辞書を保存できませんでした：\n{error}",
            )
            return

        self.load_snippets()
        QMessageBox.information(
            self,
            "保存完了",
            "辞書を保存しました。",
        )

    def delete_snippet(self):
        if self.current_snippet_id is None:
            QMessageBox.warning(
                self,
                "選択エラー",
                "削除する辞書を選択してください。",
            )
            return

        answer = QMessageBox.question(
            self,
            "削除の確認",
            f"「{self.title_input.text()}」を削除しますか？",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            self.db.delete_snippet(self.current_snippet_id)
        except Exception as error:
            QMessageBox.critical(
                self,
                "データベースエラー",
                f"辞書を削除できませんでした：\n{error}",
            )
            return

        self.load_snippets()
        QMessageBox.information(
            self,
            "削除完了",
            "辞書を削除しました。",
        )

    def copy_code(self):
        code = self.code_editor.toPlainText()

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
