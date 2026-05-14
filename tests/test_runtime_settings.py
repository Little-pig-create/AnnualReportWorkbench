import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from webview_console.error_codes import RUN_ALREADY_ACTIVE
from webview_console.infra.config_store import ConfigStore
from webview_console.infra.event_pusher import EventPusher
from webview_console.models import RunState
from webview_console.runtime import Runtime


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

    def test_extract_run_ignores_visualization_seed_for_stage_progress(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_path = root / "config" / "settings.json"
            runtime = Runtime(ConfigStore(config_path), EventPusher())
            runtime.visualization_index_service.build_snapshot = lambda settings: {
                "links": {
                    "yearTotal": 1,
                    "yearBuckets": [{"year": 2024, "status": "completed", "count": 1, "active": False}],
                    "totalAnnouncements": 1,
                },
                "pdf": {
                    "yearBuckets": [{"year": 2024, "total": 2, "completed": 2, "active": False}],
                    "total": 2,
                    "completed": 2,
                },
                "extract": {
                    "yearBuckets": [{"year": 2024, "total": 2, "completed": 2, "active": False}],
                    "total": 2,
                    "completed": 2,
                },
                "meta": {},
            }

            with patch("webview_console.runtime.ExecutionWorker.start", autospec=True, return_value=None):
                result = runtime.create_run({"mode": "extract"})

            self.assertTrue(result["ok"])
            run_id = result["data"]["runId"]
            stages = runtime.get_run_stages(run_id)
            self.assertTrue(stages["ok"])
            stage_items = {item["name"]: item for item in stages["data"]["items"]}
            self.assertEqual(stage_items["links"]["status"], "pending")
            self.assertEqual(stage_items["links"]["progress"]["percent"], 0)
            self.assertEqual(stage_items["pdf"]["status"], "pending")
            self.assertEqual(stage_items["pdf"]["progress"]["percent"], 0)
            self.assertEqual(stage_items["extract"]["status"], "pending")
            self.assertEqual(stage_items["extract"]["progress"]["percent"], 0)

    def test_links_run_ignores_visualization_seed_for_stage_progress(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_path = root / "config" / "settings.json"
            runtime = Runtime(ConfigStore(config_path), EventPusher())
            runtime.visualization_index_service.build_snapshot = lambda settings: {
                "links": {
                    "yearTotal": 2,
                    "yearBuckets": [
                        {"year": 2023, "status": "completed", "count": 1, "active": False},
                        {"year": 2024, "status": "completed", "count": 1, "active": False},
                    ],
                    "totalAnnouncements": 2,
                },
                "pdf": {
                    "yearBuckets": [{"year": 2024, "total": 5, "completed": 4, "active": False}],
                    "total": 5,
                    "completed": 4,
                },
                "extract": {
                    "yearBuckets": [{"year": 2024, "total": 5, "completed": 3, "active": False}],
                    "total": 5,
                    "completed": 3,
                },
                "meta": {},
            }

            with patch("webview_console.runtime.ExecutionWorker.start", autospec=True, return_value=None):
                result = runtime.create_run({"mode": "links"})

            self.assertTrue(result["ok"])
            run_id = result["data"]["runId"]
            stages = runtime.get_run_stages(run_id)
            self.assertTrue(stages["ok"])
            stage_items = {item["name"]: item for item in stages["data"]["items"]}
            self.assertEqual(stage_items["links"]["status"], "pending")
            self.assertEqual(stage_items["links"]["progress"]["percent"], 0)
            self.assertEqual(stage_items["pdf"]["status"], "pending")
            self.assertEqual(stage_items["pdf"]["progress"]["percent"], 0)
            self.assertEqual(stage_items["extract"]["status"], "pending")
            self.assertEqual(stage_items["extract"]["progress"]["percent"], 0)

    def test_pdf_run_ignores_visualization_seed_for_stage_progress(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_path = root / "config" / "settings.json"
            runtime = Runtime(ConfigStore(config_path), EventPusher())
            runtime.visualization_index_service.build_snapshot = lambda settings: {
                "links": {
                    "yearTotal": 1,
                    "yearBuckets": [{"year": 2024, "status": "completed", "count": 1, "active": False}],
                    "totalAnnouncements": 1,
                },
                "pdf": {
                    "yearBuckets": [{"year": 2024, "total": 5, "completed": 5, "active": False}],
                    "total": 5,
                    "completed": 5,
                },
                "extract": {
                    "yearBuckets": [{"year": 2024, "total": 5, "completed": 2, "active": False}],
                    "total": 5,
                    "completed": 2,
                },
                "meta": {},
            }

            with patch("webview_console.runtime.ExecutionWorker.start", autospec=True, return_value=None):
                result = runtime.create_run({"mode": "pdf"})

            self.assertTrue(result["ok"])
            run_id = result["data"]["runId"]
            stages = runtime.get_run_stages(run_id)
            self.assertTrue(stages["ok"])
            stage_items = {item["name"]: item for item in stages["data"]["items"]}
            self.assertEqual(stage_items["links"]["status"], "pending")
            self.assertEqual(stage_items["links"]["progress"]["percent"], 0)
            self.assertEqual(stage_items["pdf"]["status"], "pending")
            self.assertEqual(stage_items["pdf"]["progress"]["percent"], 0)
            self.assertEqual(stage_items["extract"]["status"], "pending")
            self.assertEqual(stage_items["extract"]["progress"]["percent"], 0)

    def test_confirm_close_clears_current_stage(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_path = root / "config" / "settings.json"
            runtime = Runtime(ConfigStore(config_path), EventPusher())
            run_state = RunState.create(
                "run_close",
                "pipeline",
                "2026-05-14T00:00:00+08:00",
                outputs={"projectRoot": str(root)},
            )
            run_state.status = "running"
            run_state.current_stage = "pdf"
            run_state.stages["pdf"].status = "running"
            runtime._runs[run_state.run_id] = run_state
            runtime._active_run_id = run_state.run_id

            runtime._finalize_active_run_for_window_close()

            self.assertEqual(run_state.status, "cancelled")
            self.assertIsNone(run_state.current_stage)
            self.assertEqual(run_state.stages["pdf"].status, "cancelled")


if __name__ == "__main__":
    unittest.main()
