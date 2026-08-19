from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class DashboardWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.rating_label = QLabel("1200")
        self.highest_label = QLabel("1350")
        self.color_label = QLabel("Green")
        self.updated_label = QLabel("2026-08-19")

        self.create_ui()

    def create_ui(self):
        title_label = QLabel("AtCoder Status")
        title_label.setStyleSheet("font-size: 28px; font-weight: bold;")

        form_layout = QFormLayout()

        form_layout.addRow("Rating", self.rating_label)
        form_layout.addRow("Highest", self.highest_label)
        form_layout.addRow("Color", self.color_label)
        form_layout.addRow("Updated", self.updated_label)

        layout = QVBoxLayout(self)

        layout.addWidget(title_label)
        layout.addLayout(form_layout)
        layout.addStretch()

        self.setLayout(layout)