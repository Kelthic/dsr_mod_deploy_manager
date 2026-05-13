"""
styles.py
─────────────────────────────────────────────────
Font loading, QSS stylesheets, reusable widgets:
  UnitLabel, DSPanel, SectionHeader, NavBar.
"""

from PyQt6.QtWidgets import QWidget, QLabel, QFrame, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui     import QFont, QFontDatabase, QColor, QPainter, QPen, QBrush, QPolygon
from PyQt6.QtCore    import Qt, QPoint

from config import *


# ─────────────────────────────────────────────────
# FONT HELPERS
# ─────────────────────────────────────────────────

def load_fonts():
    """
    Register custom TTF fonts from the app folder.
    Returns a dict {purpose: family_name} for direct use in QFont().
    """
    global _FAMILY_MAIN, _FAMILY_UNIT

    for label, path in (("Montserrat", FONT_MONTSERRAT), ("Unitology", FONT_UNITOLOGY)):
        if not os.path.exists(path):
            print(f"[WARN] Font file not found: {path!r}")
            continue
        # Qt needs the path as a native string; also try with forward slashes
        native = os.path.normpath(path)
        fid = QFontDatabase.addApplicationFont(native)
        if fid == -1:
            # second attempt: forward slashes (sometimes helps on Windows)
            fid = QFontDatabase.addApplicationFont(path.replace("\\", "/"))
        if fid == -1:
            print(f"[WARN] Qt rejected font: {path!r}")
            continue
        families = QFontDatabase.applicationFontFamilies(fid)
        if not families:
            print(f"[WARN] Font loaded (id={fid}) but returned no families: {path!r}")
            continue
        print(f"[INFO] Font loaded: {families[0]!r}  ({label})")
        if label == "Montserrat":
            _FAMILY_MAIN = families[0]
        else:
            _FAMILY_UNIT = families[0]


_FAMILY_MAIN = "Segoe UI"    # fallback until load_fonts() runs
_FAMILY_UNIT = "Consolas"    # fallback


def font_main(size=13, bold=False) -> QFont:
    f = QFont(_FAMILY_MAIN, size)
    f.setBold(bold)
    return f


def font_unit(size=11) -> QFont:
    return QFont(_FAMILY_UNIT, size)


# ─────────────────────────────────────────────────
# GLOBAL QSS
# ─────────────────────────────────────────────────

GLOBAL_SS = f"""
QWidget {{
    background-color: {C_BG};
    color: {C_TEXT};
}}
QLineEdit {{
    background-color: {C_PANEL2};
    border: 1px solid {C_BORDER2};
    border-left: 3px solid {C_STEEL2};
    color: {C_TEXT};
    padding: 6px 10px;
    selection-background-color: {C_ACCENT};
    selection-color: #000;
}}
QLineEdit:focus {{
    border-left: 3px solid {C_ACCENT};
    background-color: {C_PANEL};
}}
QListWidget {{
    background-color: {C_PANEL2};
    border: 1px solid {C_BORDER2};
    color: {C_TEXT};
    outline: none;
}}
QListWidget::item {{
    padding: 6px 10px;
    border-bottom: 1px solid #0d1a22;
}}
QListWidget::item:selected {{
    background-color: {C_PANEL};
    color: {C_ACCENT};
    border-left: 3px solid {C_ACCENT};
}}
QListWidget::item:hover {{
    background-color: {C_PANEL};
}}
QScrollBar:vertical {{
    background: {C_BG};
    width: 6px;
    border: none;
}}
QScrollBar::handle:vertical {{
    background: {C_BORDER2};
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{
    background: {C_STEEL};
}}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{ height: 0; }}
QTextEdit {{
    background-color: #060a0d;
    border: 1px solid {C_BORDER2};
    color: {C_STEEL};
    padding: 6px;
}}
QProgressBar {{
    background-color: {C_PANEL2};
    border: 1px solid {C_BORDER2};
    text-align: center;
    color: transparent;
}}
QProgressBar::chunk {{
    background-color: {C_ACCENT};
}}
"""

DS_BTN_SS = f"""
QPushButton {{
    background-color: {C_PANEL};
    border: 1px solid {C_BORDER2};
    color: {C_STEEL};
    padding: 5px 12px;
    letter-spacing: 2px;
}}
QPushButton:hover {{
    background-color: {C_PANEL2};
    border: 1px solid {C_STEEL};
    color: {C_TEXT};
}}
QPushButton:pressed {{
    background-color: {C_STEEL2};
    color: {C_ACCENT};
}}
QPushButton:disabled {{
    background-color: {C_BG};
    border: 1px solid #0f1e28;
    color: #1e3040;
}}
"""

