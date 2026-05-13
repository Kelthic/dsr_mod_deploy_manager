"""
window.py
─────────────────────────────────────────────────
Main application window — layout, panels, slots.
"""

import os
import json
import shutil

from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QLineEdit,
    QFileDialog, QListWidget, QTextEdit, QMessageBox,
    QVBoxLayout, QHBoxLayout, QProgressBar, QListWidgetItem,
    QFrame,
)
from PyQt6.QtGui  import QIcon
from PyQt6.QtCore import Qt

from config  import *
from styles  import (
    font_main, font_unit,
    GLOBAL_SS, DS_BTN_SS, DEPLOY_BTN_SS,
    UnitLabel, SectionHeader, NavBar, h_sep,
)
from worker  import DeployThread, ensure_dir


# ─────────────────────────────────────────────────
# MAIN WINDOW
# ─────────────────────────────────────────────────

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.setFixedSize(WIN_W, WIN_H)
        self.setStyleSheet(GLOBAL_SS)
        self._set_icon()
        self._build()

    # ── Icon ─────────────────────────────────────

    def _set_icon(self):
        if APP_ICON and os.path.exists(APP_ICON):
            self.setWindowIcon(QIcon(APP_ICON))
            print(f"[INFO] Icon loaded: {APP_ICON!r}")
        else:
            print(f"[WARN] No icon found in app folder")

    # ── Layout ───────────────────────────────────

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._make_title_bar())

        body = QWidget()
        body_lay = QHBoxLayout(body)
        body_lay.setContentsMargins(16, 14, 16, 10)
        body_lay.setSpacing(14)

        left_w = QWidget()
        left_w.setFixedWidth(430)
        left_w.setStyleSheet("background: transparent;")
        self._left = QVBoxLayout(left_w)
        self._left.setContentsMargins(0, 0, 0, 0)
        self._left.setSpacing(10)

        self._right = QVBoxLayout()
        self._right.setContentsMargins(0, 0, 0, 0)
        self._right.setSpacing(10)

        body_lay.addWidget(left_w)
        body_lay.addLayout(self._right, 1)

        root.addWidget(body, 1)
        root.addWidget(NavBar())

        self._build_left()
        self._build_right()

        # wire signals
        self.src_btn.clicked.connect(self.pick_src)
        self.game_btn.clicked.connect(self.pick_game)
        self.src_apply.clicked.connect(self.load_mods)
        self.game_apply.clicked.connect(self.check_game)
        self.deploy_btn.clicked.connect(self.deploy)
        self.restore_btn.clicked.connect(self.restore)

    # ── Title bar ────────────────────────────────

    def _make_title_bar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(56)
        bar.setStyleSheet(
            f"background: {C_PANEL2}; border-bottom: 2px solid {C_BORDER};"
        )
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(20, 0, 20, 0)
        lay.setSpacing(0)

        t1 = QLabel("DEAD SPACE")
        t1.setFont(font_main(20, bold=True))
        t1.setStyleSheet(
            f"color: {C_TEXT}; background: transparent; letter-spacing: 8px;"
        )

        div = QFrame()
        div.setFrameShape(QFrame.Shape.VLine)
        div.setFixedWidth(1)
        div.setStyleSheet(f"background: {C_BORDER}; border: none; margin: 12px 16px;")

        t2 = UnitLabel("MOD DEPLOY MANAGER", main_size=13, unit_size=11,
                       color=C_STEEL, unit_color=C_UNITOLOGY)

        self._chip = QLabel("OFFLINE")
        self._chip.setFont(font_main(8, bold=True))
        self._chip.setStyleSheet(
            f"color: {C_TEXT_DIM}; background: {C_PANEL};"
            f"border: 1px solid {C_BORDER2}; padding: 4px 12px; letter-spacing: 3px;"
        )

        lay.addWidget(t1)
        lay.addWidget(div)
        lay.addWidget(t2)
        lay.addStretch()
        lay.addWidget(self._chip)
        return bar

    # ── Left panel ───────────────────────────────

    def _build_left(self):
        L = self._left

        # — Mods source —
        L.addWidget(SectionHeader("MODS DATA FOLDER"))

        row = QHBoxLayout(); row.setSpacing(6)
        self.src = QLineEdit()
        self.src.setFont(font_main(10))
        self.src.setFixedHeight(32)
        self.src.setPlaceholderText("path/to/mods/data...")
        self.src_btn   = self._btn("BROWSE")
        self.src_apply = self._btn("LOAD")
        row.addWidget(self.src)
        row.addWidget(self.src_btn)
        row.addWidget(self.src_apply)
        L.addLayout(row)

        self.mods_count = UnitLabel("MODS: 0  —  NO LIST LOADED",
                                    main_size=12, unit_size=10,
                                    color=C_TEXT_DIM, unit_color=C_UNITOLOGY)
        L.addWidget(self.mods_count)

        self.mods_list = QListWidget()
        self.mods_list.setFont(font_main(10))
        self.mods_list.setFixedHeight(140)
        L.addWidget(self.mods_list)

        L.addWidget(h_sep())

        # — Game folder —
        L.addWidget(SectionHeader("GAME INSTALLATION"))

        row2 = QHBoxLayout(); row2.setSpacing(6)
        self.game = QLineEdit()
        self.game.setFont(font_main(10))
        self.game.setFixedHeight(32)
        self.game.setPlaceholderText("path/to/Dead Space/...")
        self.game_btn   = self._btn("BROWSE")
        self.game_apply = self._btn("CHECK")
        row2.addWidget(self.game)
        row2.addWidget(self.game_btn)
        row2.addWidget(self.game_apply)
        L.addLayout(row2)

        self.exe_status = UnitLabel("EXECUTABLE: NOT CHECKED",
                                    main_size=12, unit_size=10,
                                    color=C_TEXT_DIM, unit_color=C_UNITOLOGY)
        L.addWidget(self.exe_status)

        L.addWidget(h_sep())

        # — About block (fills leftover space) —
        L.addWidget(self._make_about())
        L.addStretch()

    def _make_about(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 4, 0, 4)
        lay.setSpacing(6)

        def row(label_text, value_text, value_color=C_TEXT_DIM):
            r = QWidget(); r.setStyleSheet("background: transparent;")
            rl = QHBoxLayout(r); rl.setContentsMargins(0,0,0,0); rl.setSpacing(10)

            lbl = UnitLabel(label_text, main_size=12, unit_size=10,
                            color=C_STEEL2, unit_color=C_UNITOLOGY)
            val = UnitLabel(value_text, main_size=12, unit_size=10,
                            color=value_color, unit_color=C_UNITOLOGY)
            rl.addWidget(lbl)
            rl.addWidget(val)
            rl.addStretch()
            return r

        lay.addWidget(row("AUTHOR",  APP_AUTHOR,  C_TEXT_DIM))
        lay.addWidget(row("VERSION", f"v{APP_VERSION}", C_STEEL))

        # GitHub link label
        gh_row = QWidget(); gh_row.setStyleSheet("background: transparent;")
        gh_l = QHBoxLayout(gh_row); gh_l.setContentsMargins(0,0,0,0); gh_l.setSpacing(10)

        lbl_key = UnitLabel("GITHUB", main_size=12, unit_size=10,
                            color=C_STEEL2, unit_color=C_UNITOLOGY)
        lbl_val = QLabel(f'<a href="{APP_GITHUB}" style="color:{C_STEEL}; text-decoration:none;">{APP_GITHUB}</a>')
        lbl_val.setFont(font_main(8))
        lbl_val.setOpenExternalLinks(True)
        lbl_val.setStyleSheet("background: transparent;")

        gh_l.addWidget(lbl_key)
        gh_l.addWidget(lbl_val)
        gh_l.addStretch()
        lay.addWidget(gh_row)

        return w

    # ── Right panel ──────────────────────────────

    def _build_right(self):
        R = self._right

        R.addWidget(SectionHeader("OPERATIONS"))

        self.deploy_btn = QPushButton("DEPLOY MODS")
        self.deploy_btn.setFont(font_main(13, bold=True))
        self.deploy_btn.setStyleSheet(DEPLOY_BTN_SS)
        self.deploy_btn.setEnabled(False)
        self.deploy_btn.setFixedHeight(54)
        R.addWidget(self.deploy_btn)

        self.restore_btn = QPushButton("RESTORE BACKUP")
        self.restore_btn.setFont(font_main(10))
        self.restore_btn.setStyleSheet(DS_BTN_SS)
        self.restore_btn.setFixedHeight(36)
        R.addWidget(self.restore_btn)

        R.addWidget(h_sep())

        R.addWidget(SectionHeader("TRANSFER STATUS"))

        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setFixedHeight(8)
        R.addWidget(self.progress)

        pct_row = QHBoxLayout()
        self.pct_label = UnitLabel("0%", main_size=12, unit_size=10,
                                   color=C_ACCENT, unit_color=C_UNITOLOGY)
        pct_row.addStretch()
        pct_row.addWidget(self.pct_label)
        R.addLayout(pct_row)

        R.addWidget(h_sep())

        R.addWidget(SectionHeader("SYSTEM LOG"))

        self.log_box = QTextEdit()
        self.log_box.setFont(font_main(9))
        self.log_box.setReadOnly(True)
        R.addWidget(self.log_box, 1)

    # ── Helpers ──────────────────────────────────

    def _btn(self, label: str) -> QPushButton:
        b = QPushButton(label)
        b.setFont(font_main(9))
        b.setStyleSheet(DS_BTN_SS)
        b.setFixedHeight(32)
        return b

    def _log(self, t: str):
        mapping = {
            "[DEPLOY]":  C_ACCENT,
            "[BACKUP]":  "#7ab0c8",
            "[SKIP]":    C_TEXT_DIM,
            "[CLEAN]":   C_STEEL2,
            "[INFO]":    C_TEXT,
            "[ERROR]":   C_RED,
            "[RESTORE]": C_GREEN,
        }
        col = next((v for k, v in mapping.items() if k in t), C_STEEL)
        self.log_box.append(
            f'<span style="color:{col}; font-size:10px">{t}</span>'
        )

    def _set_chip(self, text: str, bg: str, fg: str = None):
        fg = fg or C_BG
        self._chip.setText(text)
        self._chip.setStyleSheet(
            f"color: {fg}; background: {bg};"
            f"border: 1px solid {bg}; padding: 4px 12px; letter-spacing: 3px;"
        )

    def _update_progress(self, v: int):
        self.progress.setValue(v)
        self.pct_label.setText(f"{v}%")

    def _alert(self, title: str, msg: str, err: bool = False):
        col = C_RED if err else C_ACCENT
        box = QMessageBox(self)
        box.setWindowTitle(title)
        box.setText(msg)
        box.setIcon(QMessageBox.Icon.Critical if err else QMessageBox.Icon.Information)
        box.setStyleSheet(f"""
            QMessageBox {{ background: {C_PANEL2}; }}
            QMessageBox QLabel {{
                color: {col};
                font-family: Montserrat, Segoe UI;
                font-size: 11px;
            }}
            QPushButton {{
                background: {C_PANEL};
                border: 1px solid {C_BORDER2};
                color: {C_STEEL};
                padding: 5px 16px;
                letter-spacing: 2px;
            }}
            QPushButton:hover {{
                border: 1px solid {C_STEEL};
                color: {C_TEXT};
            }}
        """)
        box.exec()

    # ── Slots ────────────────────────────────────

    def pick_src(self):
        d = QFileDialog.getExistingDirectory(self, "Select Mods Data Folder")
        if d:
            self.src.setText(d)

    def pick_game(self):
        d = QFileDialog.getExistingDirectory(self, "Select Game Folder")
        if d:
            self.game.setText(d)

    def load_mods(self):
        path = self.src.text().strip()
        jf   = os.path.join(path, "mods.json")
        if not os.path.exists(jf):
            self._alert("FILE NOT FOUND", "mods.json not found in the selected folder", err=True)
            return
        with open(jf, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.mods_list.clear()
        for m in data:
            self.mods_list.addItem(QListWidgetItem(f"  {m.get('name', '???')}"))
        n = len(data)
        self.mods_count.setText(f"MODS: {n}  —  LIST LOADED")
        self.mods_count.setMainColor(C_TEXT)
        self._log(f"[INFO] {n} mod(s) loaded from mods.json")

    def check_game(self):
        g   = self.game.text().strip()
        exe = os.path.join(g, "Dead Space.exe")
        if os.path.exists(exe):
            self.exe_status.setText("EXECUTABLE: FOUND  ✓")
            self.exe_status.setMainColor(C_ACCENT)
            self.deploy_btn.setEnabled(True)
            self._set_chip("READY", C_ACCENT)
            self._log("[INFO] Dead Space.exe located — system ready")
        else:
            self.exe_status.setText("EXECUTABLE: NOT FOUND  ✗")
            self.exe_status.setMainColor(C_RED)
            self.deploy_btn.setEnabled(False)
            self._set_chip("OFFLINE", C_PANEL, C_TEXT_DIM)
            self._log("[ERROR] Dead Space.exe not found at specified path")

    def deploy(self):
        self.deploy_btn.setEnabled(False)
        self.restore_btn.setEnabled(False)
        self._update_progress(0)
        self._set_chip("DEPLOYING", C_STEEL)
        self.thread = DeployThread(
            self.src.text().strip(),
            self.game.text().strip(),
        )
        self.thread.log_signal.connect(self._log)
        self.thread.progress_signal.connect(self._update_progress)
        self.thread.done.connect(self._on_done)
        self.thread.start()

    def _on_done(self, ok: bool, msg: str):
        self.deploy_btn.setEnabled(True)
        self.restore_btn.setEnabled(True)
        if ok:
            self._log(f"[INFO] {msg}")
            self._set_chip("COMPLETE", C_GREEN)
            self._alert("OPERATION COMPLETE", msg)
        else:
            self._log(f"[ERROR] {msg}")
            self._set_chip("ERROR", C_RED)
            self._alert("OPERATION FAILED", msg, err=True)

    def restore(self):
        game        = self.game.text().strip()
        backup_root = os.path.join(game, "_ModBackup")
        if not os.path.exists(backup_root):
            self._alert("NO BACKUP", "No backup directory found", err=True)
            return
        folders = [
            os.path.join(backup_root, f)
            for f in os.listdir(backup_root)
        ]
        folders = [f for f in folders if os.path.isdir(f)]
        if not folders:
            self._alert("NO BACKUP", "Backup directory is empty", err=True)
            return
        latest    = max(folders, key=os.path.getmtime)
        game_data = os.path.join(game, "Data")
        restored  = 0
        for r, _, files in os.walk(latest):
            for f in files:
                b   = os.path.join(r, f)
                rel = os.path.relpath(b, latest)
                t   = os.path.join(game_data, rel)
                ensure_dir(os.path.dirname(t))
                shutil.copy2(b, t)
                restored += 1
                self._log(f"[RESTORE] {rel}")
        self._alert("RESTORE COMPLETE", f"{restored} file(s) restored from latest backup")
