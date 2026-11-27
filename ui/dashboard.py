
import threading
from datetime import datetime

import pyqtgraph as pg
from pyqtgraph.graphicsItems.DateAxisItem import DateAxisItem

from PySide6.QtCore import Signal
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QToolTip,
    QVBoxLayout,
    QWidget,
)

from core.atcoder import (
    AtCoderAPIError,
    AtCoderClient,
    AtCoderUserNotFoundError,
)
from core.config import Config


# ダークテーマで読みやすいレート色（グラフの色帯とは別に、文字用に明るめ）
RATING_TEXT_COLORS = {
    "gray": "#c0c0c0",
    "brown": "#c08a5a",
    "green": "#4cbf4c",
    "cyan": "#22c8c8",
    "blue": "#7b93ff",
    "yellow": "#e0c400",
    "orange": "#ff9a3c",
    "red": "#ff5c5c",
}


# レート色の日本語名
RATING_COLOR_NAMES = {
    "gray": "灰",
    "brown": "茶",
    "green": "緑",
    "cyan": "水",
    "blue": "青",
    "yellow": "黄",
    "orange": "橙",
    "red": "赤",
}


def format_contest_time(end_time):
    """'2024-01-01T22:40:00+09:00' -> '2024-01-01 22:40'。読めなければそのまま。"""
    if not end_time:
        return "-"
    try:
        return datetime.fromisoformat(end_time).strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return str(end_time)


