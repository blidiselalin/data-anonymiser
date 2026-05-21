"""Desktop application entry point."""

from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from data_anonymizer.desktop.theme import APP_STYLESHEET


def main() -> int:
    from data_anonymizer.desktop.main_window import MainWindow

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough,
    )
    app = QApplication(sys.argv)
    app.setApplicationName("Data Anonymizer")
    app.setOrganizationName("Zenaios")
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLESHEET)

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
