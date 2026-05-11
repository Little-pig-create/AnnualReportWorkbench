import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from webview_console.infra.config_store import ConfigStore
from webview_console.infra.event_pusher import EventPusher
from webview_console.runtime import Runtime
from webview_console.error_codes import RUN_ALREADY_ACTIVE


class RuntimeSettingsTests(unittest.TestCase):
    def test_update_settings_creates_workspace_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_path = root / "config" / "settings.json"
            runtime = Runtime(ConfigStore(config_path), EventPusher())

            payload = {
                "workspace": {
                    "projectRoot": str(root / "report_spider"),
                    "annualReportDir": "annual_reports",
                    "textOutputDir": "txt_extract",
                    "stateDir": ".",
                    "startYear": 2020,
                    "endYear": 2024,
                },
                "links": {
                    "seDate": "",
                    "pageSize": 30,
                    "requestInterval": 0.2,
                    "announcementConcurrency": 2,
                    "marketScopes": ["a_share"],
                    "resetCheckpoint": False,
                    "deleteCheckpointOnSuccess": False,
                },
                "pdf": {
                    "downloadConcurrency": 2,
                },
                "extract": {
                    "concurrency": 8,
                    "resetCheckpoint": False,
                    "deleteCheckpointOnSuccess": False,
                },
            }

            result = runtime.update_settings(payload)

            self.assertTrue(result["ok"])
            project_root = Path(payload["workspace"]["projectRoot"])
            self.assertTrue(project_root.exists())
            self.assertTrue((project_root / "annual_reports").exists())
            self.assertTrue((project_root / "txt_extract").exists())

    def test_update_settings_does_not_create_workspace_dirs_when_run_is_active(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_path = root / "config" / "settings.json"
            runtime = Runtime(ConfigStore(config_path), EventPusher())
            runtime._active_run_id = "run_active"

            project_root = root / "report_spider"
            payload = {
                "workspace": {
                    "projectRoot": str(project_root),
                    "annualReportDir": "annual_reports",
                    "textOutputDir": "txt_extract",
                    "stateDir": ".",
                    "startYear": 2020,
                    "endYear": 2024,
                },
                "links": {
                    "seDate": "",
                    "pageSize": 30,
                    "requestInterval": 0.2,
                    "announcementConcurrency": 2,
                    "marketScopes": ["a_share"],
                    "resetCheckpoint": False,
                    "deleteCheckpointOnSuccess": False,
                },
                "pdf": {
                    "downloadConcurrency": 2,
                },
                "extract": {
                    "concurrency": 8,
                    "resetCheckpoint": False,
                    "deleteCheckpointOnSuccess": False,
                },
            }

            result = runtime.update_settings(payload)

            self.assertFalse(result["ok"])
            self.assertEqual(result["error"]["code"], RUN_ALREADY_ACTIVE)
            self.assertFalse(project_root.exists())
            self.assertFalse(config_path.exists())


if __name__ == "__main__":
    unittest.main()
