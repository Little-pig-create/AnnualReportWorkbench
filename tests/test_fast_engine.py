import asyncio
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from webview_console.fast_engine import run_extraction_fast
from webview_console.text_engine import ExtractTextConfig


def _fake_extract_worker(pdf_path: Path, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("ok", encoding="utf-8")
    return pdf_path, output_path, True, "", 1, 2


class RunExtractionFastTests(unittest.TestCase):
    def _make_config(self, root: Path, *, concurrency: int = 8) -> ExtractTextConfig:
        input_dir = root / "annual_reports"
        output_dir = root / "txt_extract"
        state_dir = root / "state"
        return ExtractTextConfig(
            input_dir=input_dir,
            output_dir=output_dir,
            state_dir=state_dir,
            start_year=2024,
            end_year=2024,
            concurrency=concurrency,
        )

    def test_skips_process_pool_when_all_outputs_already_exist(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_dir = root / "annual_reports" / "2024"
            output_dir = root / "txt_extract" / "2024"
            input_dir.mkdir(parents=True, exist_ok=True)
            output_dir.mkdir(parents=True, exist_ok=True)
            (input_dir / "sample.pdf").write_bytes(b"%PDF-1.4 exists")
            (output_dir / "sample.txt").write_text("cached", encoding="utf-8")

            config = self._make_config(root)

            with patch("webview_console.fast_engine.ProcessPoolExecutor", side_effect=AssertionError("should not create process pool")):
                result = asyncio.run(run_extraction_fast(config))

            self.assertEqual(result.pending_total, 0)
            self.assertEqual(result.stats["exists"], 1)
            self.assertEqual(result.stats["extracted"], 0)

    def test_uses_thread_backend_for_tiny_extract_batches(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            year_dir = root / "annual_reports" / "2024"
            year_dir.mkdir(parents=True, exist_ok=True)
            for name in ("a.pdf", "b.pdf"):
                (year_dir / name).write_bytes(b"%PDF-1.4 tiny")

            config = self._make_config(root, concurrency=8)

            with (
                patch("webview_console.fast_engine.ProcessPoolExecutor", side_effect=AssertionError("should not create process pool")),
                patch("webview_console.fast_engine._run_extract_worker", side_effect=_fake_extract_worker),
            ):
                result = asyncio.run(run_extraction_fast(config))

            self.assertEqual(result.pending_total, 2)
            self.assertEqual(result.stats["extracted"], 2)
            self.assertTrue((root / "txt_extract" / "2024" / "a.txt").exists())
            self.assertTrue((root / "txt_extract" / "2024" / "b.txt").exists())

    def test_process_worker_count_is_capped_by_pending_work(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            year_dir = root / "annual_reports" / "2024"
            year_dir.mkdir(parents=True, exist_ok=True)
            for name in ("a.pdf", "b.pdf", "c.pdf"):
                (year_dir / name).write_bytes(b"%PDF-1.4 batch")

            config = self._make_config(root, concurrency=8)
            recorded: dict[str, int] = {}

            class SpyExecutor(ThreadPoolExecutor):
                def __init__(self, max_workers: int):
                    recorded["max_workers"] = max_workers
                    super().__init__(max_workers=max_workers)

            with (
                patch("webview_console.fast_engine.ProcessPoolExecutor", SpyExecutor),
                patch("webview_console.fast_engine._run_extract_worker", side_effect=_fake_extract_worker),
                patch("webview_console.fast_engine.os.cpu_count", return_value=8),
            ):
                result = asyncio.run(run_extraction_fast(config))

            self.assertEqual(recorded["max_workers"], 3)
            self.assertEqual(result.stats["extracted"], 3)


if __name__ == "__main__":
    unittest.main()
