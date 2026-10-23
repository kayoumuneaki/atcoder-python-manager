import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QListWidget,
    QStackedWidget,
    QHBoxLayout,
    QWidget,
)
from ui.dashboard import DashboardWidget
from ui.settings import SettingsWidget
from core.database import Database
from ui.template import TemplateWidget
from ui.snippets import SnippetsWidget
from ui.runner import RunnerWidget
from ui.editor import EditorWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AtCoder Python Manager")
        self.resize(1000, 700)

        self.create_menu()
        self.create_ui()

    def create_menu(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        file_menu.addAction("Exit")

        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction("About")

    def create_ui(self):
        # 左側ナビゲーション
        self.navigation = QListWidget()
        self.navigation.addItems([
            "Dashboard",
            "Runner",
            "Editor",
            "Templates",
            "Snippets",
            "Settings",
        ])

        self.navigation.setFixedWidth(180)

        # メインエリア
        self.stack = QStackedWidget()

        # Dashboard
        dashboard = DashboardWidget()
        self.stack.addWidget(dashboard)

        # Runner
        runner_widget = RunnerWidget()
        self.stack.addWidget(runner_widget)

        # Editor
        editor_widget = EditorWidget()
        self.stack.addWidget(editor_widget)

        # Templates
        template_widget = TemplateWidget()
        self.stack.addWidget(template_widget)

        # Snippets
        snippets_widget = SnippetsWidget()
        self.stack.addWidget(snippets_widget)

        # Settings
        settings = SettingsWidget()
        self.stack.addWidget(settings)

        # 左側とメインエリアを配置
        central_widget = QWidget()
        layout = QHBoxLayout(central_widget)

        layout.addWidget(self.navigation)
        layout.addWidget(self.stack)

        self.setCentralWidget(central_widget)

        # ナビゲーションとメインエリアを連動
        self.navigation.currentRowChanged.connect(
            self.stack.setCurrentIndex
        )


def main():
    db = Database()
    db.initialize()

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()