DEPLOY_BTN_SS = f"""
QPushButton {{
    background-color: {C_PANEL2};
    border: 2px solid {C_ACCENT};
    color: {C_ACCENT};
    padding: 10px 0px;
    letter-spacing: 6px;
    font-weight: bold;
}}
QPushButton:hover {{
    background-color: {C_ACCENT};
    color: {C_BG};
    border: 2px solid {C_ACCENT2};
}}
QPushButton:pressed {{
    background-color: {C_ACCENT2};
    color: {C_BG};
}}
QPushButton:disabled {{
    background-color: {C_BG};
    border: 2px solid {C_STEEL2};
    color: {C_STEEL2};
}}
"""


# ─────────────────────────────────────────────────
# WIDGETS
# ─────────────────────────────────────────────────

def h_sep() -> QFrame:
    """Thin horizontal separator."""
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    f.setFixedHeight(1)
    f.setStyleSheet(f"background: {C_BORDER2}; border: none;")
    return f


class UnitLabel(QWidget):
    """
    Two-row label:
      row 1 — text in Montserrat (main_color)
      row 2 — same text in Unitology font (unit_color, dim)
    """
    def __init__(self, text="", main_size=14, unit_size=12,
                 color=C_TEXT, unit_color=C_UNITOLOGY, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(1)

        self._main = QLabel(text)
        self._main.setFont(font_main(main_size))
        self._main.setStyleSheet(f"color: {color}; background: transparent;")

        self._unit = QLabel(text)
        self._unit.setFont(font_unit(unit_size))
        self._unit.setStyleSheet(f"color: {unit_color}; background: transparent;")

        lay.addWidget(self._main)
        lay.addWidget(self._unit)

    def setText(self, t: str):
        self._main.setText(t)
        self._unit.setText(t)

    def setMainColor(self, c: str):
        self._main.setStyleSheet(f"color: {c}; background: transparent;")

    def text(self) -> str:
        return self._main.text()


class DSPanel(QFrame):
    """Panel with a clipped top-left corner, like DS inventory panels."""
    def __init__(self, clip=14, parent=None):
        super().__init__(parent)
        self._clip = clip
        self.setStyleSheet("background: transparent;")

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h, c = self.width(), self.height(), self._clip
        pts = QPolygon([
            QPoint(c, 0), QPoint(w, 0),
            QPoint(w, h), QPoint(0, h), QPoint(0, c),
        ])
        p.setBrush(QBrush(QColor(C_PANEL)))
        p.setPen(QPen(QColor(C_BORDER), 1))
        p.drawPolygon(pts)
        p.setPen(QPen(QColor(C_STEEL), 1))
        p.drawLine(0, c, c, 0)
        p.end()
        super().paintEvent(e)


class SectionHeader(QWidget):
    """▼  TITLE  ─────────────────"""
    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 6, 0, 2)
        lay.setSpacing(8)

        arrow = QLabel("▼")
        arrow.setFont(font_main(8))
        arrow.setStyleSheet(f"color: {C_STEEL}; background: transparent;")

        lbl = UnitLabel(text, main_size=12, unit_size=10,
                        color=C_TEXT, unit_color=C_UNITOLOGY)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFixedHeight(1)
        line.setStyleSheet(f"background: {C_BORDER2}; border: none;")

        lay.addWidget(arrow)
        lay.addWidget(lbl)
        lay.addWidget(line, 1)


class NavBar(QWidget):
    """Bottom hotkey strip (DS-style)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(36)
        self.setStyleSheet(f"background: {C_PANEL2}; border-top: 1px solid {C_BORDER};")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 0, 16, 0)
        lay.setSpacing(20)

        for label, key in [
            ("BROWSE", "B"), ("LOAD", "L"), ("CHECK", "C"),
            ("DEPLOY", "D"), ("RESTORE", "R"), ("CLOSE", "ESC"),
        ]:
            w = QWidget()
            w.setStyleSheet("background: transparent;")
            wl = QHBoxLayout(w)
            wl.setContentsMargins(0, 0, 0, 0)
            wl.setSpacing(5)

            k = QLabel(key)
            k.setFont(font_main(8, bold=True))
            k.setStyleSheet(
                f"color: {C_BG}; background: {C_STEEL2};"
                "padding: 1px 5px; border-radius: 2px;"
            )
            t = QLabel(label)
            t.setFont(font_main(8))
            t.setStyleSheet(f"color: {C_TEXT_DIM}; background: transparent;")

            wl.addWidget(k)
            wl.addWidget(t)
            lay.addWidget(w)

        lay.addStretch()

        ver = UnitLabel(f"v{APP_VERSION}", main_size=12, unit_size=10,
                        color=C_TEXT_DIM, unit_color="#0f1e28")
        lay.addWidget(ver)
