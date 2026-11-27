
import threading

from PySide6.QtCore import Signal
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QHBoxLayout,
    QApplication,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.config import Config
from core.runner import PythonRunner


class EditorWidget(QWidget):
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
        title_label = QLabel("Python エディタ")
        title_label.setStyleSheet(
            "font-size: 24px; font-weight: bold;"
        )

        code_label = QLabel("コード")

        self.code_editor = QTextEdit()
        self.code_editor.setFont(QFont("Consolas", 11))
        self.code_editor.setPlaceholderText(
            "ここに Python コードを書きます。"
        )

        self.run_button = QPushButton("実行")
        self.run_button.setToolTip("Ctrl+Enter")
        self.run_button.clicked.connect(self.run_code)

        self.stop_button = QPushButton("停止")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_by_user)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.run_button, 1)
        button_layout.addWidget(self.stop_button)

        output_label = QLabel("出力")

        self.output_view = QTextEdit()
        self.output_view.setReadOnly(True)
        self.output_view.setFont(QFont("Consolas", 11))

        layout = QVBoxLayout(self)
        layout.addWidget(title_label)
        layout.addWidget(code_label)
        layout.addWidget(self.code_editor, 3)
        layout.addLayout(button_layout)
        layout.addWidget(output_label)
        layout.addWidget(self.output_view, 2)

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

        if not code.strip():
            self.output_view.setPlainText(
                "Python コードを入力してください。"
            )
            return

        self.run_button.setEnabled(False)
        self.run_button.setText("実行中...")
        self.stop_button.setEnabled(True)

        # 実行は別スレッドで行い、実行中も画面を操作できるようにする
        self._active_runner = self.runner
        self._thread = threading.Thread(
            target=self._run_in_background,
            args=(self.runner, code),
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

    def _run_in_background(self, runner, code):
        """別スレッドで実行。結果はシグナルで画面側に渡す。"""
        try:
            result = runner.run(code)
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
            self.output_view.setPlainText(
                f"実行エラー：\n{result['error']}"
            )
            return

        try:
            output = result["stdout"]

            if result["stderr"]:
                if output and not output.endswith("\n"):
                    output += "\n"
                output += result["stderr"]

            if result.get("stopped"):
                output += "\n停止しました。"
            elif result["timed_out"]:
                output += (
                    "\n時間切れで停止しました"
                    "（制限 5 秒）。"
                )
            elif (
                result["returncode"] not in (0, None)
                and not result["stderr"]
            ):
                output += (
                    f"\nPython が終了コード "
                    f"{result['returncode']} で終了しました。"
                )

            self.output_view.setPlainText(output)

        except Exception as error:
            self.output_view.setPlainText(
                f"実行エラー：\n{error}"
            )
