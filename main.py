"""
main.py
─────────────────────────────────────────────────
Entry point.  Run this file to start the app.

Project structure:
    main.py      ← you are here (entry point)
    config.py    ← colours, paths, app metadata
    styles.py    ← fonts, QSS, reusable widgets
    worker.py    ← DeployThread + file helpers
    window.py    ← MainWindow (UI + slots)

Assets (place next to main.py):
    Montserrat-Medium.ttf
    DeadSpace Unitology.ttf
    icon.ico  (or icon.png)
"""

import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui     import QColor, QPalette

from config  import C_BG, C_TEXT, C_PANEL, C_STEEL, C_ACCENT
from styles  import load_fonts
from window  import MainWindow


def build_palette() -> QPalette:
    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window,          QColor(C_BG))
    pal.setColor(QPalette.ColorRole.WindowText,      QColor(C_TEXT))
    pal.setColor(QPalette.ColorRole.Base,            QColor(C_BG))
    pal.setColor(QPalette.ColorRole.AlternateBase,   QColor(C_PANEL))
    pal.setColor(QPalette.ColorRole.Text,            QColor(C_TEXT))
    pal.setColor(QPalette.ColorRole.Button,          QColor(C_PANEL))
    pal.setColor(QPalette.ColorRole.ButtonText,      QColor(C_STEEL))
    pal.setColor(QPalette.ColorRole.Highlight,       QColor(C_ACCENT))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor("#000000"))
    return pal


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setPalette(build_palette())

    load_fonts()   # must happen AFTER QApplication is created
    # Debug: print all loaded font families to console
    from PyQt6.QtGui import QFontDatabase as _FDB
    print("[INFO] All app fonts:", [f for f in _FDB.families() if any(
        k in f for k in ("Montserrat","Unitology","Dead","DS"))])

    w = MainWindow()
    w.show()
    sys.exit(app.exec())
