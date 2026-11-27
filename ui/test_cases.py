from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QListWidget,
    QPushButton,
    QLabel,
    QLineEdit,
    QTextEdit,
    QMessageBox,
)

from PySide6.QtCore import Qt

from core.database import Database


class TestCasesWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.db = Database()
        self.current_test_id = None

        self.init_ui()
        self.load_test_cases()

    def init_ui(self):
        layout = QVBoxLayout()

        # タイトル
        title = QLabel("テストケース")
        layout.addWidget(title)

        # 一覧
        self.test_case_list = QListWidget()
        self.test_case_list.currentItemChanged.connect(
            self.select_test_case
        )
        layout.addWidget(self.test_case_list)

        # 問題名
        layout.addWidget(QLabel("問題名"))

        self.problem_input = QLineEdit()
        layout.addWidget(self.problem_input)

        # 入力データ
        layout.addWidget(QLabel("入力"))

        self.input_editor = QTextEdit()
        layout.addWidget(self.input_editor)

        # 期待される出力
        layout.addWidget(QLabel("期待される出力"))

        self.output_editor = QTextEdit()
        layout.addWidget(self.output_editor)

        # 新規作成ボタン（選択を解除して入力欄を空にする）
        new_button = QPushButton("新規テストケース")
        new_button.clicked.connect(self.new_test_case)
        layout.addWidget(new_button)

        # 保存ボタン（未選択なら新規追加、選択中なら更新）
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.save_test_case)
        layout.addWidget(save_button)

        # 削除ボタン
        delete_button = QPushButton("テストケースを削除")
        delete_button.clicked.connect(self.delete_test_case)
        layout.addWidget(delete_button)

        # 再読み込みボタン
        reload_button = QPushButton("一覧を再読み込み")
        reload_button.clicked.connect(self.load_test_cases)
        layout.addWidget(reload_button)

        self.setLayout(layout)

    def load_test_cases(self):
        self.test_case_list.clear()
        self.current_test_id = None

        self.problem_input.clear()
        self.input_editor.clear()
        self.output_editor.clear()

        test_cases = self.db.get_test_cases()

        for test_case in test_cases:
            test_id, problem, input_data, expected_output = test_case

            item_text = f"ID: {test_id} | {problem}"
            self.test_case_list.addItem(item_text)

            item = self.test_case_list.item(
                self.test_case_list.count() - 1
            )

            item.setData(
                Qt.ItemDataRole.UserRole,
                test_id
            )

    def select_test_case(self, current, previous):
        if current is None:
            self.current_test_id = None
            return

        test_id = current.data(Qt.ItemDataRole.UserRole)

        test_cases = self.db.get_test_cases()

        for test_case in test_cases:
            if test_case[0] == test_id:
                _, problem, input_data, expected_output = test_case

                self.current_test_id = test_id

                self.problem_input.setText(problem)
                self.input_editor.setPlainText(input_data or "")
                self.output_editor.setPlainText(
                    expected_output or ""
                )
                break

    def new_test_case(self):
        self.test_case_list.blockSignals(True)
        self.test_case_list.clearSelection()
        self.test_case_list.setCurrentRow(-1)
        self.test_case_list.blockSignals(False)

        self.current_test_id = None
        self.problem_input.clear()
        self.input_editor.clear()
        self.output_editor.clear()
        self.problem_input.setFocus()

    def save_test_case(self):
        problem = self.problem_input.text().strip()
        input_data = self.input_editor.toPlainText()
        expected_output = self.output_editor.toPlainText()

        if not problem:
            QMessageBox.warning(
                self,
                "確認",
                "問題名を入力してください。"
            )
            return

        try:
            if self.current_test_id is None:
                self.db.add_test_case(
                    problem,
                    input_data,
                    expected_output
                )
                message = "テストケースを追加しました。"
            else:
                self.db.update_test_case(
                    self.current_test_id,
                    problem,
                    input_data,
                    expected_output
                )
                message = "テストケースを更新しました。"
        except Exception as error:
            QMessageBox.critical(
                self,
                "データベースエラー",
                f"テストケースを保存できませんでした：\n{error}"
            )
            return

        QMessageBox.information(
            self,
            "保存完了",
            message
        )

        self.load_test_cases()


    def delete_test_case(self):
        if self.current_test_id is None:
            QMessageBox.warning(
                self,
                "確認",
                "テストケースを選択してください。"
            )
            return

        reply = QMessageBox.question(
            self,
            "削除の確認",
            "このテストケースを削除しますか？",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_test_case(self.current_test_id)

            QMessageBox.information(
                self,
                "削除完了",
                "テストケースを削除しました。"
            )

            self.load_test_cases()