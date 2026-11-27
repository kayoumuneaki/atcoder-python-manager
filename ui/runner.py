
import threading

from PySide6.QtCore import Signal
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QHBoxLayout,
    QApplication,
    QLabel,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.runner import PythonRunner
from core.config import Config


class RunnerWidget(QWidget):
    # 別スレッドの実行結果を画面スレッドへ渡すためのシグナル
    run_finished = Signal(object)

    def __init__(self):
        super().__init__()

        self.run_finished.connect(self.on_run_finished)

        self._thread = None
        self._active_runner = None
        QApplication.instance().aboutToQuit.connect(self.stop_running)

        self.config = Config()
        self.runner = PythonRunner()

        self.create_ui()
        self.create_shortcuts()
        self.load_settings()

    def create_ui(self):
        title_label = QLabel("Python 実行")
        title_label.setStyleSheet(
            "font-size: 24px; font-weight: bold;"
        )

        code_label = QLabel("Python コード")
        self.code_editor = QTextEdit()
        self.code_editor.setFont(QFont("Consolas", 11))
        self.code_editor.setPlaceholderText(
            "ここに Python コードを書きます。"
        )

        stdin_label = QLabel("標準入力")
        self.stdin_editor = QTextEdit()
        self.stdin_editor.setFont(QFont("Consolas", 11))
        self.stdin_editor.setPlaceholderText(
            "ここに標準入力を書きます。"
        )

        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        input_layout.addWidget(code_label)
        input_layout.addWidget(self.code_editor, 3)
        input_layout.addWidget(stdin_label)
        input_layout.addWidget(self.stdin_editor, 1)

        self.run_button = QPushButton("実行")
        self.run_button.setToolTip("Ctrl+Enter")
        self.run_button.clicked.connect(self.run_code)

        self.stop_button = QPushButton("停止")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_by_user)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.run_button, 1)
        button_layout.addWidget(self.stop_button)

        stdout_label = QLabel("標準出力")
        self.stdout_view = QTextEdit()
        self.stdout_view.setReadOnly(True)
        self.stdout_view.setFont(QFont("Consolas", 11))

        stderr_label = QLabel("エラー / 標準エラー出力")
        self.stderr_view = QTextEdit()
        self.stderr_view.setReadOnly(True)
        self.stderr_view.setFont(QFont("Consolas", 10))

        output_widget = QWidget()
        output_layout = QVBoxLayout(output_widget)
        output_layout.addWidget(stdout_label)
        output_layout.addWidget(self.stdout_view, 2)
        output_layout.addWidget(stderr_label)
        output_layout.addWidget(self.stderr_view, 1)

        splitter = QSplitter()
        splitter.addWidget(input_widget)
        splitter.addWidget(output_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        layout = QVBoxLayout(self)
        layout.addWidget(title_label)
        layout.addWidget(splitter, 1)
        layout.addLayout(button_layout)

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
        # 実行中は二重に実行しない（Ctrl+Enter 連打対策）
        if self._thread is not None and self._thread.is_alive():
            return

        code = self.code_editor.toPlainText()
        stdin = self.stdin_editor.toPlainText()

        if not code.strip():
            QMessageBox.warning(
                self,
                "入力エラー",
                "Python コードを入力してください。",
            )
            return

        self.run_button.setEnabled(False)
        self.run_button.setText("実行中...")
        self.stop_button.setEnabled(True)

        # 実行は別スレッドで行い、実行中も画面を操作できるようにする
        self._active_runner = self.runner
        self._thread = threading.Thread(
            target=self._run_in_background,
            args=(self.runner, code, stdin),
            daemon=True,
        )
        self._thread.start()

    def stop_by_user(self):
        """停止ボタン：実行中のコードを強制終了する。結果は on_run_finished で表示。"""
        if self._thread is not None and self._thread.is_alive():
            self.stop_button.setEnabled(False)
            self._active_runner.stop()

    def create_shortcuts(self):
        """Ctrl+Enter（テンキーの Enter も可）で実行。この画面を表示中のみ有効。"""
        for key in ("Ctrl+Return", "Ctrl+Enter"):
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.setContext(
                Qt.ShortcutContext.WidgetWithChildrenShortcut
            )
            shortcut.activated.connect(self.run_code)

    def stop_running(self):
        """アプリ終了時に、実行中のコードを止めて後片付けを待つ。"""
        if self._thread is not None and self._thread.is_alive():
            self._active_runner.stop()
            self._thread.join(timeout=3)

    def _run_in_background(self, runner, code, stdin):
        """別スレッドで実行。結果はシグナルで画面側に渡す。"""
        try:
            result = runner.run(code, stdin)
        except Exception as error:
            result = {"error": str(error)}

        try:
            self.run_finished.emit(result)
        except RuntimeError:
            # 実行中にウィンドウが閉じられた場合は何もしない
            pass

    def on_run_finished(self, result):
        self.run_button.setEnabled(True)
        self.run_button.setText("実行")
        self.stop_button.setEnabled(False)

        if "error" in result:
            QMessageBox.critical(
                self,
                "実行エラー",
                result["error"],
            )
            return

        self.stdout_view.setPlainText(result["stdout"])

        stderr = result["stderr"]

        if result.get("stopped"):
            stderr = "停止しました。\n" + stderr
        elif result["timed_out"]:
            stderr = (
                "時間切れで停止しました（制限 5 秒）。\n"
                + stderr
            )
        elif result["returncode"] != 0 and not stderr:
            stderr = (
                f"Python が終了コード "
                f"{result['returncode']} で終了しました。"
            )

        self.stderr_view.setPlainText(stderr)
