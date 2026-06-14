import json
import tempfile
import unittest
from pathlib import Path

from maintainer_compass.report import render
from maintainer_compass.scanner import scan_repository


class ReportTests(unittest.TestCase):
    def test_json_report_includes_categories_and_findings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            (tmp_path / "README.md").write_text("# Demo", encoding="utf-8")

            payload = json.loads(render(scan_repository(tmp_path), "json"))

            self.assertEqual(payload["path"], str(tmp_path.resolve()))
            self.assertIn("categories", payload)
            self.assertTrue(any(finding["id"] == "readme" for finding in payload["findings"]))

    def test_markdown_report_marks_missing_checks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            (tmp_path / "README.md").write_text("# Demo", encoding="utf-8")

            report = render(scan_repository(tmp_path), "markdown")

            self.assertIn("# Maintainer Compass Report:", report)
            self.assertIn("**needs attention:** Security policy is present", report)

    def test_json_report_can_include_only_failures(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            (tmp_path / "README.md").write_text("# Demo", encoding="utf-8")

            payload = json.loads(render(scan_repository(tmp_path), "json", only_failures=True))

            self.assertTrue(payload["only_failures"])
            self.assertTrue(payload["findings"])
            self.assertTrue(all(not finding["passed"] for finding in payload["findings"]))


if __name__ == "__main__":
    unittest.main()
