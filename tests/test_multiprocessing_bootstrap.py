import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from webview_console.multiprocessing_bootstrap import configure_multiprocessing


class MultiprocessingBootstrapTests(unittest.TestCase):
    def test_uses_pythonw_for_windows_source_launch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            python_exe = root / "python.exe"
            pythonw_exe = root / "pythonw.exe"
            python_exe.write_bytes(b"")
            pythonw_exe.write_bytes(b"")

            with (
                patch("webview_console.multiprocessing_bootstrap.sys.platform", "win32"),
                patch("webview_console.multiprocessing_bootstrap.sys.executable", str(python_exe)),
                patch("webview_console.multiprocessing_bootstrap.multiprocessing.freeze_support") as freeze_support,
                patch("webview_console.multiprocessing_bootstrap.multiprocessing.set_executable") as set_executable,
            ):
                configure_multiprocessing()

            freeze_support.assert_called_once_with()
            set_executable.assert_called_once_with(str(pythonw_exe))

    def test_skips_pythonw_override_for_frozen_windows_build(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            app_exe = root / "AnnualReportWorkbench.exe"
            app_exe.write_bytes(b"")

            with (
                patch("webview_console.multiprocessing_bootstrap.sys.platform", "win32"),
                patch("webview_console.multiprocessing_bootstrap.sys.executable", str(app_exe)),
                patch("webview_console.multiprocessing_bootstrap.sys.frozen", True, create=True),
                patch("webview_console.multiprocessing_bootstrap.multiprocessing.freeze_support") as freeze_support,
                patch("webview_console.multiprocessing_bootstrap.multiprocessing.set_executable") as set_executable,
            ):
                configure_multiprocessing()

            freeze_support.assert_called_once_with()
            set_executable.assert_not_called()


if __name__ == "__main__":
    unittest.main()
