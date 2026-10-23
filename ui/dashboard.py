
from datetime import datetime

import pyqtgraph as pg
from pyqtgraph.graphicsItems.DateAxisItem import DateAxisItem

from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (
    QFormLayout,
    QLabel,
    QToolTip,
    QVBoxLayout,
    QWidget,
)

from core.atcoder import AtCoderClient, AtCoderAPIError
from core.config import Config


class DashboardWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.rating_label = QLabel("-")
        self.highest_label = QLabel("-")
        self.color_label = QLabel("-")
        self.updated_label = QLabel("-")
        self.status_label = QLabel("Loading...")

        self.graph = None
        self.curve = None
        self.scatter = None
        self.performance_data = []

        self.create_ui()
        self.load_user_data()

    def create_ui(self):
        title_label = QLabel("AtCoder Status")
        title_label.setStyleSheet(
            "font-size: 28px; font-weight: bold;"
        )

        form_layout = QFormLayout()
        form_layout.addRow("Rating", self.rating_label)
        form_layout.addRow("Highest", self.highest_label)
        form_layout.addRow("Color", self.color_label)
        form_layout.addRow("Updated", self.updated_label)

        self.graph = pg.PlotWidget(
            axisItems={
                "bottom": DateAxisItem(orientation="bottom")
            }
        )
        self.graph.setBackground("#202124")
        self.graph.setLabel("left", "Rating")
        self.graph.setLabel("bottom", "Contest Date")
        self.graph.showGrid(x=True, y=True, alpha=0.25)
        self.graph.setMinimumHeight(350)
        self.graph.setMouseEnabled(x=True, y=False)
        self.graph.getViewBox().setLimits(yMin=0)

        layout = QVBoxLayout(self)
        layout.addWidget(title_label)
        layout.addLayout(form_layout)
        layout.addWidget(self.status_label)
        layout.addWidget(self.graph, 1)

    def load_user_data(self):
        settings = Config().load()
        username = settings.get("atcoder_username", "").strip()

        if not username:
            self.status_label.setText(
                "Set your AtCoder username in Settings."
            )
            return

        self.status_label.setText(
            f"Loading data for {username}..."
        )

        try:
            data = AtCoderClient().get_user_info(username)
        except AtCoderAPIError as error:
            self.status_label.setText(
                f"Failed to load AtCoder data: {error}"
            )
            return
        except Exception as error:
            self.status_label.setText(
                f"Unexpected error: {error}"
            )
            return

        self.rating_label.setText(str(data["rating"]))
        self.highest_label.setText(str(data["highest"]))
        self.color_label.setText(data["color"])
        self.updated_label.setText(data["updated_at"] or "-")

        self.performance_data = data["performances"]
        self.draw_rating_graph()

        self.status_label.setText(
            f"Loaded {len(self.performance_data)} contests."
        )

    def draw_rating_graph(self):
        self.graph.clear()

        if not self.performance_data:
            self.status_label.setText(
                "No rating history available."
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
            region = pg.LinearRegionItem(
                values=[lower, upper],
                orientation="horizontal",
                movable=False,
                brush=pg.mkBrush(color=color, alpha=35),
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
                    "contest_name", "Unknown contest"
                ),
                "end_time": end_time,
                "performance": item.get("performance"),
                "rating": rating,
            })

        points.sort(key=lambda point: point["x"])

        if not points:
            self.status_label.setText(
                "No valid rating points available."
            )
            return

        x_values = [point["x"] for point in points]
        y_values = [point["y"] for point in points]

        self.curve = self.graph.plot(
            x_values,
            y_values,
            pen=pg.mkPen("#55AAFF", width=2),
        )

        self.scatter = pg.ScatterPlotItem(
            x=x_values,
            y=y_values,
            size=8,
            brush=pg.mkBrush("#FFFFFF"),
            pen=pg.mkPen("#55AAFF", width=1.5),
            hoverable=True,
            hoverSize=13,
            hoverBrush=pg.mkBrush("#FFD54F"),
        )

        self.scatter.addPoints([
            {
                "pos": (point["x"], point["y"]),
                "data": point,
            }
            for point in points
        ])

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

    def on_point_hovered(self, points, event):
        if not points:
            return

        point = points[0].data()
        performance = point["performance"]
        performance_text = (
            str(performance)
            if performance is not None
            else "N/A"
        )

        message = (
            f'{point["contest_name"]}\n'
            f'Date: {point["end_time"]}\n'
            f'Rating: {point["rating"]}\n'
            f'Performance: {performance_text}'
        )

        QToolTip.showText(
            QCursor.pos(),
            message,
            self.graph,
        )
