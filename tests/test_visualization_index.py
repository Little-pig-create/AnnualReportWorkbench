import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from webview_console.infra.visualization_index import FILTERED_FILENAME, VisualizationIndexService
from webview_console.settings import AppSettings, ExtractSettings, LinksSettings, PdfSettings, WorkspaceSettings


class VisualizationIndexServiceTests(unittest.TestCase):
    def test_rebuilds_cached_snapshot_when_workspace_dirs_change(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project_root = root / "project"
            state_dir = project_root / "state"
            source_a = project_root / "annual_a"
            source_b = project_root / "annual_b"
            text_output = project_root / "txt"

            for path in (state_dir, source_a, source_b, text_output):
                path.mkdir(parents=True, exist_ok=True)

            self._write_year_rows(source_a, 2024, 1)
            self._write_year_rows(source_b, 2024, 3)

            service = VisualizationIndexService()
            base_kwargs = {
                "projectRoot": str(project_root),
                "textOutputDir": "txt",
                "stateDir": "state",
                "startYear": 2024,
                "endYear": 2024,
            }

            snapshot_a = service.build_snapshot(self._build_settings(annualReportDir="annual_a", **base_kwargs))
            self.assertEqual(snapshot_a["links"]["totalAnnouncements"], 1)

            snapshot_b = service.build_snapshot(self._build_settings(annualReportDir="annual_b", **base_kwargs))
            self.assertEqual(snapshot_b["links"]["totalAnnouncements"], 3)

    def test_pdf_snapshot_excludes_replaced_pdfs_but_keeps_legacy_pdf_dir(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project_root = root / "project"
            annual_root = project_root / "annual"
            text_root = project_root / "txt"
            state_root = project_root / "state"

            (annual_root / "2024").mkdir(parents=True, exist_ok=True)
            (annual_root / "2024" / "pdf").mkdir(parents=True, exist_ok=True)
            (annual_root / "2024" / "replaced_pdfs").mkdir(parents=True, exist_ok=True)
            text_root.mkdir(parents=True, exist_ok=True)
            state_root.mkdir(parents=True, exist_ok=True)

            (annual_root / "2024" / "current.pdf").write_bytes(b"%PDF-1.4 current")
            (annual_root / "2024" / "pdf" / "legacy.pdf").write_bytes(b"%PDF-1.4 legacy")
            (annual_root / "2024" / "replaced_pdfs" / "old.pdf").write_bytes(b"%PDF-1.4 old")

            service = VisualizationIndexService()
            snapshot = service.build_snapshot(
                self._build_settings(
                    projectRoot=str(project_root),
                    annualReportDir="annual",
                    textOutputDir="txt",
                    stateDir="state",
                    startYear=2024,
                    endYear=2024,
                )
            )

            self.assertEqual(snapshot["pdf"]["total"], 2)
            self.assertEqual(snapshot["pdf"]["completed"], 2)
            self.assertEqual(snapshot["pdf"]["oldAnnualReportTotal"], 1)
            self.assertEqual(snapshot["pdf"]["oldAnnualReportCompleted"], 1)
            self.assertEqual(snapshot["pdf"]["yearBuckets"][0]["replacedTotal"], 1)

    def _build_settings(self, **workspace_kwargs) -> AppSettings:
        return AppSettings(
            workspace=WorkspaceSettings(**workspace_kwargs),
            links=LinksSettings(),
            pdf=PdfSettings(),
            extract=ExtractSettings(),
        )

    def _write_year_rows(self, annual_root: Path, year: int, count: int) -> None:
        target = annual_root / str(year)
        target.mkdir(parents=True, exist_ok=True)
        lines = ['{"row": %d}' % index for index in range(count)]
        (target / FILTERED_FILENAME).write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