class StatCard(QFrame):
    """見出し・大きな値・補足の3段で表示するカード。"""

    def __init__(self, title):
        super().__init__()
        self.setObjectName("statCard")
        self.setStyleSheet("""
            QFrame#statCard {
                background-color: #25272b;
                border: 1px solid #3b3d42;
                border-radius: 8px;
            }
            QFrame#statCard QLabel {
                background-color: transparent;
            }
        """)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #9ca3af; font-size: 12px;")

        self.value_label = QLabel("-")
        self.value_label.setWordWrap(True)

        self.sub_label = QLabel("")
        self.sub_label.setStyleSheet("color: #9ca3af; font-size: 12px;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(4)
        layout.addWidget(title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.sub_label)
        layout.addStretch(1)

        self.set_value("-")

    def set_value(self, text, sub="", color=None, small=False):
        size = 15 if small else 24
        color_css = f"color: {color};" if color else ""
        self.value_label.setStyleSheet(
            f"font-size: {size}px; font-weight: bold; {color_css}"
        )
        self.value_label.setText(text)
        self.sub_label.setText(sub)


class DashboardWidget(QWidget):
    # 別スレッドの通信結果を画面スレッドへ渡すためのシグナル
    # 引数は (リクエスト番号, 結果)。古いリクエストの結果を見分けるために番号を付ける
    data_loaded = Signal(int, object)
    load_failed = Signal(int, str)

    def __init__(self):
        super().__init__()

        self._request_id = 0

        self.data_loaded.connect(self.on_data_loaded)
        self.load_failed.connect(self.on_load_failed)

        self.rating_card = StatCard("レート")
        self.highest_card = StatCard("最高レート")
        self.count_card = StatCard("Rated 参加回数")
        self.last_contest_card = StatCard("最終参加コンテスト")
        self.user_label = QLabel("")
        self.status_label = QLabel("取得中...")
        self.status_label.setStyleSheet("color: #9ca3af;")

        self.graph = None
        self.curve = None
        self.scatter = None
        self.performance_data = []

        self.create_ui()
        self.load_user_data()

    def create_ui(self):
        title_label = QLabel("AtCoder 成績")
        title_label.setStyleSheet(
            "font-size: 28px; font-weight: bold;"
        )

        self.user_label.setStyleSheet("color: #9ca3af; font-size: 16px;")

        self.refresh_button = QPushButton("更新")
        self.refresh_button.setToolTip("AtCoder からデータを取り直します")
        self.refresh_button.clicked.connect(self.load_user_data)

        header_layout = QHBoxLayout()
        header_layout.addWidget(title_label)
        header_layout.addSpacing(12)
        header_layout.addWidget(self.user_label)
        header_layout.addStretch(1)
        header_layout.addWidget(self.refresh_button)

        # カード4枚（最終参加コンテストは名前が長いので2列分）
        cards_layout = QGridLayout()
        cards_layout.setSpacing(10)
        cards_layout.addWidget(self.rating_card, 0, 0)
        cards_layout.addWidget(self.highest_card, 0, 1)
        cards_layout.addWidget(self.count_card, 0, 2)
        cards_layout.addWidget(self.last_contest_card, 0, 3, 1, 2)
        for column in range(5):
            cards_layout.setColumnStretch(column, 1)

        self.graph = pg.PlotWidget(
            axisItems={
                "bottom": DateAxisItem(orientation="bottom")
            }
        )
        self.graph.setBackground("#202124")
        self.graph.setLabel("left", "レート")
        self.graph.setLabel("bottom", "コンテスト日")
        self.graph.showGrid(x=True, y=True, alpha=0.25)
        self.graph.setMinimumHeight(350)
        self.graph.setMouseEnabled(x=True, y=False)
        self.graph.getViewBox().setLimits(yMin=0)

        layout = QVBoxLayout(self)
        layout.addLayout(header_layout)
        layout.addLayout(cards_layout)
        layout.addWidget(self.status_label)
        layout.addWidget(self.graph, 1)

    def load_user_data(self):
        # 再読込時に、前のユーザーの表示が残らないよう初期化する
        self._request_id += 1
        self.clear_user_data()

        settings = Config().load()
        username = settings.get("atcoder_username", "").strip()
        self.user_label.setText(username)
        self.finish_loading()

        if not username:
            self.status_label.setText(
                "設定画面で AtCoder のユーザー名を入力してください。"
            )
            return

        self.status_label.setText(
            f"{username} のデータを取得中..."
        )
        self.refresh_button.setEnabled(False)
        self.refresh_button.setText("取得中...")

        # 通信は別スレッドで行い、起動や画面操作を止めない
        thread = threading.Thread(
            target=self._fetch_user_data,
            args=(self._request_id, username),
            daemon=True,
        )
        thread.start()

    def clear_user_data(self):
        for card in (
            self.rating_card,
            self.highest_card,
            self.count_card,
            self.last_contest_card,
        ):
            card.set_value("-")
        self.performance_data = []
        self.scatter = None
        self.curve = None
        self.graph.clear()

    def _fetch_user_data(self, request_id, username):
        """別スレッドで実行。結果はシグナルで画面側に渡す。"""
        try:
            data = AtCoderClient().get_user_info(username)
        except AtCoderUserNotFoundError as error:
            message = f"{error}設定画面でユーザー名を確認してください。"
            result = None
        except AtCoderAPIError as error:
            message = f"AtCoder のデータを取得できませんでした：{error}"
            result = None
        except Exception as error:
            message = f"予期しないエラー：{error}"
            result = None
        else:
            message = None
            result = data

        try:
            if result is None:
                self.load_failed.emit(request_id, message)
            else:
                self.data_loaded.emit(request_id, result)
        except RuntimeError:
            # 通信中にウィンドウが閉じられた場合は何もしない
            pass

    def on_load_failed(self, request_id, message):
        # 設定変更で再読込済みなら、古い通信結果は捨てる
        if request_id != self._request_id:
            return

        self.finish_loading()
        self.status_label.setText(message)

    def finish_loading(self):
        self.refresh_button.setEnabled(True)
        self.refresh_button.setText("更新")

    def on_data_loaded(self, request_id, data):
        if request_id != self._request_id:
            return

        self.finish_loading()

        rating = data["rating"]
        highest = data["highest"]

        if rating is None:
            self.rating_card.set_value("-", "Unrated")
            self.highest_card.set_value("-")
        else:
            color = data["color"]
            highest_color = AtCoderClient.get_rating_color(highest)
            self.rating_card.set_value(
                str(rating),
                RATING_COLOR_NAMES.get(color, color),
                RATING_TEXT_COLORS.get(color),
            )
            self.highest_card.set_value(
                str(highest),
                RATING_COLOR_NAMES.get(highest_color, highest_color),
                RATING_TEXT_COLORS.get(highest_color),
            )

        self.count_card.set_value(str(data.get("rated_count", 0)))

        last_contest = data.get("last_contest")
        if last_contest:
            sub = format_contest_time(last_contest["end_time"])
            if not last_contest["is_rated"]:
                sub += "  (Unrated)"
            self.last_contest_card.set_value(
                last_contest["contest_name"] or "-",
                sub,
                small=True,
            )
        else:
            self.last_contest_card.set_value("-", "参加なし")

        self.performance_data = data["performances"]

        if not last_contest:
            self.graph.clear()
            self.status_label.setText(
                f"{data['username']} はまだコンテストに参加していません。"
            )
            return

        self.draw_rating_graph()

        if self.performance_data:
            self.status_label.setText(
                f"Rated コンテスト {len(self.performance_data)} 回分を読み込みました。"
            )

    def draw_rating_graph(self):
        self.graph.clear()

        if not self.performance_data:
            self.status_label.setText(
                "Rated の参加履歴がありません。"
            )
            return

        bands = [
            (0, 400, "#795548"),
            (400, 800, "#808080"),
            (800, 1200, "#008000"),
            (1200, 1600, "#00C0C0"),
            (1600, 2000, "#0000FF"),
            (2000, 2400, "#FFFF00"),
            (2400, 2800, "#FF8000"),
            (2800, 5000, "#FF0000"),
        ]

        for lower, upper, color in bands:
            # mkBrush は alpha 引数を無視するため、色そのものに透明度を設定する
            band_color = pg.mkColor(color)
            band_color.setAlpha(35)

            region = pg.LinearRegionItem(
                values=[lower, upper],
                orientation="horizontal",
                movable=False,
                brush=pg.mkBrush(band_color),
                pen=pg.mkPen(color=color, width=0.5),
            )
            region.setZValue(-10)
            self.graph.addItem(region)

        points = []

        for item in self.performance_data:
            end_time = item.get("end_time")
            rating = item.get("rating")

            if not end_time or rating is None:
                continue

            try:
                timestamp = datetime.fromisoformat(
                    end_time
                ).timestamp()
            except (ValueError, TypeError):
                continue

            points.append({
                "x": timestamp,
                "y": rating,
                "contest_name": item.get(
                    "contest_name", "不明なコンテスト"
                ),
                "end_time": end_time,
                "performance": item.get("performance"),
                "rating": rating,
            })

        points.sort(key=lambda point: point["x"])

        if not points:
            self.status_label.setText(
                "グラフに表示できるデータがありません。"
            )
            return

        x_values = [point["x"] for point in points]
        y_values = [point["y"] for point in points]

        self.curve = self.graph.plot(
            x_values,
            y_values,
            pen=pg.mkPen("#55AAFF", width=2),
        )

        # 点はここで1回だけ作成し、各点にコンテスト情報を持たせる
        self.scatter = pg.ScatterPlotItem(
            x=x_values,
            y=y_values,
            data=points,
            size=8,
            brush=pg.mkBrush("#FFFFFF"),
            pen=pg.mkPen("#55AAFF", width=1.5),
            hoverable=True,
            hoverSize=13,
            hoverBrush=pg.mkBrush("#FFD54F"),
            tip=None,  # 標準の x/y ツールチップを無効化し、独自表示のみにする
        )

        self.scatter.sigHovered.connect(
            self.on_point_hovered
        )
        self.graph.addItem(self.scatter)

        self.graph.setYRange(
            0,
            max(3200, max(y_values) + 200),
            padding=0,
        )

        self.graph.setXRange(
            min(x_values),
            max(x_values) if len(x_values) > 1
            else min(x_values) + 86400,
            padding=0.03,
        )

    def on_point_hovered(self, item, points, event):
        # sigHovered は (item, points, ev) を渡す。points は numpy 配列
        if len(points) == 0:
            QToolTip.hideText()
            return

        point = points[0].data()
        if not point:
            return

        performance = point["performance"]
        performance_text = (
            str(performance)
            if performance is not None
            else "-"
        )

        message = (
            f'{point["contest_name"]}\n'
            f'日時: {format_contest_time(point["end_time"])}\n'
            f'レート: {point["rating"]}\n'
            f'パフォーマンス: {performance_text}'
        )

        QToolTip.showText(
            QCursor.pos(),
            message,
            self.graph,
        )
