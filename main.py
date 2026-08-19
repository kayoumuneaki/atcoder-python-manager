import sys
from core.database import Database
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AtCoder Python Manager")
        self.resize(800, 600)

        label = QLabel("AtCoder Python Manager")
        label.setStyleSheet("font-size: 24px;")

        self.setCentralWidget(label)


def main():
    db = Database()
    db.initialize()

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()