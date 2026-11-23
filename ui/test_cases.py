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
        title = QLabel("Test Cases")
        layout.addWidget(title)

        # 一覧
        self.test_case_list = QListWidget()
        self.test_case_list.currentItemChanged.connect(
            self.select_test_case
        )
        layout.addWidget(self.test_case_list)

        # 問題名
        layout.addWidget(QLabel("Problem"))

        self.problem_input = QLineEdit()
        layout.addWidget(self.problem_input)

        # 入力データ
        layout.addWidget(QLabel("Input"))

        self.input_editor = QTextEdit()
        layout.addWidget(self.input_editor)

        # 期待される出力
        layout.addWidget(QLabel("Expected Output"))

        self.output_editor = QTextEdit()
        layout.addWidget(self.output_editor)

        # 保存ボタン
        save_button = QPushButton("Save Changes")
        save_button.clicked.connect(self.save_test_case)
        layout.addWidget(save_button)

        # 削除ボタン
        delete_button = QPushButton("Delete Test Case")
        delete_button.clicked.connect(self.delete_test_case)
        layout.addWidget(delete_button)

        # 再読み込みボタン
        reload_button = QPushButton("Reload List")
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

    def save_test_case(self):
        if self.current_test_id is None:
            QMessageBox.warning(
                self,
                "Warning",
                "Please select a test case."
            )
            return

        problem = self.problem_input.text()
        input_data = self.input_editor.toPlainText()
        expected_output = self.output_editor.toPlainText()

        self.db.update_test_case(
            self.current_test_id,
            problem,
            input_data,
            expected_output
        )

        QMessageBox.information(
            self,
            "Saved",
            "Test case updated successfully."
        )

        self.load_test_cases()
        
    def delete_test_case(self):
        if self.current_test_id is None:
            QMessageBox.warning(
                self,
                "Warning",
                "Please select a test case."
            )
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this test case?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_test_case(self.current_test_id)

            QMessageBox.information(
                self,
                "Deleted",
                "Test case deleted successfully."
            )

            self.load_test_cases()