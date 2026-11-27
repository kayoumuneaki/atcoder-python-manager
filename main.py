import sys

import PySide6
from PySide6.QtCore import QLibraryInfo, Qt, QTranslator
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMessageBox,
    QListWidget,
    QStackedWidget,
    QHBoxLayout,
    QWidget,
    QStyle,
)
from ui.dashboard import DashboardWidget
from ui.settings import SettingsWidget
from core.database import Database
from ui.template import TemplateWidget
from ui.snippets import SnippetsWidget
from ui.runner import RunnerWidget
from ui.editor import EditorWidget
from ui.test_cases import TestCasesWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AtCoder Python Manager")
        self.resize(1000, 700)

        self.create_menu()
        self.create_ui()

    def create_menu(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("ファイル")
        exit_action = file_menu.addAction("終了")
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        # close() を使うと、実行中コードの停止など終了時の後片付けも通る
        exit_action.triggered.connect(self.close)

        help_menu = menu_bar.addMenu("ヘルプ")
        about_action = help_menu.addAction("このアプリについて")
        about_action.triggered.connect(self.show_about)

    def show_about(self):
        QMessageBox.about(
            self,
            "AtCoder Python Manager について",
            "<b>AtCoder Python Manager</b><br>"
            "Prototype v0.1<br><br>"
            "Pythonで競技プログラミングをするための管理・支援アプリ。<br><br>"
            "Python {} / PySide6 {}".format(
                sys.version.split()[0], PySide6.__version__
            ),
        )

    def create_ui(self):
        # 左側ナビゲーション
        self.navigation = QListWidget()

        items = [
            "ダッシュボード",
            "実行",
            "エディタ",
            "テンプレート",
            "辞書登録",
            "テストケース",
            "設定"
        ]

        self.navigation.addItems(items)
        self.navigation.setFixedWidth(200)

        # アイコン
        style = QApplication.style()

        icons = [
            QStyle.StandardPixmap.SP_ComputerIcon,
            QStyle.StandardPixmap.SP_MediaPlay,
            QStyle.StandardPixmap.SP_FileIcon,
            QStyle.StandardPixmap.SP_DirIcon,
            QStyle.StandardPixmap.SP_FileDialogDetailedView,
            QStyle.StandardPixmap.SP_FileDialogListView,
            QStyle.StandardPixmap.SP_DesktopIcon,
        ]

        for i, icon in enumerate(icons):
            self.navigation.item(i).setIcon(
                style.standardIcon(icon)
            )

        # ナビゲーションの見た目
        self.navigation.setStyleSheet("""
            QListWidget {
                font-size: 14px;
                padding: 5px;
            }

            QListWidget::item {
                height: 40px;
                padding-left: 8px;
                border-radius: 5px;
            }

            QListWidget::item:selected {
                background-color: #45475a;
                color: #ffffff;
            }

            QListWidget::item:hover {
                background-color: #353740;
            }
        """)

        # メインエリア
        self.stack = QStackedWidget()

        dashboard = DashboardWidget()
        self.stack.addWidget(dashboard)

        runner_widget = RunnerWidget()
        self.stack.addWidget(runner_widget)

        editor_widget = EditorWidget()
        self.stack.addWidget(editor_widget)

        template_widget = TemplateWidget()
        self.stack.addWidget(template_widget)

        snippets_widget = SnippetsWidget()
        self.stack.addWidget(snippets_widget)

        test_cases_widget = TestCasesWidget()
        self.stack.addWidget(test_cases_widget)

        settings = SettingsWidget()
        self.stack.addWidget(settings)

        # Settings 保存時に、設定を使う各画面へすぐ反映する
        settings.settings_saved.connect(dashboard.load_user_data)
        settings.settings_saved.connect(runner_widget.load_settings)
        settings.settings_saved.connect(editor_widget.load_settings)

        # 全体レイアウト
        central_widget = QWidget()
        layout = QHBoxLayout(central_widget)

        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        layout.addWidget(self.navigation)
        layout.addWidget(self.stack, 1)

        self.setCentralWidget(central_widget)

        # ナビゲーション連動
        self.navigation.currentRowChanged.connect(
            self.stack.setCurrentIndex
        )

        # 最初のページを選択
        self.navigation.setCurrentRow(0)


def main():
    db = Database()
    db.initialize()

    app = QApplication(sys.argv)

    # Qt 標準のボタンやダイアログ（Yes/No、ファイル選択など）を日本語にする
    translator = QTranslator(app)
    if translator.load(
        "qtbase_ja",
        QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath),
    ):
        app.installTranslator(translator)

    # Dark Theme
    app.setStyleSheet("""
        QWidget {
            background-color: #1e1f22;
            color: #e5e7eb;
            font-size: 14px;
        }

        QMainWindow {
            background-color: #1e1f22;
        }

        QListWidget {
            background-color: #25272b;
            border: 1px solid #3b3d42;
        }

        QLineEdit, QTextEdit, QPlainTextEdit {
            background-color: #2b2d31;
            color: #e5e7eb;
            border: 1px solid #45474d;
            border-radius: 5px;
            padding: 5px;
        }

        QPushButton {
            background-color: #36383d;
            color: #e5e7eb;
            border: 1px solid #4b4d53;
            border-radius: 5px;
            padding: 7px 12px;
        }

        QPushButton:hover {
            background-color: #45474d;
        }

        QPushButton:pressed {
            background-color: #292b2f;
        }

        QLabel {
            color: #e5e7eb;
        }

        QMenuBar {
            background-color: #25272b;
            color: #e5e7eb;
        }

        QMenuBar::item:selected {
            background-color: #36383d;
        }

        QMenu {
            background-color: #2b2d31;
            color: #e5e7eb;
            border: 1px solid #45474d;
        }

        QMenu::item:selected {
            background-color: #45474d;
        }

        QScrollBar:vertical {
            background-color: #25272b;
            width: 12px;
        }

        QScrollBar::handle:vertical {
            background-color: #505258;
            border-radius: 4px;
            min-height: 20px;
        }
    """)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()