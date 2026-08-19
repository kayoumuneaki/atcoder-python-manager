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
            "Templates",
            "Snippets",
            "Settings",
        ])

        self.navigation.setFixedWidth(180)

        # メインエリア
        self.stack = QStackedWidget()

        dashboard = DashboardWidget()
        self.stack.addWidget(dashboard)

        for page_name in [
            "Templates",
            "Snippets",
            "Settings",
        ]:
            label = QLabel(page_name)
            label.setStyleSheet("font-size: 24px;")
            label.setAlignment(Qt.AlignCenter)

            page = QWidget()
            layout = QHBoxLayout(page)
            layout.addWidget(label)

            self.stack.addWidget(page)

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
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()