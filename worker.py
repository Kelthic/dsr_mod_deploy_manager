"""
worker.py
─────────────────────────────────────────────────
Background deploy thread and file-system helpers.
"""

import os
import shutil
import hashlib
from datetime import datetime

from PyQt6.QtCore import QThread, pyqtSignal


# ─────────────────────────────────────────────────
# FILE HELPERS
# ─────────────────────────────────────────────────

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def clean_empty(root: str, log=None):
    """Remove zero-byte files and empty directories under root."""
    for r, _, files in os.walk(root):
        for f in files:
            fp = os.path.join(r, f)
            try:
                if os.path.getsize(fp) == 0:
                    os.remove(fp)
                    if log:
                        log(f"[CLEAN] {fp}")
            except Exception:
                pass

    for r, dirs, _ in os.walk(root, topdown=False):
        for d in dirs:
            dp = os.path.join(r, d)
            try:
                if not os.listdir(dp):
                    os.rmdir(dp)
                    if log:
                        log(f"[CLEAN] {dp}")
            except Exception:
                pass


# ─────────────────────────────────────────────────
# DEPLOY THREAD
# ─────────────────────────────────────────────────

class DeployThread(QThread):
    log_signal      = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    done            = pyqtSignal(bool, str)

    def __init__(self, src: str, game: str):
        super().__init__()
        self.src  = src
        self.game = game

    def log(self, t: str):
        self.log_signal.emit(t)

    def run(self):
        try:
            self.execute()
        except Exception as e:
            self.done.emit(False, str(e))

    def execute(self):
        game_data = os.path.join(self.game, "Data")

        if not os.path.exists(game_data):
            self.done.emit(False, "Game Data folder not found")
            return

        self.log("[INFO] Scanning source for empty files...")
        clean_empty(self.src, self.log)

        files = []
        for r, _, fs in os.walk(self.src):
            for f in fs:
                full = os.path.join(r, f)
                rel  = os.path.relpath(full, self.src)
                files.append((full, rel))

        if not files:
            self.done.emit(False, "No files found in source folder")
            return

        backup_root = os.path.join(
            self.game, "_ModBackup",
            datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
        )

        self.log("[INFO] Starting deployment...")
        total    = len(files)
        deployed = skipped = backuped = 0

        for i, (src_f, rel) in enumerate(files):
            dst_f = os.path.join(game_data, rel)
            ensure_dir(os.path.dirname(dst_f))
            should_copy = True

            if os.path.exists(dst_f):
                try:
                    if sha256_file(src_f) == sha256_file(dst_f):
                        should_copy = False
                        skipped += 1
                        self.log(f"[SKIP] {rel}")
                except Exception:
                    pass

                if should_copy:
                    backup_f = os.path.join(backup_root, rel)
                    if not os.path.exists(backup_f):
                        ensure_dir(os.path.dirname(backup_f))
                        shutil.copy2(dst_f, backup_f)
                        backuped += 1
                        self.log(f"[BACKUP] {rel}")

            if should_copy:
                shutil.copy2(src_f, dst_f)
                deployed += 1
                self.log(f"[DEPLOY] {rel}")

            self.progress_signal.emit(int((i + 1) / total * 100))

        self.done.emit(
            True,
            f"Deploy complete — {deployed} transferred, {skipped} skipped, {backuped} backed up",
        )
