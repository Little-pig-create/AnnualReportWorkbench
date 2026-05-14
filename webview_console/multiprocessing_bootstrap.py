from __future__ import annotations

import multiprocessing
import sys
from pathlib import Path


def configure_multiprocessing() -> None:
    multiprocessing.freeze_support()
    _configure_windows_subprocess_executable()


def _configure_windows_subprocess_executable() -> None:
    if sys.platform != "win32":
        return
    if getattr(sys, "frozen", False):
        return

    executable = Path(sys.executable)
    if executable.name.lower() != "python.exe":
        return

    pythonw_path = executable.with_name("pythonw.exe")
    if pythonw_path.exists():
        multiprocessing.set_executable(str(pythonw_path))
