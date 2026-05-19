import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from webview_console import launcher


class LauncherTests(unittest.TestCase):
    def test_resolve_frontend_entry_auto_prefers_built_frontend(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            dist_dir = Path(temp_dir)
            index_path = dist_dir / "index.html"
            index_path.write_text("<!doctype html>", encoding="utf-8")

            with patch.dict(os.environ, {"ARW_WEBUI_SOURCE": "auto"}, clear=False):
                with patch("webview_console.launcher.frontend_dist_dir", return_value=dist_dir):
                    with patch("webview_console.launcher._url_is_alive", return_value=True):
                        self.assertEqual(launcher.resolve_frontend_entry(), index_path.as_uri())

    def test_resolve_frontend_entry_dev_requires_live_server(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            dist_dir = Path(temp_dir)
            index_path = dist_dir / "index.html"
            index_path.write_text("<!doctype html>", encoding="utf-8")

            with patch.dict(os.environ, {"ARW_WEBUI_SOURCE": "dev"}, clear=False):
                with patch("webview_console.launcher.frontend_dist_dir", return_value=dist_dir):
                    with patch("webview_console.launcher._url_is_alive", return_value=False):
                        with self.assertRaises(FileNotFoundError):
                            launcher.resolve_frontend_entry()

    def test_resolve_window_spec_uses_small_work_area_as_min_size(self) -> None:
        with patch("webview_console.launcher._read_windows_work_area", return_value=(1024, 768)):
            spec = launcher.resolve_window_spec()

        self.assertEqual(spec.width, 1024)
        self.assertEqual(spec.height, 768)
        self.assertEqual(spec.min_size, (1024, 768))
        self.assertTrue(spec.maximized)

if __name__ == "__main__":
    unittest.main()
