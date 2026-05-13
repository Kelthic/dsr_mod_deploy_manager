"""
config.py
─────────────────────────────────────────────────
All constants: colours, sizes, app metadata.
"""

import os

# ── App ──────────────────────────────────────────
APP_TITLE   = "DEAD SPACE REMAKE  //  MOD DEPLOY MANAGER"
APP_VERSION = "1.0"
APP_AUTHOR  = "Mark de Rune"
APP_GITHUB  = "https://github.com/Kelthic/dsr_mod_deploy_manager/"

WIN_W, WIN_H = 1020, 800

# ── Asset paths (same dir as main.py) ────────────
_BASE = os.path.dirname(os.path.abspath(__file__))

FONT_MONTSERRAT = os.path.join(_BASE, "Montserrat-Medium.ttf")
FONT_UNITOLOGY  = os.path.join(_BASE, "DeadSpace Unitology.ttf")

# Icon — tries all known variants in order
_ICON_CANDIDATES = [
    "app_icon.PNG", "app_icon.png", "app_icon.ico",
    "icon.ico",     "icon.png",     "icon.PNG",
]
APP_ICON = next(
    (os.path.join(_BASE, n) for n in _ICON_CANDIDATES
     if os.path.exists(os.path.join(_BASE, n))),
    None,
)

# ── Colour palette (Dead Space inventory) ────────
C_BG        = "#0a0e12"
C_PANEL     = "#0d1520"
C_PANEL2    = "#0b1219"
C_BORDER    = "#1e3a52"
C_BORDER2   = "#152838"
C_TEXT      = "#c8d8e8"
C_TEXT_DIM  = "#3a5a70"
C_ACCENT    = "#e87820"
C_ACCENT2   = "#f0a040"
C_STEEL     = "#5a8090"
C_STEEL2    = "#2a4a5a"
C_GREEN     = "#50c878"
C_RED       = "#cc3333"
C_UNITOLOGY = "#1b3040"
